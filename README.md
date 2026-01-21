# Bank Statement Parser (Standalone)

A unified tool to parse bank statements from BCA, Mandiri, and CIMB into a standardized CSV format. (Mainly for being used in Money Manager App)

## Features
### Supported Banks
- [x] **BCA**: PDF e-statements.
- [x] **Mandiri**: XLSX e-statements (supports password-protected files).
- [x] **CIMB**: PDF e-statements.
- [ ] **BNI**: (Planned)
- [ ] **BRI**: (Planned)

### Core Capabilities
- **Built-in General Categorization**: Automatically groups transactions into common categories (Food & Beverage, Shopping, Transport, etc.) using Indonesian merchant keywords.
- **Rule-Agnostic**: Automatically cleans and extracts notes from transaction descriptions without external configuration.
- **Standalone**: No external database or complex rules engine required.

## Requirements
- **Python 3.11+** (Recommended for best dependency compatibility)
- Dependencies listed in `requirements.txt` (`pandas`, `pdfplumber`, `msoffcrypto-tool`, `openpyxl`)

## Installation
1. Create and activate a virtual environment:
   ```powershell
   # Recommended using Python 3.11
   py -3.11 -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage
Run the script using the CLI:
```powershell
python main.py --bank <bca|mandiri|cimb> --input <path_to_statement> --output <output_path.csv> --account <account_name>
```

### Examples
- **BCA**:
  ```powershell
  python main.py --bank bca --input statements/bca_jan_2025.pdf --output bca.csv --account my-bca
  ```
- **Mandiri**:
  ```powershell
  python main.py --bank mandiri --input statements/mandiri_dec_2025.xlsx --output mandiri.csv --account my-mandiri
  ```
  *Note: If the XLSX is password protected, place a `password.txt` file in the same directory as the statement.*

- **CIMB**:
  ```powershell
  python main.py --bank cimb --input statements/cimb_jan_2026.pdf --output cimb.csv --account my-cimb
  ```

## Output Format
The resulting CSV will have the following columns:
- `Date`: Transaction date (MM/DD/YYYY HH:MM:SS)
- `Account`: Account identifier
- `Category`: Automated category (e.g., `Food & Beverage`, `Shopping & Groceries`, `Other`)
- `Note`: Cleaned transaction note / inferred merchant name
- `Amount`: Transaction amount (IDR)
- `Type`: `Income` or `Expense`
- `Description`: Full original description (flattened)
- `Currency`: `IDR`

## Project Structure
- `main.py`: CLI entry point.
- `parsers/`: Contains bank-specific logic (BCA, Mandiri, CIMB).
- `utils/`: Utility functions for cleaning and categorization.
- `requirements.txt`: Python package dependencies.
