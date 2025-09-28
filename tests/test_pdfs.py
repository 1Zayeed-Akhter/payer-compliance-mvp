"""
Unit tests for the PDF generation functionality.
Tests the PDF generation functions in pdfs.py.
"""

import pytest
import pandas as pd
import zipfile
import io
from datetime import datetime

from pdfs import make_attestation_pdf, zip_attestations


class TestMakeAttestationPdf:
    """Test the make_attestation_pdf function."""
    
    def test_make_attestation_pdf_missing_claim_id(self):
        """Test that make_attestation_pdf raises ValueError for missing ClaimID."""
        row = {
            'Provider': 'Dr. Test',
            'PatientID': 'PAT001',
            'ICD10': 'Z51.11',
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2024-01-15'
        }
        with pytest.raises(ValueError, match="ClaimID and Provider are required fields"):
            make_attestation_pdf(row)
    
    def test_make_attestation_pdf_missing_provider(self):
        """Test that make_attestation_pdf raises ValueError for missing Provider."""
        row = {
            'ClaimID': 'CLM001',
            'PatientID': 'PAT001',
            'ICD10': 'Z51.11',
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2024-01-15'
        }
        with pytest.raises(ValueError, match="ClaimID and Provider are required fields"):
            make_attestation_pdf(row)
    
    def test_make_attestation_pdf_basic_claim(self):
        """Test make_attestation_pdf with a basic clean claim."""
        row = {
            'ClaimID': 'CLM001',
            'Provider': 'Dr. Test',
            'PatientID': 'PAT001',
            'ICD10': 'Z51.11',
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2024-01-15'
        }
        
        pdf_bytes = make_attestation_pdf(row)
        
        # Check that result is bytes
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check that PDF contains expected content
        pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
        assert 'CLM001' in pdf_content
        assert 'Dr. Test' in pdf_content
        assert 'PAT001' in pdf_content
        assert 'Z51.11' in pdf_content
        assert '99213' in pdf_content
        assert '2024-01-15' in pdf_content
        assert 'Provider Attestation' in pdf_content
        assert 'Claim Details' in pdf_content
        assert 'Attestation' in pdf_content
        assert 'Provider Signature' in pdf_content
        assert 'contemporaneous clinical documentation' in pdf_content
    
    def test_make_attestation_pdf_with_issues_column(self):
        """Test make_attestation_pdf with pre-existing Issues column (issues are ignored in new format)."""
        row = {
            'ClaimID': 'CLM001',
            'Provider': 'Dr. Test',
            'PatientID': 'PAT001',
            'ICD10': 'I50.9',  # High-audit-risk diagnosis
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2024-01-15',
            'Issues': ['High-audit-risk diagnosis', 'Missing documentation']
        }
        
        pdf_bytes = make_attestation_pdf(row)
        
        # Check that result is bytes
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check that PDF contains standard attestation content (issues are not displayed in new format)
        pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
        assert 'Provider Attestation' in pdf_content
        assert 'Claim Details' in pdf_content
        assert 'Attestation' in pdf_content
        assert 'contemporaneous clinical documentation' in pdf_content
        assert 'CLM001' in pdf_content
        assert 'Dr. Test' in pdf_content
    
    def test_make_attestation_pdf_without_issues_column(self):
        """Test make_attestation_pdf without Issues column (new format ignores compliance checks)."""
        row = {
            'ClaimID': 'CLM001',
            'Provider': 'Dr. Test',
            'PatientID': 'PAT001',
            'ICD10': 'I50.9',  # High-audit-risk diagnosis
            'ProcCode': 'J9355',  # High-cost procedure
            'DocStatus': 'Complete',  # Not "Attached"
            'ServiceDate': '2024-01-15'
        }
        
        pdf_bytes = make_attestation_pdf(row)
        
        # Check that result is bytes
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check that PDF contains standard attestation content (compliance checks are not run in new format)
        pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
        assert 'Provider Attestation' in pdf_content
        assert 'Claim Details' in pdf_content
        assert 'Attestation' in pdf_content
        assert 'contemporaneous clinical documentation' in pdf_content
        assert 'CLM001' in pdf_content
        assert 'Dr. Test' in pdf_content
    
    def test_make_attestation_pdf_clean_claim_no_issues(self):
        """Test make_attestation_pdf with a clean claim that has no issues."""
        row = {
            'ClaimID': 'CLM001',
            'Provider': 'Dr. Test',
            'PatientID': 'PAT001',
            'ICD10': 'Z51.11',
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2024-01-15',
            'Issues': []  # Empty issues list
        }
        
        pdf_bytes = make_attestation_pdf(row)
        
        # Check that result is bytes
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check that PDF contains standard attestation content
        pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
        assert 'Provider Attestation' in pdf_content
        assert 'Claim Details' in pdf_content
        assert 'Attestation' in pdf_content
        assert 'contemporaneous clinical documentation' in pdf_content
        assert 'Provider Signature' in pdf_content
    
    def test_make_attestation_pdf_special_characters(self):
        """Test make_attestation_pdf with special characters in provider name."""
        row = {
            'ClaimID': 'CLM001',
            'Provider': 'Dr. José García, M.D.',
            'PatientID': 'PAT001',
            'ICD10': 'Z51.11',
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2024-01-15'
        }
        
        pdf_bytes = make_attestation_pdf(row)
        
        # Check that result is bytes
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check that PDF contains provider name
        pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
        assert 'Dr. José García, M.D.' in pdf_content
    
    def test_make_attestation_pdf_empty_string_fields(self):
        """Test make_attestation_pdf with empty string fields."""
        row = {
            'ClaimID': 'CLM001',
            'Provider': 'Dr. Test',
            'PatientID': '',
            'ICD10': '',
            'ProcCode': '',
            'DocStatus': '',
            'ServiceDate': ''
        }
        
        pdf_bytes = make_attestation_pdf(row)
        
        # Check that result is bytes
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check that PDF still generates successfully
        pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
        assert 'CLM001' in pdf_content
        assert 'Dr. Test' in pdf_content
        assert 'Provider Attestation' in pdf_content
        assert 'Claim Details' in pdf_content
    
    def test_make_attestation_pdf_date_formatting(self):
        """Test that make_attestation_pdf includes today's date in the header."""
        row = {
            'ClaimID': 'CLM001',
            'Provider': 'Dr. Test',
            'PatientID': 'PAT001',
            'ICD10': 'Z51.11',
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2024-01-15'
        }
        
        pdf_bytes = make_attestation_pdf(row)
        
        # Check that result is bytes
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check that PDF contains today's date
        pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
        assert 'Date:' in pdf_content
        # Should contain current year
        from datetime import datetime
        current_year = str(datetime.now().year)
        assert current_year in pdf_content
    
    def test_make_attestation_pdf_professional_format(self):
        """Test that make_attestation_pdf follows the professional format requirements."""
        row = {
            'ClaimID': 'CLM001',
            'Provider': 'Dr. Test',
            'PatientID': 'PAT001',
            'ICD10': 'Z51.11',
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2024-01-15'
        }
        
        pdf_bytes = make_attestation_pdf(row)
        
        # Check that result is bytes
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check that PDF contains all required elements
        pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
        
        # Title
        assert 'Provider Attestation' in pdf_content
        
        # Header with date
        assert 'Date:' in pdf_content
        
        # Claim details section
        assert 'Claim Details' in pdf_content
        assert 'Claim ID:' in pdf_content
        assert 'Patient ID:' in pdf_content
        assert 'Service Date:' in pdf_content
        assert 'Diagnosis (ICD-10):' in pdf_content
        assert 'Procedure Code:' in pdf_content
        assert 'Provider:' in pdf_content
        
        # Attestation section
        assert 'Attestation' in pdf_content
        assert 'contemporaneous clinical documentation' in pdf_content
        
        # Footer signature section
        assert 'Provider Signature:' in pdf_content
        assert 'Date:' in pdf_content
    
    def test_make_attestation_pdf_margins_and_spacing(self):
        """Test that make_attestation_pdf uses proper margins and spacing."""
        row = {
            'ClaimID': 'CLM001',
            'Provider': 'Dr. Test',
            'PatientID': 'PAT001',
            'ICD10': 'Z51.11',
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2024-01-15'
        }
        
        pdf_bytes = make_attestation_pdf(row)
        
        # Check that result is bytes
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check that PDF is properly formatted
        pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
        
        # Should contain professional formatting elements
        assert 'Provider Attestation' in pdf_content
        assert 'Claim Details' in pdf_content
        assert 'Attestation' in pdf_content
        assert 'Provider Signature:' in pdf_content


