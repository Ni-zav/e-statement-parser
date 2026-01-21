import argparse
import sys
from pathlib import Path
from parsers.bca import BCAParser
from parsers.mandiri import MandiriParser
from parsers.cimb import CIMBParser

def main():
    parser = argparse.ArgumentParser(description='Standalone Bank Statement Parser')
    parser.add_argument('--bank', choices=['bca', 'mandiri', 'cimb'], required=True, help='Bank type')
    parser.add_argument('--input', required=True, help='Path to statement file (PDF/XLSX)')
    parser.add_argument('--output', default='output.csv', help='Output CSV path')
    parser.add_argument('--account', default='my-account', help='Account identifier')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    print(f"Parsing {args.bank} statement: {input_path.name}...")

    if args.bank == 'bca':
        bank_parser = BCAParser(args.account)
    elif args.bank == 'mandiri':
        bank_parser = MandiriParser(args.account)
    elif args.bank == 'cimb':
        bank_parser = CIMBParser(args.account)
    else:
        print(f"Error: Unsupported bank type: {args.bank}")
        sys.exit(1)

    try:
        df = bank_parser.parse(str(input_path))
        if df.empty:
            print("No transactions found or error during parsing.")
        else:
            df.to_csv(args.output, index=False)
            print(f"Successfully parsed {len(df)} transactions to {args.output}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
