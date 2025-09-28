"""
Unit tests for the compliance scrubbing functionality.
Tests the core rules and logic in scrub.py.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from scrub import (
    check_claim_compliance,
    check_required_fields,
    check_procedure_codes,
    check_diagnosis_codes,
    check_billing_amounts,
    check_npi_format,
    check_date_format,
    get_compliance_summary,
    check_claim,
    apply_checks,
    cleaned_csv_bytes,
    ComplianceResult
)


class TestRequiredFields:
    """Test required field validation."""
    
    def test_missing_claim_id(self):
        """Test detection of missing claim ID."""
        claim_data = {
            "provider_name": "Dr. Test",
            "patient_id": "PAT001",
            "procedure_code": "99213",
            "billed_amount": 100.00,
            "date_of_service": "2024-01-01"
        }
        issues = check_required_fields(claim_data)
        assert any("Missing required field 'claim_id'" in issue for issue in issues)
    
    def test_missing_provider_name(self):
        """Test detection of missing provider name."""
        claim_data = {
            "claim_id": "CLM001",
            "patient_id": "PAT001",
            "procedure_code": "99213",
            "billed_amount": 100.00,
            "date_of_service": "2024-01-01"
        }
        issues = check_required_fields(claim_data)
        assert any("Missing required field 'provider_name'" in issue for issue in issues)
    
    def test_all_required_fields_present(self):
        """Test that no issues are found when all required fields are present."""
        claim_data = {
            "claim_id": "CLM001",
            "provider_name": "Dr. Test",
            "patient_id": "PAT001",
            "procedure_code": "99213",
            "billed_amount": 100.00,
            "date_of_service": "2024-01-01"
        }
        issues = check_required_fields(claim_data)
        assert len(issues) == 0


class TestProcedureCodes:
    """Test procedure code validation."""
    
    def test_valid_cpt_code(self):
        """Test that valid CPT codes pass validation."""
        claim_data = {"procedure_code": "99213"}
        issues = check_procedure_codes(claim_data)
        assert len(issues) == 0
    
    def test_invalid_cpt_format(self):
        """Test detection of invalid CPT code format."""
        claim_data = {"procedure_code": "9921"}
        issues = check_procedure_codes(claim_data)
        assert any("Invalid procedure code format" in issue for issue in issues)
    
    def test_invalid_cpt_code(self):
        """Test detection of known invalid CPT codes."""
        claim_data = {"procedure_code": "00000"}
        issues = check_procedure_codes(claim_data)
        assert any("Invalid procedure code '00000'" in issue for issue in issues)
    
    def test_empty_procedure_code(self):
        """Test that empty procedure codes don't cause errors."""
        claim_data = {"procedure_code": ""}
        issues = check_procedure_codes(claim_data)
        assert len(issues) == 0


class TestDiagnosisCodes:
    """Test diagnosis code validation."""
    
    def test_valid_icd10_code(self):
        """Test that valid ICD-10 codes pass validation."""
        claim_data = {"diagnosis_code": "Z51.11"}
        issues = check_diagnosis_codes(claim_data)
        assert len(issues) == 0
    
    def test_invalid_icd10_format(self):
        """Test detection of invalid ICD-10 format."""
        claim_data = {"diagnosis_code": "Z5111"}
        issues = check_diagnosis_codes(claim_data)
        assert any("Invalid diagnosis code format" in issue for issue in issues)
    
    def test_placeholder_diagnosis_code(self):
        """Test detection of placeholder diagnosis codes."""
        claim_data = {"diagnosis_code": "Z00.0"}
        issues = check_diagnosis_codes(claim_data)
        assert any("Placeholder diagnosis code" in issue for issue in issues)


