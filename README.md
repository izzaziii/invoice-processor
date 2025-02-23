# Invoice Processor

A Python-based tool that processes PDF invoices using Claude AI to extract structured data and store it in MongoDB.

## Installation

### Clone the Repository
```bash
git clone https://github.com/izzaziii/invoice-processor.git
cd invoice-processor
```

### Set Up Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file in the root directory with the following variables:
```
ANTHROPIC_API_KEY=your_api_key_here
DATABASE_URI=mongodb://localhost:27017/
INVOICE_DATABASE=invoices
```

### MongoDB Setup
1. Install MongoDB Community Edition:
   - [MongoDB Installation Guide](https://www.mongodb.com/docs/manual/installation/)
   - For macOS (using Homebrew): `brew install mongodb-community`
   - For Windows: Download and install from MongoDB website

2. Start MongoDB service:
   - macOS: `brew services start mongodb-community`
   - Windows: MongoDB runs as a service automatically

## Usage

### Processing New Invoices
Run the main script with the path to your PDF invoice:
```bash
python modules/main.py "/path/to/your/invoice.pdf"
```

The script will:
1. Extract data using Claude AI
2. Check for duplicate invoices
3. Store the data in MongoDB
4. Display a success message or error if something goes wrong

### Query Examples
Check the MongoDB cheat sheet in the repository for common query examples to retrieve and analyze your invoice data.

## Project Structure
```
invoice-processor/
├── .env
├── requirements.txt
└── modules/
    ├── __init__.py
    ├── processor.py  # Handles PDF processing with Claude
    ├── db.py        # MongoDB operations
    └── main.py      # Main script
```

## Future Improvements

### Short Term
1. Add batch processing for multiple invoices
2. Implement better error handling and logging
3. Add data validation before storage
4. Create a simple web interface

### Medium Term
1. Deploy MongoDB to a remote server (Atlas)
2. Add user authentication
3. Implement API endpoints
4. Add invoice data analytics dashboard

### Long Term
1. Containerize the application using Docker
2. Set up CI/CD pipeline
3. Add support for different invoice formats
4. Implement automated testing
5. Add export functionality to different formats (CSV, Excel)

## Contributing
Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
