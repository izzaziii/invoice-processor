from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
import os


class MongoDB:
    def __init__(self):
        load_dotenv()
        self.client = MongoClient(os.getenv("DATABASE_URI"))
        self.db = self.client[os.getenv("INVOICE_DATABASE")]
        self.collection = self.db.invoices
        self.collection.create_index("invoice_details.invoice_number", unique=True)

    def insert_invoice(self, invoice_data):
        try:
            return self.collection.insert_one(invoice_data)
        except DuplicateKeyError:
            raise ValueError(
                f"Invoice {invoice_data['invoice_details']['invoice_number']} already exists in database"
            )

    def get_invoice(self, invoice_number):
        return self.collection.find_one(
            {"invoice_details.invoice_number": invoice_number}
        )

    def get_all_invoices(self):
        return list(self.collection.find())

    def update_invoice(self, invoice_number, updated_data):
        return self.collection.update_one(
            {"invoice_details.invoice_number": invoice_number}, {"$set": updated_data}
        )

    def delete_invoice(self, invoice_number):
        return self.collection.delete_one(
            {"invoice_details.invoice_number": invoice_number}
        )

    def close(self):
        self.client.close()


# Export the class
__all__ = ["MongoDB"]