class TestBillingAmounts:
    """Test billing amount validation."""
    
    def test_valid_billing_amount(self):
        """Test that valid billing amounts pass validation."""
        claim_data = {"billed_amount": 245.50}
        issues = check_billing_amounts(claim_data)
        assert len(issues) == 0
    
    def test_negative_billing_amount(self):
        """Test detection of negative billing amounts."""
        claim_data = {"billed_amount": -100.00}
        issues = check_billing_amounts(claim_data)
        assert any("Negative billing amount" in issue for issue in issues)
    
    def test_high_billing_amount(self):
        """Test detection of unusually high billing amounts."""
        claim_data = {"billed_amount": 15000.00}
        issues = check_billing_amounts(claim_data)
        assert any("Unusually high billing amount" in issue for issue in issues)
    
    def test_zero_billing_amount(self):
        """Test detection of zero billing amounts."""
        claim_data = {"billed_amount": 0}
        issues = check_billing_amounts(claim_data)
        assert any("Zero billing amount" in issue for issue in issues)
    
    def test_invalid_billing_amount_format(self):
        """Test detection of invalid billing amount formats."""
        claim_data = {"billed_amount": "invalid"}
        issues = check_billing_amounts(claim_data)
        assert any("Invalid billing amount format" in issue for issue in issues)


class TestNPIFormat:
    """Test NPI format validation."""
    
    def test_valid_npi(self):
        """Test that valid NPIs pass validation."""
        claim_data = {"rendering_npi": "1987654321"}
        issues = check_npi_format(claim_data)
        assert len(issues) == 0
    
    def test_invalid_npi_format(self):
        """Test detection of invalid NPI format."""
        claim_data = {"rendering_npi": "198765432"}
        issues = check_npi_format(claim_data)
        assert any("Invalid NPI format" in issue for issue in issues)
    
    def test_placeholder_npi(self):
        """Test detection of placeholder NPIs."""
        claim_data = {"rendering_npi": "0000000001"}
        issues = check_npi_format(claim_data)
        assert any("Placeholder NPI" in issue for issue in issues)