class TestZipAttestations:
    """Test the zip_attestations function."""
    
    def test_zip_attestations_empty_dataframe(self):
        """Test that zip_attestations raises ValueError for empty DataFrame."""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="DataFrame cannot be empty"):
            zip_attestations(empty_df)
    
    def test_zip_attestations_missing_issues_column(self):
        """Test that zip_attestations raises ValueError for missing Issues column."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001'],
            'Provider': ['Dr. Test'],
            'PatientID': ['PAT001'],
            'ICD10': ['Z51.11'],
            'ProcCode': ['99213'],
            'DocStatus': ['Complete'],
            'ServiceDate': ['2024-01-15']
        })
        with pytest.raises(ValueError, match="DataFrame must contain an 'Issues' column"):
            zip_attestations(df)
    
    def test_zip_attestations_no_issues(self):
        """Test zip_attestations with DataFrame containing no issues."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001', 'CLM002'],
            'Provider': ['Dr. Test', 'Dr. Test'],
            'PatientID': ['PAT001', 'PAT002'],
            'ICD10': ['Z51.11', 'E11.9'],
            'ProcCode': ['99213', '99214'],
            'DocStatus': ['Complete', 'Complete'],
            'ServiceDate': ['2024-01-15', '2024-01-16'],
            'Issues': [[], []]  # No issues
        })
        
        zip_bytes = zip_attestations(df)
        
        # Check that result is bytes
        assert isinstance(zip_bytes, bytes)
        assert len(zip_bytes) > 0
        
        # Check that ZIP contains placeholder message
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
            file_list = zip_file.namelist()
            assert 'no_attestations_needed.txt' in file_list
            
            # Check content of placeholder file
            content = zip_file.read('no_attestations_needed.txt').decode('utf-8')
            assert 'No claims with compliance issues found' in content
    
    def test_zip_attestations_with_issues(self):
        """Test zip_attestations with DataFrame containing issues."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001', 'CLM002'],
            'Provider': ['Dr. Test', 'Dr. Test'],
            'PatientID': ['PAT001', 'PAT002'],
            'ICD10': ['I50.9', 'Z51.11'],
            'ProcCode': ['99213', '99214'],
            'DocStatus': ['Complete', 'Complete'],
            'ServiceDate': ['2024-01-15', '2024-01-16'],
            'Issues': [['High-audit-risk diagnosis'], []]  # First claim has issues
        })
        
        zip_bytes = zip_attestations(df)
        
        # Check that result is bytes
        assert isinstance(zip_bytes, bytes)
        assert len(zip_bytes) > 0
        
        # Check that ZIP contains PDF file
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
            file_list = zip_file.namelist()
            assert len(file_list) == 1
            assert file_list[0].startswith('attestation_CLM001_')
            assert file_list[0].endswith('.pdf')
            
            # Check that PDF content is valid
            pdf_content = zip_file.read(file_list[0])
            assert len(pdf_content) > 0
            assert pdf_content.startswith(b'%PDF')  # PDF header
    
    def test_zip_attestations_multiple_claims_with_issues(self):
        """Test zip_attestations with multiple claims having issues."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001', 'CLM002', 'CLM003'],
            'Provider': ['Dr. Test', 'Dr. Smith', 'Dr. Test'],
            'PatientID': ['PAT001', 'PAT002', 'PAT003'],
            'ICD10': ['I50.9', 'C50.911', 'Z51.11'],
            'ProcCode': ['99213', 'J9355', '99214'],
            'DocStatus': ['Complete', 'Complete', 'Complete'],
            'ServiceDate': ['2024-01-15', '2024-01-16', '2024-01-17'],
            'Issues': [
                ['High-audit-risk diagnosis'],
                ['High-audit-risk diagnosis', 'High-cost procedure requires attached documentation'],
                []
            ]
        })
        
        zip_bytes = zip_attestations(df)
        
        # Check that result is bytes
        assert isinstance(zip_bytes, bytes)
        assert len(zip_bytes) > 0
        
        # Check that ZIP contains 2 PDF files (2 claims with issues)
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
            file_list = zip_file.namelist()
            assert len(file_list) == 2
            
            # Check filenames
            pdf_files = [f for f in file_list if f.endswith('.pdf')]
            assert len(pdf_files) == 2
            
            # Check that each PDF is valid
            for pdf_file in pdf_files:
                pdf_content = zip_file.read(pdf_file)
                assert len(pdf_content) > 0
                assert pdf_content.startswith(b'%PDF')  # PDF header
    
    def test_zip_attestations_special_characters_in_names(self):
        """Test zip_attestations with special characters in provider names."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001'],
            'Provider': ['Dr. José García, M.D.'],
            'PatientID': ['PAT001'],
            'ICD10': ['I50.9'],
            'ProcCode': ['99213'],
            'DocStatus': ['Complete'],
            'ServiceDate': ['2024-01-15'],
            'Issues': [['High-audit-risk diagnosis']]
        })
        
        zip_bytes = zip_attestations(df)
        
        # Check that result is bytes
        assert isinstance(zip_bytes, bytes)
        assert len(zip_bytes) > 0
        
        # Check that ZIP contains PDF with cleaned filename
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
            file_list = zip_file.namelist()
            assert len(file_list) == 1
            assert file_list[0].startswith('attestation_CLM001_')
            assert file_list[0].endswith('.pdf')
            
            # Check that filename doesn't contain special characters
            filename = file_list[0]
            assert ',' not in filename
            assert '.' not in filename.split('.')[-2]  # Only extension should have dot
    
    def test_zip_attestations_missing_claim_id(self):
        """Test zip_attestations with missing ClaimID (should use index)."""
        df = pd.DataFrame({
            'ClaimID': ['', 'CLM002'],  # First claim missing ID
            'Provider': ['Dr. Test', 'Dr. Test'],
            'PatientID': ['PAT001', 'PAT002'],
            'ICD10': ['I50.9', 'Z51.11'],
            'ProcCode': ['99213', '99214'],
            'DocStatus': ['Complete', 'Complete'],
            'ServiceDate': ['2024-01-15', '2024-01-16'],
            'Issues': [['High-audit-risk diagnosis'], []]
        })
        
        zip_bytes = zip_attestations(df)
        
        # Check that result is bytes
        assert isinstance(zip_bytes, bytes)
        assert len(zip_bytes) > 0
        
        # Check that ZIP contains PDF with index-based filename
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
            file_list = zip_file.namelist()
            assert len(file_list) == 1
            assert file_list[0].startswith('attestation_claim_0_')  # Uses index 0
            assert file_list[0].endswith('.pdf')
    
    def test_zip_attestations_error_handling(self):
        """Test zip_attestations error handling for invalid rows."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001', ''],  # Second claim missing required ClaimID
            'Provider': ['Dr. Test', 'Dr. Test'],
            'PatientID': ['PAT001', 'PAT002'],
            'ICD10': ['I50.9', 'Z51.11'],
            'ProcCode': ['99213', '99214'],
            'DocStatus': ['Complete', 'Complete'],
            'ServiceDate': ['2024-01-15', '2024-01-16'],
            'Issues': [['High-audit-risk diagnosis'], ['Some issue']]
        })
        
        # Should not raise exception, but should handle errors gracefully
        zip_bytes = zip_attestations(df)
        
        # Check that result is bytes
        assert isinstance(zip_bytes, bytes)
        assert len(zip_bytes) > 0
        
        # Should contain at least one valid PDF
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
            file_list = zip_file.namelist()
            pdf_files = [f for f in file_list if f.endswith('.pdf')]
            assert len(pdf_files) >= 1  # At least one valid PDF should be generated


if __name__ == "__main__":
    pytest.main([__file__])
