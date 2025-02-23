import anthropic
import base64
import json
from pathlib import Path
from dotenv import load_dotenv


def process_invoice(pdf_path):
    # Load PDF and encode
    with open(pdf_path, "rb") as file:
        pdf_data = base64.b64encode(file.read()).decode("utf-8")

    # Initialize Claude client
    client = anthropic.Anthropic()

    prompt_template = {
        "invoice_details": {
            "invoice_issuer": "",
            "invoice_date": "",
            "invoice_number": "",
            "total_cost": "",
        },
        "campaign_details": {
            "campaign_name": "",
            "campaign_duration": {"start_date": "", "end_date": ""},
        },
        "line_items": [
            {
                "description": "",
                "platform": "",
                "funnel_stage": "",
                "language": "",
                "ad_format": "",
                "cost": "",
            }
        ],
    }

    # Create message
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
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
                        "text": f"""Extract and return the following information in valid JSON format with no additional text. Use this exact structure:
{json.dumps(prompt_template, indent=2)}

For funnel_stage, only use: awareness, consideration, conversion, or combination.
If any field is not found in the invoice, leave it as an empty string.""",
                    },
                ],
            }
        ],
    )

    try:
        # Parse the content as JSON
        json_result = json.loads(message.content[0].text)
        # Print formatted JSON
        print(json.dumps(json_result, indent=4))
        return json_result
    except json.JSONDecodeError:
        print("Error: Could not parse response as JSON")
        print("Raw response:", message.content)
        return None


if __name__ == "__main__":
    load_dotenv()  # Load ANTHROPIC_API_KEY from .env
    pdf_path = (
        "21476_TTDC_FTTH_AO Q1_Jan 2025 (MC) copy.pdf"  # Replace with your PDF path
    )
    result = process_invoice(pdf_path)