class TestDateFormat:
    """Test date format validation."""
    
    def test_valid_date(self):
        """Test that valid dates pass validation."""
        claim_data = {"date_of_service": "2024-01-15"}
        issues = check_date_format(claim_data)
        assert len(issues) == 0
    
    def test_invalid_date_format(self):
        """Test detection of invalid date formats."""
        claim_data = {"date_of_service": "01/15/2024"}
        issues = check_date_format(claim_data)
        assert any("Invalid date format" in issue for issue in issues)
    
    def test_future_date(self):
        """Test detection of future dates."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        claim_data = {"date_of_service": future_date}
        issues = check_date_format(claim_data)
        assert any("Future date of service" in issue for issue in issues)
    
    def test_very_old_date(self):
        """Test detection of very old dates."""
        old_date = (datetime.now() - timedelta(days=800)).strftime("%Y-%m-%d")
        claim_data = {"date_of_service": old_date}
        issues = check_date_format(claim_data)
        assert any("Very old date of service" in issue for issue in issues)


class TestClaimCompliance:
    """Test overall claim compliance checking."""
    
    def test_clean_claim(self):
        """Test that a clean claim passes all checks."""
        claim_data = {
            "claim_id": "CLM001",
            "provider_name": "Dr. Test",
            "patient_id": "PAT001",
            "procedure_code": "99213",
            "billed_amount": 245.50,
            "date_of_service": "2024-01-15",
            "diagnosis_code": "Z51.11",
            "place_of_service": "11",
            "rendering_npi": "1987654321"
        }
        result = check_claim_compliance(claim_data)
        assert len(result.issues) == 0
        assert result.severity == "low"
    
    def test_claim_with_multiple_issues(self):
        """Test a claim with multiple compliance issues."""
        claim_data = {
            "claim_id": "",  # Missing required field
            "provider_name": "Dr. Test",
            "patient_id": "PAT001",
            "procedure_code": "00000",  # Invalid procedure code
            "billed_amount": -100.00,  # Negative amount
            "date_of_service": "invalid-date",  # Invalid date
            "diagnosis_code": "Z00.0",  # Placeholder code
            "place_of_service": "11",
            "rendering_npi": "198765432"  # Invalid NPI format
        }
        result = check_claim_compliance(claim_data)
        assert len(result.issues) > 0
        assert result.severity == "high"  # Should be high due to critical issues


class TestComplianceSummary:
    """Test compliance summary generation."""
    
    def test_summary_with_mixed_results(self):
        """Test summary generation with mixed compliance results."""
        results = [
            ComplianceResult("CLM001", "Dr. Test", [], "low", {}),
            ComplianceResult("CLM002", "Dr. Test", ["WARNING: Test issue"], "medium", {}),
            ComplianceResult("CLM003", "Dr. Test", ["CRITICAL: Test issue"], "high", {}),
            ComplianceResult("CLM004", "Dr. Test", [], "low", {})
        ]
        
        summary = get_compliance_summary(results)
        
        assert summary["total_claims"] == 4
        assert summary["flagged_claims"] == 2
        assert summary["clean_claims"] == 2
        assert summary["compliance_rate"] == 50.0
        assert summary["severity_breakdown"]["low"] == 0
        assert summary["severity_breakdown"]["medium"] == 1
        assert summary["severity_breakdown"]["high"] == 1


class TestCheckClaim:
    """Test the check_claim function with specific compliance rules."""
    
    def test_clean_claim_no_issues(self):
        """Test that a clean claim with no issues returns empty list."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "Z51.11",
            "ProcCode": "99213",
            "Provider": "Dr. Test",
            "DocStatus": "Complete",
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert len(issues) == 0
    
    def test_missing_documentation(self):
        """Test detection of missing documentation."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "Z51.11",
            "ProcCode": "99213",
            "Provider": "Dr. Test",
            "DocStatus": "",  # Missing documentation
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert "Missing documentation" in issues
    
    def test_missing_documentation_none(self):
        """Test detection of missing documentation when DocStatus is None."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "Z51.11",
            "ProcCode": "99213",
            "Provider": "Dr. Test",
            "DocStatus": None,  # Missing documentation
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert "Missing documentation" in issues
    
    def test_missing_documentation_whitespace(self):
        """Test detection of missing documentation when DocStatus is whitespace."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "Z51.11",
            "ProcCode": "99213",
            "Provider": "Dr. Test",
            "DocStatus": "   ",  # Whitespace only
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert "Missing documentation" in issues
    
    def test_mismatched_documentation_rule2(self):
        """Test detection of mismatched documentation (Rule 2)."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "Z51.11",
            "ProcCode": "J9355",  # High-cost procedure
            "Provider": "Dr. Test",
            "DocStatus": "Complete",  # Should be "Attached" for high-cost procedures
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert "Mismatched documentation" in issues
    
    def test_high_audit_risk_diagnosis_i50(self):
        """Test detection of high-audit-risk diagnosis starting with I50."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "I50.9",  # Heart failure - high audit risk
            "ProcCode": "99213",
            "Provider": "Dr. Test",
            "DocStatus": "Complete",
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert "High-audit-risk diagnosis" in issues
    
    def test_high_audit_risk_diagnosis_c50(self):
        """Test detection of high-audit-risk diagnosis starting with C50."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "C50.911",  # Breast cancer - high audit risk
            "ProcCode": "99213",
            "Provider": "Dr. Test",
            "DocStatus": "Complete",
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert "High-audit-risk diagnosis" in issues
    
    def test_high_audit_risk_diagnosis_i50_variations(self):
        """Test detection of various I50 diagnosis codes."""
        test_codes = ["I50", "I50.1", "I50.9", "I50.10", "I50.20"]
        for code in test_codes:
            row = {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": code,
                "ProcCode": "99213",
                "Provider": "Dr. Test",
                "DocStatus": "Complete",
                "ServiceDate": "2024-01-15"
            }
            issues = check_claim(row)
            assert "High-audit-risk diagnosis" in issues
    
    def test_high_audit_risk_diagnosis_c50_variations(self):
        """Test detection of various C50 diagnosis codes."""
        test_codes = ["C50", "C50.1", "C50.9", "C50.911", "C50.112"]
        for code in test_codes:
            row = {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": code,
                "ProcCode": "99213",
                "Provider": "Dr. Test",
                "DocStatus": "Complete",
                "ServiceDate": "2024-01-15"
            }
            issues = check_claim(row)
            assert "High-audit-risk diagnosis" in issues
    
    def test_high_cost_procedure_j9355_missing_attached_doc(self):
        """Test detection of high-cost procedure J9355 without attached documentation."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "Z51.11",
            "ProcCode": "J9355",  # High-cost procedure
            "Provider": "Dr. Test",
            "DocStatus": "Complete",  # Not "Attached"
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert "High-cost procedure requires attached documentation" in issues
        assert "Mismatched documentation" in issues  # Should also trigger Rule 2
    
    def test_high_cost_procedure_j1940_missing_attached_doc(self):
        """Test detection of high-cost procedure J1940 without attached documentation."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "Z51.11",
            "ProcCode": "J1940",  # High-cost procedure
            "Provider": "Dr. Test",
            "DocStatus": "Complete",  # Not "Attached"
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert "High-cost procedure requires attached documentation" in issues
        assert "Mismatched documentation" in issues  # Should also trigger Rule 2
    
    def test_high_cost_procedure_j9355_with_attached_doc(self):
        """Test that high-cost procedure J9355 with attached documentation passes."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "Z51.11",
            "ProcCode": "J9355",  # High-cost procedure
            "Provider": "Dr. Test",
            "DocStatus": "Attached",  # Has attached documentation
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert "High-cost procedure requires attached documentation" not in issues
    
    def test_high_cost_procedure_j1940_with_attached_doc(self):
        """Test that high-cost procedure J1940 with attached documentation passes."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "Z51.11",
            "ProcCode": "J1940",  # High-cost procedure
            "Provider": "Dr. Test",
            "DocStatus": "Attached",  # Has attached documentation
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert "High-cost procedure requires attached documentation" not in issues
    
    def test_multiple_issues_combined(self):
        """Test a claim with multiple compliance issues."""
        row = {
            "ClaimID": "CLM001",
            "PatientID": "PAT001",
            "ICD10": "I50.9",  # High-audit-risk diagnosis
            "ProcCode": "J9355",  # High-cost procedure
            "Provider": "Dr. Test",
            "DocStatus": "",  # Missing documentation
            "ServiceDate": "2024-01-15"
        }
        issues = check_claim(row)
        assert len(issues) == 3
        assert "Missing documentation" in issues
        assert "High-audit-risk diagnosis" in issues
        assert "High-cost procedure requires attached documentation" in issues
    
    def test_regular_procedure_codes_no_issues(self):
        """Test that regular procedure codes don't trigger high-cost procedure issues."""
        regular_codes = ["99213", "99214", "99215", "99202", "99203"]
        for code in regular_codes:
            row = {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "Z51.11",
                "ProcCode": code,
                "Provider": "Dr. Test",
                "DocStatus": "Complete",
                "ServiceDate": "2024-01-15"
            }
            issues = check_claim(row)
            assert "High-cost procedure requires attached documentation" not in issues
    
    def test_regular_diagnosis_codes_no_issues(self):
        """Test that regular diagnosis codes don't trigger high-audit-risk issues."""
        regular_codes = ["Z51.11", "E11.9", "M25.561", "L70.9", "J06.9"]
        for code in regular_codes:
            row = {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": code,
                "ProcCode": "99213",
                "Provider": "Dr. Test",
                "DocStatus": "Complete",
                "ServiceDate": "2024-01-15"
            }
            issues = check_claim(row)
            assert "High-audit-risk diagnosis" not in issues


