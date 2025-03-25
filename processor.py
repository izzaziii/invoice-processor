import base64
from anthropic import Anthropic
import json
import pandas as pd

# Load a local file, encode in base64
with open("statements\\2025-02 Statement.pdf", "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

# Send to Claude
client = Anthropic()
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=5000,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {
                    "type": "text",
                    # Input message to claude below
                    "text": """
                        Extract all my transactions from my bank statement, and return only a JSON array. Format each document as:

                        {
                            "date" : "DD/MM/YY",
                            "transaction_type" : "type of transaction",
                            "transaction" : "merchant or description",
                            "amount" : float value of amount,
                            "statement_balance" : statement balance value
                        }

                        Remove all symbols from the amount, like RM, or commas, but include the symbols for the transactions, like positive or negative.

                        Example of expected format:
                        [
                            {
                                "date" : "01/02/25",
                                "transaction_type" : "SALE DEBIT"
                                "transaction" : "SPayLater Repayment",
                                "amount" : -147.99,
                                "statement_balance" : 5166.68,
                            },
                            {
                                "date" : "03/02/25",
                                "transaction_type" : "TRANSFER FROM A/C"
                                "transaction" : "MBBQR1522764",
                                "amount" : -27.50,
                                "statement_balance" : 5016.18,
                            },

                        ]

                        """,
                },
            ],
        }
    ],
)

output = message.content[0].text

json_data = json.loads(output)

df = pd.DataFrame(json_data)

df.head(10)

df.to_csv("maybankfeb25.csv", index=False)
