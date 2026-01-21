import re

def clean_description(description: str) -> str:
    """Flatten and clean transaction description."""
    if not description:
        return ""
    # Replace literal \n and actual newlines with space
    desc = description.replace('\\n', ' ').replace('\n', ' ').strip()
    # Replace multiple spaces with single space
    desc = re.sub(r'\s+', ' ', desc)
    return desc

def extract_generic_note(description: str) -> str:
    """
    Extract a clean note from a description without external rules.
    Recognizes common keywords for income/expense/transfer.
    """
    desc_upper = description.upper()
    
    # Common Indonesian bank keywords
    if 'BIAYA ADM' in desc_upper or 'BIAYA TRANSFER' in desc_upper:
        return "Fees"
    if 'PENARIKAN TUNAI' in desc_upper or 'TARIKAN ATM' in desc_upper:
        return "ATM Withdrawal"
    if 'PEMBAYARAN QR' in desc_upper or 'QR PURCHASE' in desc_upper:
        # Try to find merchant after QR keyword
        match = re.search(r'(?:KE|US)\s+([A-Z\s]+)', desc_upper)
        if match:
            return match.group(1).strip()
        return "QR Payment"
    
    # Try to find names (capitalized words) that are not common bank terms
    # This is a fallback to keep the note short
    words = description.split()
    meaningful_words = [w for w in words if len(w) > 2 and w.upper() not in ['TRANSFER', 'TRSF', 'BI-FAST', 'BANK', 'SA', 'OFF', 'WIB']]
    
    if meaningful_words:
        return ' '.join(meaningful_words[:5])
        
def categorize_transaction(description: str, tx_type: str) -> str:
    """
    Categorize transaction based on common keywords for general usage.
    """
    desc = description.upper()
    
    # Fees & Charges
    if any(w in desc for w in ['BIAYA ADM', 'BIAYA TRANSFER', 'ADMIN FEE', 'SERVICE FEE', 'CHARGE', 'ADMINISTRASI']):
        return "Fees & Charges"

    # Food & Beverage
    if any(w in desc for w in ['GOFOOD', 'GRABFOOD', 'SHOPEEFOOD', 'RESTAURANT', 'CAFE', 'KOPI', 'BAKERY', 'FOOD', 'DINING', 'MCD', 'COUVEE', 'SOTO', 'MIE', 'AYAM', 'CHICKEN', 'COFFEE', 'BAKERY', 'CAKE', 'DESSERT', 'MAKO', 'ESTUARY', 'XOPI', 'SAMBEL', 'YOSHINOYA', 'CHATIME', 'QPON']):
        return "Food & Beverage"

    # Transport & Travel
    if any(w in desc for w in ['GOJEK', 'GRAB', 'PERTAMINA', 'SHELL', 'TOLL', 'PARKIR', 'TIKET', 'TRAVELOKA', 'KAI', 'FLIGHT', 'TAXI', 'JOPARK']):
        return "Transport & Travel"

    # Shopping & Groceries
    if any(w in desc for w in ['TOKOPEDIA', 'SHOPEE', 'LAZADA', 'ALFAMART', 'INDOMARET', 'SUPERMARKET', 'HYPERMART', 'MALL', 'FASHION', 'CLOTHING', 'MARKET', 'IDM', 'ALFA', 'UNIQLO', 'TRANSMART', 'MDS']):
        return "Shopping & Groceries"

    # Utilities & Bills
    if any(w in desc for w in ['PLN', 'PAM', 'TELKOM', 'INTERNET', 'PULSA', 'BPJS', 'PBB', 'SUBSCRIPTION', 'BILL', 'SMARTFREN', 'TELKOMSEL', 'XL', 'INDOSAT']):
        return "Utilities & Bills"

    # Entertainment
    if any(w in desc for w in ['NETFLIX', 'SPOTIFY', 'DISNEY', 'CINEMA', 'CGV', 'XXI', 'GAME', 'STEAM', 'PLAYSTATION', 'STARCADE']):
        return "Entertainment"
        
    # Health & Personal Care
    if any(w in desc for w in ['APOTEK', 'PHARMACY', 'HOSPITAL', 'CLINIC', 'DOKTER', 'DOCTOR', 'SALON', 'BARBERSHOP', 'WATSONS', 'GUARDIAN']):
        return "Health & Personal Care"

    # Income Handling
    if tx_type == "Income":
        if any(w in desc for w in ['SALARY', 'GAJI', 'BONUS', 'PAYROLL', 'REWARD']):
            return "Income: Salary & Bonus"
        if any(w in desc for w in ['BUNGA', 'INTEREST', 'EARNING']):
            return "Income: Wealth"
        return "Income: Other"

    # Transfers
    if any(w in desc for w in ['TRANSFER', 'TRSF', 'BI-FAST', 'OVERBOOKING', 'TOPUP', 'TOP-UP', 'E-WALLET', 'OVO', 'GOPAY', 'DANA', 'SHOPEEPAY']):
        return "Transfer & Topup"

    # ATM Withdrawal
    if 'ATM' in desc or 'PENARIKAN TUNAI' in desc or 'TARIKAN' in desc:
        return "Cash Withdrawal"

    return "Other"