class TestApplyChecks:
    """Test the apply_checks function."""
    
    def test_apply_checks_empty_dataframe(self):
        """Test that apply_checks raises ValueError for empty DataFrame."""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="DataFrame cannot be empty"):
            apply_checks(empty_df)
    
    def test_apply_checks_clean_claims(self):
        """Test apply_checks with clean claims that have no issues."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001', 'CLM002'],
            'PatientID': ['PAT001', 'PAT002'],
            'ICD10': ['Z51.11', 'E11.9'],
            'ProcCode': ['99213', '99214'],
            'Provider': ['Dr. Test', 'Dr. Test'],
            'DocStatus': ['Complete', 'Complete'],
            'ServiceDate': ['2024-01-15', '2024-01-16']
        })
        
        result_df = apply_checks(df)
        
        # Check that Issues column was added
        assert 'Issues' in result_df.columns
        
        # Check that all claims have no issues
        for issues in result_df['Issues']:
            assert issues == []
        
        # Check that original columns are preserved
        assert list(result_df.columns) == ['ClaimID', 'PatientID', 'ICD10', 'ProcCode', 'Provider', 'DocStatus', 'ServiceDate', 'Issues']
    
    def test_apply_checks_missing_documentation(self):
        """Test apply_checks with claims missing documentation."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001', 'CLM002'],
            'PatientID': ['PAT001', 'PAT002'],
            'ICD10': ['Z51.11', 'E11.9'],
            'ProcCode': ['99213', '99214'],
            'Provider': ['Dr. Test', 'Dr. Test'],
            'DocStatus': ['', 'Complete'],  # First claim missing documentation
            'ServiceDate': ['2024-01-15', '2024-01-16']
        })
        
        result_df = apply_checks(df)
        
        # Check first claim has missing documentation issue
        assert 'Missing documentation' in result_df.iloc[0]['Issues']
        
        # Check second claim has no issues
        assert result_df.iloc[1]['Issues'] == []
    
    def test_apply_checks_high_audit_risk_diagnosis(self):
        """Test apply_checks with high-audit-risk diagnosis codes."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001', 'CLM002'],
            'PatientID': ['PAT001', 'PAT002'],
            'ICD10': ['I50.9', 'Z51.11'],  # First claim has high-audit-risk diagnosis
            'ProcCode': ['99213', '99214'],
            'Provider': ['Dr. Test', 'Dr. Test'],
            'DocStatus': ['Complete', 'Complete'],
            'ServiceDate': ['2024-01-15', '2024-01-16']
        })
        
        result_df = apply_checks(df)
        
        # Check first claim has high-audit-risk diagnosis issue
        assert 'High-audit-risk diagnosis' in result_df.iloc[0]['Issues']
        
        # Check second claim has no issues
        assert result_df.iloc[1]['Issues'] == []
    
    def test_apply_checks_high_cost_procedure(self):
        """Test apply_checks with high-cost procedures without attached documentation."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001', 'CLM002'],
            'PatientID': ['PAT001', 'PAT002'],
            'ICD10': ['Z51.11', 'Z51.11'],
            'ProcCode': ['J9355', '99213'],  # First claim has high-cost procedure
            'Provider': ['Dr. Test', 'Dr. Test'],
            'DocStatus': ['Complete', 'Complete'],  # Not "Attached"
            'ServiceDate': ['2024-01-15', '2024-01-16']
        })
        
        result_df = apply_checks(df)
        
        # Check first claim has high-cost procedure issue
        assert 'High-cost procedure requires attached documentation' in result_df.iloc[0]['Issues']
        
        # Check second claim has no issues
        assert result_df.iloc[1]['Issues'] == []
    
    def test_apply_checks_multiple_issues(self):
        """Test apply_checks with claims having multiple issues."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001'],
            'PatientID': ['PAT001'],
            'ICD10': ['I50.9'],  # High-audit-risk diagnosis
            'ProcCode': ['J9355'],  # High-cost procedure
            'Provider': ['Dr. Test'],
            'DocStatus': [''],  # Missing documentation
            'ServiceDate': ['2024-01-15']
        })
        
        result_df = apply_checks(df)
        
        issues = result_df.iloc[0]['Issues']
        assert len(issues) == 3
        assert 'Missing documentation' in issues
        assert 'High-audit-risk diagnosis' in issues
        assert 'High-cost procedure requires attached documentation' in issues
    
    def test_apply_checks_preserves_original_dataframe(self):
        """Test that apply_checks doesn't modify the original DataFrame."""
        original_df = pd.DataFrame({
            'ClaimID': ['CLM001'],
            'PatientID': ['PAT001'],
            'ICD10': ['Z51.11'],
            'ProcCode': ['99213'],
            'Provider': ['Dr. Test'],
            'DocStatus': ['Complete'],
            'ServiceDate': ['2024-01-15']
        })
        
        original_columns = list(original_df.columns)
        
        result_df = apply_checks(original_df)
        
        # Check that original DataFrame is unchanged
        assert list(original_df.columns) == original_columns
        assert 'Issues' not in original_df.columns


