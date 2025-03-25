"""
Bank Statement Processor Module
-------------------------------
This module extracts transaction data from bank statement PDFs using the Anthropic API.
It processes the results and converts them to structured data formats.
"""

import base64
import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, TypedDict, cast
from datetime import datetime

import pandas as pd
from anthropic import Anthropic, APIError
from anthropic.types import (
    MessageParam,
    ContentBlockParam,
    TextBlockParam,
    DocumentBlockParam,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Type definitions
class Transaction(TypedDict, total=False):
    """
    Type definition for transaction data

    Using total=False allows for partial dictionaries during processing,
    though the final output will include all fields.
    """

    date: str
    transaction_type: str
    transaction: str
    amount: float
    statement_balance: float


def encode_pdf(file_path: str) -> Optional[str]:
    """
    Reads a PDF file and encodes it as base64.

    Args:
        file_path: Path to the PDF file

    Returns:
        Base64 encoded string of the PDF or None if an error occurs

    Example:
        >>> encoded_data = encode_pdf("statements/february.pdf")
        >>> print("Encoded data length:", len(encoded_data) if encoded_data else "Failed")
    """
    try:
        file_path_obj: Path = Path(file_path)
        if not file_path_obj.exists():
            logger.error(f"File not found: {file_path}")
            return None

        with open(file_path_obj, "rb") as f:
            file_data: bytes = f.read()
            encoded_data: str = base64.standard_b64encode(file_data).decode("utf-8")
            return encoded_data
    except Exception as e:
        logger.error(f"Error encoding PDF {file_path}: {str(e)}")
        return None


def extract_transactions(
    pdf_data: str, model: str = "claude-3-7-sonnet-20250219", max_tokens: int = 4096
) -> Optional[str]:
    """
    Sends a PDF to Claude and extracts transaction data.

    Args:
        pdf_data: Base64 encoded PDF data
        model: Claude model to use
        max_tokens: Maximum tokens for response

    Returns:
        The raw output text from Claude or None if an error occurs
    """
    if not pdf_data:
        logger.error("No PDF data provided")
        return None

    try:
        # Initialize Anthropic client
        api_key: Optional[str] = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY environment variable not set")
            return None

        client: Anthropic = Anthropic(api_key=api_key)

        # Create the prompt for transaction extraction
        prompt: str = """
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
                    "transaction_type" : "SALE DEBIT",
                    "transaction" : "SPayLater Repayment",
                    "amount" : -147.99,
                    "statement_balance" : 5166.68
                }
            ]

            Important:
            1. Return ONLY the JSON array with no additional text or explanation
            2. Make amount a number, not a string
            3. Make sure the JSON is properly formatted with no trailing commas
        """

        # Construct message content
        document_block: DocumentBlockParam = {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": pdf_data,
            },
        }

        text_block: TextBlockParam = {
            "type": "text",
            "text": prompt,
        }

        content: List[ContentBlockParam] = [document_block, text_block]

        # Send to Claude API
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
        )

        # Extract text from response
        output_text: str = message.content[0].text
        return output_text

    except APIError as e:
        logger.error(f"Anthropic API error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error extracting transactions: {str(e)}")
        return None


