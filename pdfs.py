"""
Payer Compliance Scrub - PDF Generation
Generates provider attestation PDFs for flagged claims.
"""

from fpdf import FPDF
from typing import List, Dict, Any
import io
import zipfile
from datetime import datetime
import pandas as pd

from scrub import ComplianceResult, check_claim


class AttestationPDF(FPDF):
    """Custom PDF class for provider attestations."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        """Add header to each page."""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Provider Compliance Attestation', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 0, 'C')


def generate_attestation_pdf(result: ComplianceResult) -> bytes:
    """
    Generate a provider attestation PDF for a flagged claim.
    
    Args:
        result: ComplianceResult object containing claim and issue information
        
    Returns:
        PDF content as bytes
    """
    pdf = AttestationPDF()
    pdf.add_page()
    
    # Add disclaimer
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'DEMO ONLY - NOT FOR ACTUAL USE', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, 'This is a demonstration tool. Do not use with real PHI data.', 0, 1, 'C')
    pdf.ln(10)
    
    # Claim information
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Claim Information', 0, 1)
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(40, 8, 'Claim ID:', 0, 0)
    pdf.cell(0, 8, result.claim_id, 0, 1)
    
    pdf.cell(40, 8, 'Provider:', 0, 0)
    pdf.cell(0, 8, result.provider_name, 0, 1)
    
    pdf.cell(40, 8, 'Severity:', 0, 0)
    pdf.cell(0, 8, result.severity.upper(), 0, 1)
    pdf.ln(5)
    
    # Compliance issues
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Compliance Issues Identified', 0, 1)
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 11)
    for i, issue in enumerate(result.issues, 1):
        # Handle long text wrapping
        pdf.cell(10, 8, f'{i}.', 0, 0)
        pdf.multi_cell(0, 8, issue, 0, 1)
        pdf.ln(2)
    
    pdf.ln(10)
    
    # Provider attestation section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Provider Attestation', 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 11)
    attestation_text = f"""
I, {result.provider_name}, acknowledge that the above compliance issues have been 
identified for claim {result.claim_id}. I attest that:

1. I have reviewed the identified issues and understand the compliance requirements.
2. I will take appropriate corrective action to address these issues.
3. I understand that continued non-compliance may result in claim denials or 
   other administrative actions.
4. I will implement measures to prevent similar issues in future claims.

This attestation is made in good faith and based on my review of the claim data 
and compliance requirements.

Provider Signature: _________________________    Date: _______________

Print Name: {result.provider_name}

NPI: {result.original_data.get('rendering_npi', 'N/A')}
"""
    
    pdf.multi_cell(0, 8, attestation_text, 0, 1)
    
    # Add page break for additional information if needed
    if len(result.issues) > 5:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Additional Information', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 11)
        additional_info = """
For questions about this attestation or compliance requirements, please contact 
your compliance officer or billing department.

This document should be retained in your records for audit purposes.