class TestCleanedCsvBytes:
    """Test the cleaned_csv_bytes function."""
    
    def test_cleaned_csv_bytes_empty_dataframe(self):
        """Test that cleaned_csv_bytes raises ValueError for empty DataFrame."""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="DataFrame cannot be empty"):
            cleaned_csv_bytes(empty_df)
    
    def test_cleaned_csv_bytes_basic_dataframe(self):
        """Test cleaned_csv_bytes with a basic DataFrame."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001', 'CLM002'],
            'PatientID': ['PAT001', 'PAT002'],
            'ICD10': ['Z51.11', 'E11.9'],
            'ProcCode': ['99213', '99214'],
            'Provider': ['Dr. Test', 'Dr. Test'],
            'DocStatus': ['Complete', 'Complete'],
            'ServiceDate': ['2024-01-15', '2024-01-16']
        })
        
        csv_bytes = cleaned_csv_bytes(df)
        
        # Check that result is bytes
        assert isinstance(csv_bytes, bytes)
        
        # Check that CSV content is correct
        csv_string = csv_bytes.decode('utf-8')
        lines = csv_string.strip().split('\n')
        
        # Check header
        assert lines[0] == 'ClaimID,PatientID,ICD10,ProcCode,Provider,DocStatus,ServiceDate'
        
        # Check data rows
        assert lines[1] == 'CLM001,PAT001,Z51.11,99213,Dr. Test,Complete,2024-01-15'
        assert lines[2] == 'CLM002,PAT002,E11.9,99214,Dr. Test,Complete,2024-01-16'
    
    def test_cleaned_csv_bytes_with_issues_column(self):
        """Test cleaned_csv_bytes with DataFrame containing Issues column."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001'],
            'PatientID': ['PAT001'],
            'ICD10': ['Z51.11'],
            'ProcCode': ['99213'],
            'Provider': ['Dr. Test'],
            'DocStatus': ['Complete'],
            'ServiceDate': ['2024-01-15'],
            'Issues': [['Missing documentation']]
        })
        
        csv_bytes = cleaned_csv_bytes(df)
        
        # Check that result is bytes
        assert isinstance(csv_bytes, bytes)
        
        # Check that CSV content includes Issues column
        csv_string = csv_bytes.decode('utf-8')
        lines = csv_string.strip().split('\n')
        
        # Check header includes Issues
        assert 'Issues' in lines[0]
        
        # Check data row includes issues
        assert 'Missing documentation' in lines[1]
    
    def test_cleaned_csv_bytes_with_special_characters(self):
        """Test cleaned_csv_bytes with special characters in data."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001'],
            'PatientID': ['PAT001'],
            'ICD10': ['Z51.11'],
            'ProcCode': ['99213'],
            'Provider': ['Dr. Test, M.D.'],
            'DocStatus': ['Complete'],
            'ServiceDate': ['2024-01-15']
        })
        
        csv_bytes = cleaned_csv_bytes(df)
        
        # Check that result is bytes
        assert isinstance(csv_bytes, bytes)
        
        # Check that CSV content handles special characters correctly
        csv_string = csv_bytes.decode('utf-8')
        lines = csv_string.strip().split('\n')
        
        # Check that comma in provider name is handled correctly
        assert 'Dr. Test, M.D.' in lines[1]
    
    def test_cleaned_csv_bytes_utf8_encoding(self):
        """Test that cleaned_csv_bytes properly handles UTF-8 encoding."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001'],
            'PatientID': ['PAT001'],
            'ICD10': ['Z51.11'],
            'ProcCode': ['99213'],
            'Provider': ['Dr. José García'],
            'DocStatus': ['Complete'],
            'ServiceDate': ['2024-01-15']
        })
        
        csv_bytes = cleaned_csv_bytes(df)
        
        # Check that result is bytes
        assert isinstance(csv_bytes, bytes)
        
        # Check that UTF-8 characters are properly encoded
        csv_string = csv_bytes.decode('utf-8')
        assert 'Dr. José García' in csv_string
    
    def test_cleaned_csv_bytes_no_index(self):
        """Test that cleaned_csv_bytes doesn't include DataFrame index."""
        df = pd.DataFrame({
            'ClaimID': ['CLM001'],
            'PatientID': ['PAT001'],
            'ICD10': ['Z51.11'],
            'ProcCode': ['99213'],
            'Provider': ['Dr. Test'],
            'DocStatus': ['Complete'],
            'ServiceDate': ['2024-01-15']
        })
        
        # Set a custom index
        df.index = [999]
        
        csv_bytes = cleaned_csv_bytes(df)
        csv_string = csv_bytes.decode('utf-8')
        
        # Check that custom index is not included in CSV
        assert '999' not in csv_string
        assert csv_string.startswith('ClaimID,PatientID,ICD10,ProcCode,Provider,DocStatus,ServiceDate')


if __name__ == "__main__":
    pytest.main([__file__])
