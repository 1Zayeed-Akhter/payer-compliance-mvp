#!/usr/bin/env python3
"""
Simple test to verify the compliance rules are working correctly.
"""

def check_claim_simple(row):
    """
    Simplified version of check_claim function for testing.
    """
    issues = []
    
    # Rule 1: Missing documentation
    if not row.get("DocStatus") or str(row.get("DocStatus", "")).strip() == "":
        issues.append("Missing documentation")
    
    # Rule 2: Mismatched documentation
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

def test_rules():
    """Test the compliance rules."""
    
    print("🧪 Testing Compliance Rules (Simple Version)")
    print("=" * 50)
    
    # Test the specific cases we're concerned about
    test_cases = [
        {
            'name': 'Dr. Michael Chen (Row 2)',
            'data': {
                'ClaimID': 'CLM0002',
                'PatientID': 'PAT0002',
                'ICD10': 'E11.9',
                'ProcCode': 'J9355',
                'Provider': 'Dr. Michael Chen - Orthopedics',
                'DocStatus': 'Complete',
                'ServiceDate': '2025-01-16'
            },
            'expected': ['Mismatched documentation', 'High-cost procedure requires attached documentation']
        },
        {
            'name': 'Dr. James Wilson (Row 4)',
            'data': {
                'ClaimID': 'CLM0004',
                'PatientID': 'PAT0004',
                'ICD10': 'L70.9',
                'ProcCode': 'J1940',
                'Provider': 'Dr. James Wilson - Dermatology',
                'DocStatus': 'Complete',
                'ServiceDate': '2025-01-18'
            },
            'expected': ['Mismatched documentation', 'High-cost procedure requires attached documentation']
        }
    ]
    
    print("🔍 Testing specific cases:")
    print("-" * 30)
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        actual_issues = check_claim_simple(case['data'])
        expected_issues = case['expected']
        
        print(f"  Expected: {expected_issues}")
        print(f"  Actual:   {actual_issues}")
        print(f"  Match:    {actual_issues == expected_issues}")
        print(f"  Count:    {len(actual_issues)} issues")
        
        if actual_issues == expected_issues:
            print(f"  ✅ CORRECT!")
        else:
            print(f"  ❌ MISMATCH!")
    
    print("\n🎉 Simple compliance rules test complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_rules()
