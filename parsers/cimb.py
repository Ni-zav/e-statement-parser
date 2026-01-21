import pdfplumber
import pandas as pd
import re
from datetime import datetime
from pathlib import Path
from parsers.base import BaseBankParser
from utils.cleaner import clean_description, extract_generic_note, categorize_transaction

class CIMBParser(BaseBankParser):
    """CIMB Bank E-Statement Parser (PDF format)"""
    
    def parse(self, filepath: str) -> pd.DataFrame:
        transactions = []
        
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text: continue
                
                lines = text.split('\n')
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    # Match CIMB date format: DD Mon YYYY
                    date_match = re.match(r'^(\d{2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', line)
                    if date_match:
                        day = int(date_match.group(1))
                        mon_str = date_match.group(2)
                        year = int(date_match.group(3))
                        
                        mon_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                                   'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
                        tx_date = datetime(year, mon_map[mon_str], day)
                        
                        tx_type_line = line[len(date_match.group(0)):].strip()
                        tx_lines = []
                        i += 1
                        
                        # Check for time
                        if i < len(lines):
                            time_match = re.match(r'^(\d{2}:\d{2}:\d{2})', lines[i].strip())
                            if time_match:
                                h, m, s = map(int, time_match.group(1).split(':'))
                                tx_date = tx_date.replace(hour=h, minute=m, second=s)
                                rest = lines[i].strip()[len(time_match.group(0)):].strip()
                                if rest: tx_lines.append(rest)
                                i += 1
                        
                        # Collect continuation lines
                        while i < len(lines):
                            next_line = lines[i].strip()
                            if re.match(r'^\d{2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', next_line): break
                            if any(skip in next_line for skip in ['Page', 'Laporan Rekening', 'Saldo Awal']):
                                i += 1
                                continue
                            if next_line: tx_lines.append(next_line)
                            i += 1
                        
                        # Amount parsing (CIMB uses negative for debit)
                        amount = 0
                        tx_type = "Expense"
                        debit_match = re.search(r'-(\d{1,3}(?:,\d{3})*(?:\.\d{2}))', tx_type_line)
                        credit_match = re.search(r'(?<!-)(\d{1,3}(?:,\d{3})*\.\d{2})', tx_type_line)
                        
                        if debit_match:
                            amount = float(debit_match.group(1).replace(',', ''))
                            tx_type = "Expense"
                        elif credit_match:
                            amount = float(credit_match.group(1).replace(',', ''))
                            tx_type = "Income" if 'FROM' in tx_type_line.upper() or 'CR' in tx_type_line.upper() else "Expense"

                        if amount > 0:
                            description = clean_description(' '.join(tx_lines))
                            note = extract_generic_note(description)
                            category = categorize_transaction(description, tx_type)
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
