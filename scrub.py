"""
Payer Compliance Scrub - Core compliance checking logic
Contains rules and processing functions for claims compliance validation.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import io


@dataclass
class ComplianceResult:
    """Result of compliance check for a single claim."""
    claim_id: str
    provider_name: str
    issues: List[str]
    severity: str  # "low", "medium", "high"
    original_data: Dict[str, Any]


def process_claims(df: pd.DataFrame) -> List[ComplianceResult]:
    """
    Process a dataframe of claims and return compliance results.
    
    Args:
        df: DataFrame containing claims data
        
    Returns:
        List of ComplianceResult objects
    """
    results = []
    
    for _, row in df.iterrows():
        result = check_claim_compliance(row.to_dict())
        results.append(result)
    
    return results


def check_claim_compliance(claim_data: Dict[str, Any]) -> ComplianceResult:
    """
    Check a single claim for compliance issues.
    
    Args:
        claim_data: Dictionary containing claim information
        
    Returns:
        ComplianceResult with any issues found
    """
    issues = []
    severity = "low"
    
    # Extract claim information
    claim_id = str(claim_data.get("claim_id", ""))
    provider_name = str(claim_data.get("provider_name", ""))
    
    # Run compliance checks
    issues.extend(check_required_fields(claim_data))
    issues.extend(check_procedure_codes(claim_data))
    issues.extend(check_diagnosis_codes(claim_data))
    issues.extend(check_billing_amounts(claim_data))
    issues.extend(check_npi_format(claim_data))
    issues.extend(check_date_format(claim_data))
    
    # Determine severity
    if any("CRITICAL" in issue for issue in issues):
        severity = "high"
    elif any("WARNING" in issue for issue in issues):
        severity = "medium"
    
    return ComplianceResult(
        claim_id=claim_id,
        provider_name=provider_name,
        issues=issues,
        severity=severity,
        original_data=claim_data
    )


def check_required_fields(claim_data: Dict[str, Any]) -> List[str]:
    """Check for missing required fields."""
    issues = []
    required_fields = [
        "claim_id", "provider_name", "patient_id", 
        "procedure_code", "billed_amount", "date_of_service"
    ]
    
    for field in required_fields:
        if not claim_data.get(field) or str(claim_data.get(field)).strip() == "":
            issues.append(f"CRITICAL: Missing required field '{field}'")
    
    return issues


def check_procedure_codes(claim_data: Dict[str, Any]) -> List[str]:
    """Validate procedure codes format and common issues."""
    issues = []
    procedure_code = str(claim_data.get("procedure_code", ""))
    
    if not procedure_code:
        return issues
    
    # Check for valid CPT format (5 digits)
    if not re.match(r'^\d{5}$', procedure_code):
        issues.append(f"WARNING: Invalid procedure code format '{procedure_code}' - should be 5 digits")
    
    # Check for common invalid codes
    invalid_codes = ["00000", "99999", "11111"]
    if procedure_code in invalid_codes:
        issues.append(f"CRITICAL: Invalid procedure code '{procedure_code}'")
    
    return issues


def check_diagnosis_codes(claim_data: Dict[str, Any]) -> List[str]:
    """Validate ICD-10 diagnosis codes."""
    issues = []
    diagnosis_code = str(claim_data.get("diagnosis_code", ""))
    
    if not diagnosis_code:
        return issues
    
    # Basic ICD-10 format check (letter followed by digits and optional decimal)
    if not re.match(r'^[A-Z]\d{2}(\.\d{1,4})?$', diagnosis_code):
        issues.append(f"WARNING: Invalid diagnosis code format '{diagnosis_code}' - should be ICD-10 format")
    
    # Check for placeholder codes
    placeholder_codes = ["Z00.0", "Z99.9", "A00.0"]
    if diagnosis_code in placeholder_codes:
        issues.append(f"WARNING: Placeholder diagnosis code '{diagnosis_code}' may need review")
    
    return issues


def check_billing_amounts(claim_data: Dict[str, Any]) -> List[str]:
    """Validate billing amounts for reasonableness."""
    issues = []
    billed_amount = claim_data.get("billed_amount")
    
    if billed_amount is None:
        return issues
    
    try:
        amount = float(billed_amount)
        
        # Check for negative amounts
        if amount < 0:
            issues.append(f"CRITICAL: Negative billing amount ${amount}")
        
        # Check for unreasonably high amounts
        if amount > 10000:
            issues.append(f"WARNING: Unusually high billing amount ${amount} - may need review")
        
        # Check for zero amounts
        if amount == 0:
            issues.append(f"WARNING: Zero billing amount - may indicate missing data")
            
    except (ValueError, TypeError):
        issues.append(f"CRITICAL: Invalid billing amount format '{billed_amount}'")
    
    return issues


def check_npi_format(claim_data: Dict[str, Any]) -> List[str]:
    """Validate NPI (National Provider Identifier) format."""
    issues = []
    npi = str(claim_data.get("rendering_npi", ""))
    
    if not npi:
        return issues
    
    # NPI should be 10 digits
    if not re.match(r'^\d{10}$', npi):
        issues.append(f"WARNING: Invalid NPI format '{npi}' - should be 10 digits")
    
    # Check for placeholder NPIs
    if npi.startswith("000000000") or npi == "1234567890":
        issues.append(f"WARNING: Placeholder NPI '{npi}' may need verification")
    
    return issues


def check_date_format(claim_data: Dict[str, Any]) -> List[str]:
    """Validate date formats and reasonableness."""
    issues = []
    date_str = str(claim_data.get("date_of_service", ""))
    
    if not date_str:
        return issues
    
    try:
        # Try to parse the date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Check if date is in the future
        if date_obj > datetime.now():
            issues.append(f"WARNING: Future date of service '{date_str}'")
        
        # Check if date is too far in the past (more than 2 years)
        from datetime import timedelta
        if date_obj < datetime.now() - timedelta(days=730):
            issues.append(f"WARNING: Very old date of service '{date_str}' - may be outside filing window")
            
    except ValueError:
        issues.append(f"CRITICAL: Invalid date format '{date_str}' - should be YYYY-MM-DD")
    
    return issues


def check_claim(row: Dict[str, Any]) -> List[str]:
    """
    Check a single claim row for specific compliance issues.
    
    Args:
        row: Dictionary containing claim information
        
    Returns:
        List of compliance issue messages
    """
    issues = []
    
    # Rule 1: Missing documentation
    if not row.get("DocStatus") or str(row.get("DocStatus", "")).strip() == "":
        issues.append("Missing documentation")
    
    # Rule 2: Mismatched documentation
    # High-cost procedures (J9355, J1940) require "Attached" documentation status
    # If they have "Complete" status instead, it's a mismatch
    if row.get("DocStatus") == "Complete" and row.get("ProcCode") in ["J9355", "J1940"]:
        issues.append("Mismatched documentation")
    
    # Rule 3: High-audit-risk diagnosis codes
    icd10 = str(row.get("ICD10", ""))
    if icd10.startswith("I50") or icd10.startswith("C50"):
        issues.append("High-audit-risk diagnosis")
    
    # Rule 4: High-cost procedure requires attached documentation
    proc_code = str(row.get("ProcCode", ""))
    doc_status = str(row.get("DocStatus", ""))
    if proc_code in ["J9355", "J1940"] and doc_status != "Attached":
        issues.append("High-cost procedure requires attached documentation")
    
    return issues


def get_compliance_summary(results: List[ComplianceResult]) -> Dict[str, Any]:
    """
    Generate a summary of compliance results.
    
    Args:
        results: List of ComplianceResult objects
        
    Returns:
        Dictionary with summary statistics
    """
    total_claims = len(results)
    flagged_claims = sum(1 for r in results if r.issues)
    clean_claims = total_claims - flagged_claims
    
    severity_counts = {"low": 0, "medium": 0, "high": 0}
    for result in results:
        if result.issues:
            severity_counts[result.severity] += 1
    
    return {
        "total_claims": total_claims,
        "flagged_claims": flagged_claims,
        "clean_claims": clean_claims,
        "compliance_rate": (clean_claims / total_claims * 100) if total_claims > 0 else 0,
        "severity_breakdown": severity_counts
    }


def apply_checks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply compliance checks to a DataFrame and add an Issues column.
    
    This function processes each row in the DataFrame using the check_claim function
    and adds a new 'Issues' column containing the list of compliance issues found.
    
    Args:
        df: DataFrame containing claims data with columns matching the expected format
        
    Returns:
        DataFrame with an additional 'Issues' column containing compliance issues
        
    Raises:
        ValueError: If the DataFrame is empty or missing required columns
    """
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    
    # Create a copy to avoid modifying the original DataFrame
    result_df = df.copy()
    
    # Apply compliance checks to each row
    issues_list = []
    for _, row in df.iterrows():
        issues = check_claim(row.to_dict())
        issues_list.append(issues)
    
    # Add the Issues column
    result_df['Issues'] = issues_list
    
    return result_df


def cleaned_csv_bytes(df: pd.DataFrame) -> bytes:
    """
    Export a DataFrame to CSV format as bytes.
    
    This function converts a DataFrame to CSV format and returns it as bytes,
    which is useful for downloading or streaming the data.
    
    Args:
        df: DataFrame to export to CSV
        
    Returns:
        Bytes containing the CSV data
        
    Raises:
        ValueError: If the DataFrame is empty
    """
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    
    # Create a StringIO buffer to write CSV data
    csv_buffer = io.StringIO()
    
    # Write DataFrame to CSV buffer
    df.to_csv(csv_buffer, index=False)
    
    # Get the CSV string and convert to bytes
    csv_string = csv_buffer.getvalue()
    csv_bytes = csv_string.encode('utf-8')
    
    return csv_bytes