def parse_claude_output(output_text: str) -> Optional[List[Transaction]]:
    """
    Parses Claude's output text into structured transaction data.
    Handles variations in transaction formats and ensures all transactions are included.

    Args:
        output_text: Raw text response from Claude

    Returns:
        List of transaction dictionaries or None if parsing completely fails

    Note:
        This function attempts to parse all transactions even with missing or malformed fields.
        Default values will be used for missing fields rather than skipping transactions.
    """
    if not output_text:
        logger.error("No output text to parse")
        return None

    try:
        # Clean the output text
        cleaned_text: str = output_text.strip()

        # Handle markdown code blocks if present
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text.replace("```json", "", 1)
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text.replace("```", "", 1)
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        # Parse the JSON data
        raw_transactions: List[Dict[str, Any]] = json.loads(cleaned_text)

        # Validate structure
        if not isinstance(raw_transactions, list):
            logger.error("Parsed JSON is not a list")
            return None

        # Convert to typed transactions and adapt to variations
        transactions: List[Transaction] = []
        for item in raw_transactions:
            try:
                # Handle missing or malformed fields with defaults
                # Date field - ensure string format
                date_value = (
                    str(item.get("date", "")) if item.get("date") is not None else ""
                )

                # Transaction type - use default if missing
                transaction_type = (
                    str(item.get("transaction_type", "TRANSACTION"))
                    if item.get("transaction_type") is not None
                    else "TRANSACTION"
                )

                # Transaction description - use default if missing
                transaction_desc = (
                    str(item.get("transaction", "Unknown transaction"))
                    if item.get("transaction") is not None
                    else "Unknown transaction"
                )

                # Amount - handle various formats
                amount_value = item.get("amount", 0)
                if isinstance(amount_value, str):
                    # Clean up string amounts (remove currency symbols, handle parentheses for negative)
                    amount_str = amount_value.replace("RM", "").replace(",", "").strip()
                    if "(" in amount_str and ")" in amount_str:
                        # Handle (100.00) format for negative numbers
                        amount_str = "-" + amount_str.replace("(", "").replace(")", "")
                    amount = float(amount_str)
                else:
                    amount = float(amount_value)

                # Statement balance - handle various formats
                balance_value = item.get("statement_balance", None)
                if balance_value is None:
                    # If missing, use a sentinel value
                    balance = 0.0
                    logger.info(
                        f"Missing statement_balance for transaction: {date_value} - {transaction_desc}"
                    )
                elif isinstance(balance_value, str):
                    # Clean up string balances
                    balance_str = (
                        balance_value.replace("RM", "").replace(",", "").strip()
                    )
                    balance = float(balance_str)
                else:
                    balance = float(balance_value)

                # Create transaction with all fields normalized
                transaction: Transaction = {
                    "date": date_value,
                    "transaction_type": transaction_type,
                    "transaction": transaction_desc,
                    "amount": amount,
                    "statement_balance": balance,
                }
                transactions.append(transaction)

            except (ValueError, TypeError) as e:
                # Instead of skipping, create a transaction with best-effort values
                logger.warning(f"Issue with transaction, using defaults: {e}")
                transaction: Transaction = {
                    "date": str(item.get("date", ""))
                    if item.get("date") is not None
                    else "",
                    "transaction_type": str(item.get("transaction_type", "UNKNOWN"))
                    if item.get("transaction_type") is not None
                    else "UNKNOWN",
                    "transaction": str(
                        item.get("transaction", "Error processing transaction")
                    )
                    if item.get("transaction") is not None
                    else "Error processing transaction",
                    "amount": 0.0,  # Default to zero for unparseable amounts
                    "statement_balance": 0.0,  # Default to zero for unparseable balances
                }
                transactions.append(transaction)

        logger.info(f"Successfully parsed {len(transactions)} transactions")
        return transactions

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        logger.debug(f"Raw output: {output_text[:200]}...")
        return None
    except Exception as e:
        logger.error(f"Error parsing output: {str(e)}")
        return None


def save_transactions(transactions: List[Transaction], output_path: str) -> bool:
    """
    Saves transaction data to a CSV file.

    Args:
        transactions: List of transaction dictionaries
        output_path: Path to save the CSV file

    Returns:
        True if successful, False otherwise
    """
    if not transactions:
        logger.error("No transactions to save")
        return False

    try:
        # Convert to DataFrame
        df: pd.DataFrame = pd.DataFrame(transactions)

        # Save to CSV
        output_path_obj: Path = Path(output_path)
        df.to_csv(output_path_obj, index=False)
        logger.info(f"Saved {len(df)} transactions to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving transactions: {str(e)}")
        return False


def process_statement(
    pdf_path: str, output_path: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    End-to-end function to process a bank statement PDF.

    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the output CSV (optional)

    Returns:
        DataFrame with transaction data or None if processing fails

    Example:
        >>> df = process_statement("statements/2025-02 Statement.pdf", "transactions.csv")
        >>> if df is not None:
        ...     print(f"Processed {len(df)} transactions")
    """
    # Generate default output path if not provided
    output_file_path: Optional[str] = output_path
    if not output_file_path:
        pdf_name: str = os.path.basename(pdf_path)
        output_file_path = f"{os.path.splitext(pdf_name)[0]}_transactions.csv"

    # Process the PDF
    pdf_data: Optional[str] = encode_pdf(pdf_path)
    if not pdf_data:
        return None

    output_text: Optional[str] = extract_transactions(pdf_data)
    if not output_text:
        return None

    transactions: Optional[List[Transaction]] = parse_claude_output(output_text)
    if not transactions:
        return None

    # Convert to DataFrame
    df: pd.DataFrame = pd.DataFrame(transactions)

    # Save if requested
    if output_file_path:
        save_transactions(transactions, output_file_path)

    return df


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        input_path: str = sys.argv[1]
        output_path: Optional[str] = sys.argv[2] if len(sys.argv) > 2 else None

        df: Optional[pd.DataFrame] = process_statement(input_path, output_path)
        if df is not None:
            print(f"Successfully processed {len(df)} transactions")
            print("\nSample data:")
            print(df.head(5))
    else:
        print("Usage: python processor.py <pdf_path> [output_csv_path]")
