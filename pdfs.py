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
    return pdf.output(dest='S')


def make_simple_test_pdf(claim_id: str, provider: str, issues: list) -> bytes:
    """Create a simple test PDF to verify PDF generation works."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Test PDF for Claim {claim_id}', 0, 1, 'C')
        pdf.ln(10)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Provider: {provider}', 0, 1)
        pdf.cell(0, 10, f'Issues: {", ".join(issues) if issues else "None"}', 0, 1)
        pdf.ln(10)
        pdf.cell(0, 10, 'This is a test PDF to verify generation works.', 0, 1)
        return pdf.output(dest='S')
    except Exception as e:
        raise ValueError(f"Simple PDF generation failed: {e}")


def make_attestation_pdf(row: Dict[str, Any], signature_name: str = None, signed_ts: str = None) -> bytes:
    """
    Generate a professional provider attestation PDF with enhanced layout.
    
    This function creates a clean, professional attestation form with claim details,
    compliance issues, and a signature section for provider attestation.
    
    Args:
        row: Dictionary containing claim information with expected columns:
             ClaimID, PatientID, ICD10, ProcCode, Provider, ServiceDate, Issues
        signature_name: Name of the person who signed (if already signed)
        signed_ts: ISO timestamp of when it was signed (if already signed)
        
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
    issues = row.get('Issues', [])
    
    # Ensure issues is always a list
    if isinstance(issues, str):
        issues = [issue.strip() for issue in issues.split(';') if issue.strip()]
    elif not isinstance(issues, list):
        issues = []
    
    # Validate required fields - be more lenient for demo purposes
    if not claim_id:
        claim_id = f"UNKNOWN_{hash(str(row)) % 10000:04d}"
    if not provider_name:
        provider_name = "Unknown Provider"
    
    # Create PDF with professional settings
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
    except Exception as e:
        raise ValueError(f"Failed to create PDF object: {e}")
    
    # Set 1-inch margins (72 points = 1 inch)
    pdf.set_margins(72, 72, 72)
    
    # Title - "Provider Attestation – CMS Audit Preparation" centered
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 20, 'Provider Attestation - CMS Audit Preparation', 0, 1, 'C')
    
    # Draw thin deep-teal line under title
    pdf.set_draw_color(0, 128, 128)  # Deep teal color
    pdf.set_line_width(0.5)
    pdf.line(72, pdf.get_y(), 72 + (8.5 * 72) - 144, pdf.get_y())  # Full width line
    pdf.ln(15)
    
    # Claim details in clean table-style layout
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 12, 'Claim Information', 0, 1)
    pdf.ln(8)
    
    # Table-style layout for claim information with consistent spacing
    pdf.set_font('Arial', '', 12)
    
    # Define label width for consistent alignment
    label_width = 60
    
    # Claim ID
    pdf.cell(label_width, 10, 'Claim ID:', 0, 0)
    pdf.cell(0, 10, claim_id, 0, 1)
    pdf.ln(3)
    
    # Provider
    pdf.cell(label_width, 10, 'Provider:', 0, 0)
    pdf.cell(0, 10, provider_name, 0, 1)
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
    pdf.cell(label_width, 10, 'ICD-10:', 0, 0)
    pdf.cell(0, 10, icd10, 0, 1)
    pdf.ln(3)
    
    # Procedure Code
    pdf.cell(label_width, 10, 'ProcCode:', 0, 0)
    pdf.cell(0, 10, proc_code, 0, 1)
    pdf.ln(15)
    
    # Compliance Issues section (if any)
    if issues and len(issues) > 0:
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 12, 'Compliance Issues Identified', 0, 1)
        pdf.ln(8)
        
        pdf.set_font('Arial', '', 12)
        
        for i, issue in enumerate(issues, 1):
            pdf.cell(15, 10, f'{i}.', 0, 0)
            pdf.multi_cell(0, 10, str(issue), 0, 'L')
            pdf.ln(3)
        
        pdf.ln(10)
    
    # Attestation section
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 12, 'Provider Attestation', 0, 1)
    pdf.ln(8)
    
    # Standard attestation statement (exact copy from Phase 2)
    pdf.set_font('Arial', '', 12)
    attestation_text = """I attest that the documentation provided is accurate and complete for the services billed. I understand that falsification or omission may result in penalties under applicable law."""
    
    pdf.multi_cell(0, 10, attestation_text, 0, 'L')
    pdf.ln(20)
    
    # Signature section
    pdf.set_font('Arial', '', 12)
    
    if signature_name and signed_ts:
        # Already signed - show signature info
        pdf.cell(0, 10, 'Provider Signature (electronic): ______________________', 0, 1)
        pdf.ln(5)
        pdf.cell(0, 10, f'Name: {signature_name}    Date: {signed_ts}', 0, 1)
    else:
        # Not signed yet - show blank signature line
        pdf.cell(0, 10, 'Provider Signature: _________________________', 0, 1)
        pdf.ln(10)
        pdf.cell(0, 10, 'Date: ___________', 0, 1)
    
    # Footer - "Confidential – Demonstration Use Only"
    pdf.ln(20)
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, 'Confidential - Demonstration Use Only', 0, 0, 'C')
    
    # Subtle right-angle motif in footer corner
    pdf.set_draw_color(200, 200, 200)  # Very light gray
    pdf.set_line_width(0.3)
    corner_x = 8.5 * 72 - 72 - 20  # Right margin - 20 points
    corner_y = 11 * 72 - 72 - 20   # Bottom margin - 20 points
    pdf.line(corner_x - 10, corner_y, corner_x, corner_y)  # Horizontal line
    pdf.line(corner_x, corner_y - 10, corner_x, corner_y)  # Vertical line
    
    # Return PDF as bytes
    return pdf.output(dest='S')


