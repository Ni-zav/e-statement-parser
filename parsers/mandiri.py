import pandas as pd
import re
from datetime import datetime
from pathlib import Path
from parsers.base import BaseBankParser
from utils.cleaner import clean_description, extract_generic_note, categorize_transaction

class MandiriParser(BaseBankParser):
    """Mandiri Bank E-Statement Parser (XLSX format)"""
    
    def parse(self, filepath: str) -> pd.DataFrame:
        filepath = Path(filepath)
        
        # Mandiri Excel files might be password protected
        password = None
        password_file = filepath.parent / "password.txt"
        if password_file.exists():
            with open(password_file, 'r', encoding='utf-8') as f:
                password = f.readline().strip()

        if password:
            import io
            import msoffcrypto
            try:
                with open(filepath, 'rb') as encrypted_file:
                    office_file = msoffcrypto.OfficeFile(encrypted_file)
                    office_file.load_key(password=password)
                    decrypted = io.BytesIO()
                    office_file.decrypt(decrypted)
                    decrypted.seek(0)
                    df = pd.read_excel(decrypted, sheet_name=0, header=None)
            except Exception as e:
                print(f"Error decrypting {filepath.name}: {e}")
                df = pd.read_excel(filepath, sheet_name=0, header=None)
        else:
            df = pd.read_excel(filepath, sheet_name=0, header=None)

        transactions = []
        header_row = None
        for i, row in df.iterrows():
            if row.astype(str).str.contains('Tanggal', case=False, na=False).any():
                if row.astype(str).str.contains('No', case=False, na=False).any():
                    header_row = i
                    break
        
        if header_row is None:
            return self.create_empty_df()

        data_start = header_row + 2
        i = data_start
        while i < len(df):
            row = df.iloc[i]
            try:
                tx_num = row[0]
                if pd.isna(tx_num) or not str(tx_num).strip().isdigit():
                    i += 1
                    continue
            except:
                i += 1
                continue

            date_val = row[4]
            if pd.isna(date_val):
                i += 1
                continue

            # Parse date
            tx_date = date_val if isinstance(date_val, datetime) else pd.to_datetime(date_val)
            
            # Get time from next row
            if i + 1 < len(df):
                time_row = df.iloc[i + 1]
                time_val = time_row[4]
                if pd.notna(time_val) and 'WIB' in str(time_val):
                    time_str = str(time_val).replace(' WIB', '')
                    try:
                        time_parts = time_str.split(':')
                        tx_date = tx_date.replace(
                            hour=int(time_parts[0]),
                            minute=int(time_parts[1]),
                            second=int(time_parts[2]) if len(time_parts) > 2 else 0
                        )
                    except: pass

            remarks_raw = str(row[7]) if pd.notna(row[7]) else ""
            description = clean_description(remarks_raw)
            
            incoming = row[15] # Dana Masuk (Credit/Income)
            outgoing = row[18] # Dana Keluar (Debit/Expense)
            
            amount = 0
            tx_type = "Expense"
            
            if pd.notna(outgoing):
                amount_str = str(outgoing).strip().replace('.', '').replace(',', '.')
                try:
                    amount = float(amount_str)
                    tx_type = "Expense"
                except: pass
            
            if pd.notna(incoming):
                amount_str = str(incoming).strip().replace('.', '').replace(',', '.')
                try:
                    amount = float(amount_str)
                    tx_type = "Income"
                except: pass

            if amount > 0:
                note = extract_generic_note(remarks_raw)
                category = categorize_transaction(remarks_raw, tx_type)
                transactions.append({
                    'Date': tx_date.strftime('%m/%d/%Y %H:%M:%S'),
                    'Account': self.account_name,
                    'Category': category,
                    'Note': note,
                    'Amount': int(amount),
                    'Type': tx_type,
                    'Description': description,
                    'Currency': 'IDR'
                })
            i += 2
            
        return pd.DataFrame(transactions)
