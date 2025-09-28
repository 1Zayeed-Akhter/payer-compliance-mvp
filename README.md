# Payer Compliance Scrub

A demo MVP for claims compliance checking and provider attestation generation. This tool uploads a claims CSV, scrubs it for compliance issues using simple rules, and outputs a cleaned CSV plus auto-generated provider attestation PDFs for flagged claims.

## ⚠️ IMPORTANT DISCLAIMER

**THIS IS A DEMO ONLY** - This tool is for demonstration purposes only. Do not use with real PHI (Protected Health Information) data. This tool is not HIPAA compliant and should not be used in production environments.

## Features

- 📁 **CSV Upload**: Upload claims data in CSV format
- 🔍 **Compliance Checking**: Automated validation of claims against compliance rules
- 📊 **Results Dashboard**: Visual display of compliance results and statistics
- 📄 **Clean CSV Export**: Download cleaned claims data
- 📋 **Provider Attestations**: Auto-generated PDF attestations for flagged claims
- 🧪 **Unit Tests**: Comprehensive test coverage for compliance rules

## Compliance Rules

The tool checks for the following compliance issues:

### Required Fields
- Missing claim ID, provider name, patient ID, procedure code, billed amount, or date of service

### Procedure Codes
- Invalid CPT code format (must be 5 digits)
- Known invalid procedure codes (00000, 99999, 11111)

### Diagnosis Codes
- Invalid ICD-10 format
- Placeholder diagnosis codes that may need review

### Billing Amounts
- Negative billing amounts
- Unusually high amounts (>$10,000)
- Zero amounts that may indicate missing data

### NPI Validation
- Invalid NPI format (must be 10 digits)
- Placeholder NPIs that may need verification

### Date Validation
- Invalid date formats
- Future dates of service
- Very old dates (outside filing window)

## Tech Stack

- **Python 3.11**
- **Streamlit** - Web UI framework
- **pandas** - Data processing
- **fpdf2** - PDF generation
- **pytest** - Testing framework

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd payer-compliance-scrub
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

1. **Start the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Test the application**:
   - Download the sample claims CSV from the app
   - Upload it back to test the compliance checking
   - Review the results and download clean CSV/PDFs

## Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_scrub.py

# Run tests with coverage
pytest --cov=scrub
```

## Project Structure

```
payer-compliance-scrub/
├── app.py                 # Streamlit UI application
├── scrub.py              # Core compliance checking logic
├── pdfs.py               # PDF generation for attestations
├── sample_claims.csv     # Sample data for testing
├── requirements.txt      # Python dependencies
├── .cursorrules          # Project coding standards
├── README.md            # This file
└── tests/
    └── test_scrub.py    # Unit tests for compliance rules
```

## Deployment to Streamlit Cloud

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository: `payer-compliance-scrub`
   - Set the main file path: `app.py`
   - Click "Deploy"

3. **Configure environment** (if needed):
   - Add any environment variables in the Streamlit Cloud dashboard
   - The app will automatically install dependencies from `requirements.txt`

## Usage

1. **Upload Claims Data**: Use the file uploader to select a CSV file with claims data
2. **Review Sample Data**: The app displays a preview of your uploaded data
3. **Process Claims**: Click "Process Claims for Compliance" to run the compliance checks
4. **Review Results**: View the compliance summary and detailed results
5. **Download Files**: 
   - Download the cleaned CSV (claims without issues)
   - Generate and download provider attestation PDFs for flagged claims

## Sample Data Format

The CSV should contain the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| claim_id | Unique claim identifier | CLM0001 |
| provider_name | Provider name | Dr. Sarah Johnson - Cardiology |
| patient_id | Patient identifier | PAT0001 |
| procedure_code | CPT procedure code | 99213 |
| billed_amount | Billed amount | 245.50 |
| date_of_service | Date of service (YYYY-MM-DD) | 2024-01-15 |
| diagnosis_code | ICD-10 diagnosis code | Z51.11 |
| place_of_service | Place of service code | 11 |
| rendering_npi | Provider NPI | 1234567890 |

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Commit your changes: `git commit -m "Add feature"`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is for demonstration purposes only. See the disclaimer above regarding HIPAA compliance and production use.

## Support

For questions or issues with this demo application, please create an issue in the repository.
