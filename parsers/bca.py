import pdfplumber
import pandas as pd
import re
from datetime import datetime
from pathlib import Path
from parsers.base import BaseBankParser
from utils.cleaner import clean_description, extract_generic_note, categorize_transaction

class BCAParser(BaseBankParser):
    """BCA Bank E-Statement Parser (PDF format)"""
    
    def parse(self, filepath: str) -> pd.DataFrame:
        transactions = []
        year = datetime.now().year
        
        with pdfplumber.open(filepath) as pdf:
            # Try to get period from first page
            first_page_text = pdf.pages[0].extract_text() if pdf.pages else ""
            period_match = re.search(r'PERIODE\s*:\s*\w+\s+(\d{4})', first_page_text)
            if period_match:
                year = int(period_match.group(1))
            else:
                filename = Path(filepath).stem
                year_match = re.search(r'(\d{4})', filename)
                if year_match:
                    year = int(year_match.group(1))

            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                
                lines = text.split('\n')
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if not line:
                        i += 1
                        continue
                        
                    # Match date format DD/MM
                    date_match = re.match(r'^(\d{2}/\d{2})\s+(.+)', line)
                    if date_match:
                        date_str = date_match.group(1)
                        rest = date_match.group(2)
                        
                        day, mon = map(int, date_str.split('/'))
                        tx_date = datetime(year, mon, day)
                        
                        tx_lines = [rest]
                        i += 1
                        
                        # Collect continuation lines
                        while i < len(lines):
                            next_line = lines[i].strip()
                            if re.match(r'^\d{2}/\d{2}\s+', next_line): break
                            if any(skip in next_line for skip in ['HALAMAN', 'PERIODE', 'SALDO AWAL']):
                                i += 1
                                continue
                            if next_line:
                                tx_lines.append(next_line)
                            i += 1
                        
                        full_tx_text = ' '.join(tx_lines)
                        if 'SALDO AWAL' in full_tx_text: continue
                        
                        amount = 0
                        tx_type = "Expense"
                        
                        # Find amount and DB marker
                        amount_matches = re.findall(r'([\d,]+\.\d{2})\s*(DB)?', full_tx_text)
                        if amount_matches:
                            for amt_str, is_db in amount_matches:
                                amt = float(amt_str.replace(',', ''))
                                if amt > 0:
                                    amount = amt
                                    tx_type = "Expense" if is_db else "Income"
                                    break
                        
                        if amount > 0:
                            description = clean_description(full_tx_text)
                            note = extract_generic_note(full_tx_text)
                            category = categorize_transaction(full_tx_text, tx_type)
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
                    else:
                        i += 1
        
        return pd.DataFrame(transactions)
