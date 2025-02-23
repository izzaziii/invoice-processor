import argparse
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.processor import process_invoice
from modules.db import MongoDB
import json


def print_invoice_summary(invoice_data):
    details = invoice_data["invoice_details"]
    print("\nInvoice Summary:")
    print(f"Issuer: {details['invoice_issuer']}")
    print(f"Number: {details['invoice_number']}")
    print(f"Date: {details['invoice_date']}")
    print(f"Total Cost: {details['total_cost']}")
    print(f"Number of line items: {len(invoice_data['line_items'])}")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Process invoice PDF and store in MongoDB"
    )
    parser.add_argument("filepath", help="Path to the invoice PDF file")
    args = parser.parse_args()

    try:
        # Process invoice
        print(f"Processing invoice: {args.filepath}")
        invoice_data = process_invoice(args.filepath)

        if not invoice_data:
            raise ValueError("Failed to extract data from invoice")

        # Initialize database connection
        db = MongoDB()

        try:
            # Insert into database
            result = db.insert_invoice(invoice_data)
            print("\n✅ Success! Invoice processed and stored in database.")
            print_invoice_summary(invoice_data)

        except ValueError as e:
            print(f"\n❌ Database Error: {str(e)}")
            print("Please check if this invoice has already been processed.")

        finally:
            db.close()

    except FileNotFoundError:
        print(f"\n❌ Error: File not found at {args.filepath}")
    except Exception as e:
        print(f"\n❌ Error processing invoice: {str(e)}")
        print("Please check the file and try again.")


if __name__ == "__main__":
    main()