def zip_attestations(df_or_db_rows: pd.DataFrame) -> bytes:
    """
    Generate attestation PDFs for all rows with issues and return as a ZIP file with audit trail.
    
    This function processes a DataFrame (either dashboard DataFrame with attestation data
    or compliance results df), generates attestation PDFs for rows that have issues,
    and packages them into a ZIP file with an audit summary CSV.
    
    Args:
        df_or_db_rows: DataFrame containing claims data. Can be:
                      - Dashboard DataFrame with attestation data (has attestation_status, signed_name, signed_at)
                      - Compliance results DataFrame with 'Issues' column
        
    Returns:
        ZIP file content as bytes containing all attestation PDFs and audit_summary.csv
        
    Raises:
        ValueError: If DataFrame is empty or missing required columns
    """
    if df_or_db_rows.empty:
        raise ValueError("DataFrame cannot be empty")
    
    # Determine if this is a dashboard DataFrame (has attestation data) or compliance results
    is_dashboard_df = 'attestation_status' in df_or_db_rows.columns
    
    # Debug info
    print(f"ZIP Generation: DataFrame type = {'Dashboard' if is_dashboard_df else 'Compliance Results'}")
    print(f"ZIP Generation: Total rows = {len(df_or_db_rows)}")
    print(f"ZIP Generation: Columns = {list(df_or_db_rows.columns)}")
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        pdf_count = 0
        audit_rows = []
        
        for index, row in df_or_db_rows.iterrows():
            # Check if row has issues (different logic for dashboard vs compliance results)
            if is_dashboard_df:
                # Dashboard DataFrame - all rows should have issues (they were flagged to get here)
                # For dashboard data, we trust that if it's in the dashboard, it has issues
                issues = str(row.get('issues', ''))
                has_issues = True  # Always true for dashboard data - they were flagged to get here
            else:
                # Compliance results DataFrame - check Issues column
                issues = row.get('Issues', [])
                has_issues = issues and len(issues) > 0
            
            if has_issues:
                print(f"Processing row {index}: claim_id={row.get('claim_id', 'N/A')}, has_issues={has_issues}")
                try:
                    # Prepare row data for PDF generation
                    # Convert issues to list format for PDF generation
                    if isinstance(issues, str):
                        issues_list = [issue.strip() for issue in issues.split(';') if issue.strip()]
                    else:
                        issues_list = issues if isinstance(issues, list) else []
                    
                    pdf_row_data = {
                        'ClaimID': str(row.get('claim_id', row.get('id', row.get('ClaimID', '')))),
                        'PatientID': str(row.get('patient_id', row.get('PatientID', ''))),
                        'ServiceDate': str(row.get('service_date', row.get('ServiceDate', ''))),
                        'ICD10': str(row.get('icd10', row.get('ICD10', ''))),
                        'ProcCode': str(row.get('proc_code', row.get('ProcCode', ''))),
                        'Provider': str(row.get('provider', row.get('Provider', ''))),
                        'Issues': issues_list
                    }
                    
                    # Get signature info if available (dashboard DataFrame)
                    signature_name = None
                    signed_ts = None
                    if is_dashboard_df:
                        signature_name = row.get('signed_name')
                        signed_at = row.get('signed_at')
                        if pd.notna(signed_at):
                            signed_ts = str(signed_at)
                    
                    
                    # Generate PDF for this row
                    print(f"  -> Generating PDF for {pdf_row_data['ClaimID']}")
                    pdf_bytes = make_attestation_pdf(pdf_row_data, signature_name, signed_ts)
                    print(f"  -> PDF generated: {len(pdf_bytes)} bytes")
                    
                    # Create filename
                    claim_id = pdf_row_data['ClaimID']
                    provider_name = pdf_row_data['Provider']
                    # Clean filename characters
                    safe_provider = "".join(c for c in provider_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_provider = safe_provider.replace(' ', '_')
                    
                    filename = f"Claim_{claim_id}_{safe_provider}.pdf"
                    
                    # Add PDF to ZIP
                    zip_file.writestr(filename, pdf_bytes)
                    pdf_count += 1
                    print(f"  -> Added {filename} to ZIP")
                    
                    # Add to audit trail with proper status handling
                    status = row.get('attestation_status', 'Pending') if is_dashboard_df else 'Pending'
                    signed_at = row.get('signed_at', '') if is_dashboard_df else ''
                    verified_at = row.get('verified_at', '') if is_dashboard_df else ''
                    
                    # Clean up timestamp formatting
                    if pd.notna(signed_at) and signed_at != '':
                        signed_at = str(signed_at)
                    else:
                        signed_at = ''
                        
                    if pd.notna(verified_at) and verified_at != '':
                        verified_at = str(verified_at)
                    else:
                        verified_at = ''
                    
                    audit_rows.append({
                        'ClaimID': claim_id,
                        'Provider': provider_name,
                        'Issues': '; '.join(issues_list) if issues_list else '',
                        'Status': status,
                        'SignedAt': signed_at,
                        'VerifiedAt': verified_at,
                        'LastReminderAt': row.get('last_reminder_at', '') if is_dashboard_df else ''
                    })
                    
                except Exception as e:
                    # Log error but continue processing other rows
                    print(f"ERROR: Failed to generate PDF for row {index}: {e}")
                    continue
        
        # Add audit summary CSV
        if audit_rows:
            audit_df = pd.DataFrame(audit_rows)
            csv_buffer = io.StringIO()
            audit_df.to_csv(csv_buffer, index=False)
            zip_file.writestr("audit_summary.csv", csv_buffer.getvalue())
        else:
            # No flagged claims - add README.txt
            readme_content = """No flagged claims found.

All claims in the uploaded dataset passed compliance checks and do not require provider attestations.

This ZIP file was generated by the Payer Compliance Scrub tool - a demonstration application for claims compliance checking and provider attestation generation.

DEMO ONLY - This tool is for demonstration purposes only. Do not use with real PHI data."""
            zip_file.writestr("README.txt", readme_content)
    
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
