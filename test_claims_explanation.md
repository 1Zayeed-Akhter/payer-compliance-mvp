# Test Claims CSV - Compliance Rule Triggers

This document explains how each row in `test_claims.csv` is designed to trigger specific compliance rules.

## File: test_claims.csv

### Row 1: Missing Documentation
```
CLM0001,PAT0001,Z51.11,99213,Dr. Sarah Johnson - Cardiology,,2025-01-15
```
**Trigger**: Missing documentation
- **DocStatus**: Empty (blank)
- **Expected Issue**: "Missing documentation"
- **Rule**: When DocStatus is empty, null, or whitespace-only

### Row 2: Mismatched Documentation
```
CLM0002,PAT0002,E11.9,99214,Dr. Michael Chen - Orthopedics,Complete,2025-01-16
```
**Trigger**: Mismatched documentation
- **DocStatus**: "Complete" (but not "Attached")
- **Expected Issue**: "Mismatched documentation" (if rule is implemented)
- **Rule**: Documentation status doesn't match procedure requirements

### Row 3: High-Audit-Risk Diagnosis
```
CLM0003,PAT0003,I50.9,99215,Dr. Emily Rodriguez - Internal Medicine,Complete,2025-01-17
```
**Trigger**: High-audit-risk diagnosis
- **ICD10**: "I50.9" (starts with "I50" - heart failure)
- **Expected Issue**: "High-audit-risk diagnosis"
- **Rule**: ICD-10 codes starting with "I50" or "C50" are high-audit-risk

### Row 4: High-Cost Procedure with Missing Attached Documentation
```
CLM0004,PAT0004,L70.9,J9355,Dr. James Wilson - Dermatology,Complete,2025-01-18
```
**Trigger**: High-cost procedure requires attached documentation
- **ProcCode**: "J9355" (high-cost procedure)
- **DocStatus**: "Complete" (but not "Attached")
- **Expected Issue**: "High-cost procedure requires attached documentation"
- **Rule**: Procedures J9355 and J1940 require "Attached" documentation status

### Row 5: Multiple Issues (High-Risk Diagnosis + Missing Documentation)
```
CLM0005,PAT0005,C50.911,J1940,Dr. Lisa Thompson - Pediatrics,,2025-01-19
```
**Trigger**: Multiple compliance issues
- **ICD10**: "C50.911" (starts with "C50" - breast cancer, high-audit-risk)
- **ProcCode**: "J1940" (high-cost procedure)
- **DocStatus**: Empty (missing documentation)
- **Expected Issues**: 
  - "High-audit-risk diagnosis"
  - "Missing documentation"
  - "High-cost procedure requires attached documentation"

### Row 6: Clean Row (Control)
```
CLM0006,PAT0006,Z51.11,99213,Dr. Robert Smith - Family Medicine,Complete,2025-01-20
```
**Trigger**: No issues (control case)
- **ICD10**: "Z51.11" (normal diagnosis code)
- **ProcCode**: "99213" (standard procedure code)
- **DocStatus**: "Complete" (appropriate documentation)
- **Expected Issues**: None (clean claim)

## Compliance Rules Tested

1. **Missing Documentation**: Empty or null DocStatus
2. **Mismatched Documentation**: DocStatus doesn't match procedure requirements
3. **High-Audit-Risk Diagnosis**: ICD-10 codes starting with "I50" or "C50"
4. **High-Cost Procedure Documentation**: J9355 and J1940 require "Attached" status
5. **Multiple Issues**: Combination of multiple compliance problems
6. **Clean Claims**: Claims that pass all compliance checks

## Usage

Run the test script to verify compliance rule triggers:
```bash
python test_compliance_rules.py
```

This will show which rules are triggered for each row and verify the expected behavior.