Compliance Resources:
- CMS Compliance Guidelines
- HIPAA Privacy and Security Rules
- State-specific billing requirements
- Payer-specific policies and procedures
"""
        pdf.multi_cell(0, 8, additional_info, 0, 1)
    
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin-1')


def make_attestation_pdf(row: Dict[str, Any]) -> bytes:
    """
    Generate a professional provider attestation PDF.
    
    This function creates a clean, professional attestation form with claim details
    and a signature section for provider attestation.
    
    Args:
        row: Dictionary containing claim information with expected columns:
             ClaimID, PatientID, ICD10, ProcCode, Provider, ServiceDate
        
    Returns:
        PDF content as bytes
        
    Raises:
        ValueError: If required claim information is missing
    """
    # Extract claim information
    claim_id = str(row.get('ClaimID', ''))
    provider_name = str(row.get('Provider', ''))
    patient_id = str(row.get('PatientID', ''))
    icd10 = str(row.get('ICD10', ''))
    proc_code = str(row.get('ProcCode', ''))
    service_date = str(row.get('ServiceDate', ''))
    
    # Validate required fields
    if not claim_id or not provider_name:
        raise ValueError("ClaimID and Provider are required fields")
    
    # Create PDF with professional settings
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    
    # Set 1-inch margins (72 points = 1 inch)
    pdf.set_margins(72, 72, 72)
    
    # Title - "Provider Attestation" centered
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 20, 'Provider Attestation', 0, 1, 'C')
    pdf.ln(10)
    
    # Header with today's date
    pdf.set_font('Arial', '', 12)
    today = datetime.now().strftime('%B %d, %Y')
    pdf.cell(0, 10, f'Date: {today}', 0, 1, 'R')
    pdf.ln(15)
    
    # Claim details in clean table-style layout
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 12, 'Claim Details', 0, 1)
    pdf.ln(8)
    
    # Table-style layout for claim information with consistent spacing
    pdf.set_font('Arial', '', 12)
    
    # Define label width for consistent alignment
    label_width = 50
    
    # Claim ID
    pdf.cell(label_width, 10, 'Claim ID:', 0, 0)
    pdf.cell(0, 10, claim_id, 0, 1)
    pdf.ln(3)
    
    # Patient ID
    pdf.cell(label_width, 10, 'Patient ID:', 0, 0)
    pdf.cell(0, 10, patient_id, 0, 1)
    pdf.ln(3)
    
    # Service Date
    pdf.cell(label_width, 10, 'Service Date:', 0, 0)
    pdf.cell(0, 10, service_date, 0, 1)
    pdf.ln(3)
    
    # Diagnosis (ICD-10)
    pdf.cell(label_width, 10, 'Diagnosis (ICD-10):', 0, 0)
    pdf.cell(0, 10, icd10, 0, 1)
    pdf.ln(3)
    
    # Procedure Code
    pdf.cell(label_width, 10, 'Procedure Code:', 0, 0)
    pdf.cell(0, 10, proc_code, 0, 1)
    pdf.ln(3)
    
    # Provider
    pdf.cell(label_width, 10, 'Provider:', 0, 0)
    pdf.cell(0, 10, provider_name, 0, 1)
    pdf.ln(20)
    
    # Attestation section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 12, 'Attestation', 0, 1)
    pdf.ln(8)
    
    # Attestation statement
    pdf.set_font('Arial', '', 12)
    attestation_text = """I attest that the diagnoses and procedures billed on this claim are supported by contemporaneous clinical documentation for the date of service listed above."""
    
    pdf.multi_cell(0, 10, attestation_text, 0, 1)
    pdf.ln(30)
    
    # Footer with signature section
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Provider Signature: _________________________   Date: ___________', 0, 1)
    
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin-1')


def zip_attestations(df: pd.DataFrame) -> bytes:
    """
    Generate attestation PDFs for all rows with issues and return as a ZIP file.
    
    This function processes a DataFrame, generates attestation PDFs for rows
    that have issues (non-empty Issues column), and packages them into a ZIP file.
    
    Args:
        df: DataFrame containing claims data with an 'Issues' column
        
    Returns:
        ZIP file content as bytes containing all attestation PDFs
        
    Raises:
        ValueError: If DataFrame is empty or missing required columns
    """
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    
    if 'Issues' not in df.columns:
        raise ValueError("DataFrame must contain an 'Issues' column")
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        pdf_count = 0
        
        for index, row in df.iterrows():
            # Only process rows with issues
            issues = row.get('Issues', [])
            if issues:  # Non-empty issues list
                try:
                    # Generate PDF for this row
                    pdf_bytes = make_attestation_pdf(row.to_dict())
                    
                    # Create filename
                    claim_id = str(row.get('ClaimID', f'claim_{index}'))
                    provider_name = str(row.get('Provider', 'unknown_provider'))
                    # Clean filename characters
                    safe_provider = "".join(c for c in provider_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_provider = safe_provider.replace(' ', '_')
                    
                    filename = f"attestation_{claim_id}_{safe_provider}.pdf"
                    
                    # Add PDF to ZIP
                    zip_file.writestr(filename, pdf_bytes)
                    pdf_count += 1
                    
                except Exception as e:
                    # Log error but continue processing other rows
                    print(f"Warning: Failed to generate PDF for row {index}: {e}")
                    continue
    
    if pdf_count == 0:
        # Create a placeholder ZIP with a message
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            message = "No claims with compliance issues found. No attestations generated."
            zip_file.writestr("no_attestations_needed.txt", message)
    
    # Return ZIP file as bytes
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def generate_batch_attestations(results: List[ComplianceResult]) -> Dict[str, bytes]:
    """
    Generate multiple attestation PDFs for a batch of flagged claims.
    
    Args:
        results: List of ComplianceResult objects
        
    Returns:
        Dictionary mapping provider names to PDF bytes
    """
    attestations = {}
    
    for result in results:
        if result.issues:  # Only generate for flagged claims
            provider_key = result.provider_name.replace(' ', '_')
            attestations[provider_key] = generate_attestation_pdf(result)
    
    return attestations


def create_summary_report(results: List[ComplianceResult]) -> bytes:
    """
    Create a summary report PDF for all compliance results.
    
    Args:
        results: List of ComplianceResult objects
        
    Returns:
        PDF content as bytes
    """
    pdf = AttestationPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Compliance Check Summary Report', 0, 1, 'C')
    pdf.ln(10)
    
    # Disclaimer
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'DEMO ONLY - NOT FOR ACTUAL USE', 0, 1, 'C')
    pdf.ln(5)
    
    # Summary statistics
    total_claims = len(results)
    flagged_claims = sum(1 for r in results if r.issues)
    clean_claims = total_claims - flagged_claims
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Summary Statistics', 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(60, 8, 'Total Claims Processed:', 0, 0)
    pdf.cell(0, 8, str(total_claims), 0, 1)
    
    pdf.cell(60, 8, 'Claims with Issues:', 0, 0)
    pdf.cell(0, 8, str(flagged_claims), 0, 1)
    
    pdf.cell(60, 8, 'Clean Claims:', 0, 0)
    pdf.cell(0, 8, str(clean_claims), 0, 1)
    
    compliance_rate = (clean_claims / total_claims * 100) if total_claims > 0 else 0
    pdf.cell(60, 8, 'Compliance Rate:', 0, 0)
    pdf.cell(0, 8, f'{compliance_rate:.1f}%', 0, 1)
    
    pdf.ln(10)
    
    # Detailed results
    if flagged_claims > 0:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Flagged Claims Details', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 10)
        for result in results:
            if result.issues:
                pdf.cell(0, 8, f'Claim ID: {result.claim_id} | Provider: {result.provider_name}', 0, 1)
                pdf.cell(0, 8, f'Severity: {result.severity.upper()}', 0, 1)
                for issue in result.issues:
                    pdf.cell(10, 6, '-', 0, 0)
                    pdf.cell(0, 6, issue, 0, 1)
                pdf.ln(3)
    
    return pdf.output(dest='S').encode('latin-1')
