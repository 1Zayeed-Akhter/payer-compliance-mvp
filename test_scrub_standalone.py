#!/usr/bin/env python3
"""
Standalone test for check_claim function logic.
"""

def check_claim(row):
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
    
    # Rule 2: Mismatched documentation (simplified check - could be expanded)
    # This is a basic implementation - in practice, you'd have more sophisticated logic
    # to determine if documentation supports the billed codes
    if row.get("DocStatus") == "Complete" and row.get("ProcCode") in ["J9355", "J1940"]:
        # This is a simplified example - real implementation would check if docs support the procedure
        pass  # Could add more sophisticated matching logic here
    
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


def run_tests():
    """Run comprehensive tests for check_claim function."""
    
    print("Testing check_claim function...")
    
    # Test cases based on the pytest tests
    test_cases = [
        # Test 1: Clean claim
        {
            "name": "Clean claim no issues",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "Z51.11",
                "ProcCode": "99213",
                "Provider": "Dr. Test",
                "DocStatus": "Complete",
                "ServiceDate": "2024-01-15"
            },
            "expected": []
        },
        
        # Test 2: Missing documentation
        {
            "name": "Missing documentation",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "Z51.11",
                "ProcCode": "99213",
                "Provider": "Dr. Test",
                "DocStatus": "",
                "ServiceDate": "2024-01-15"
            },
            "expected": ["Missing documentation"]
        },
        
        # Test 3: Missing documentation (None)
        {
            "name": "Missing documentation (None)",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "Z51.11",
                "ProcCode": "99213",
                "Provider": "Dr. Test",
                "DocStatus": None,
                "ServiceDate": "2024-01-15"
            },
            "expected": ["Missing documentation"]
        },
        
        # Test 4: Missing documentation (whitespace)
        {
            "name": "Missing documentation (whitespace)",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "Z51.11",
                "ProcCode": "99213",
                "Provider": "Dr. Test",
                "DocStatus": "   ",
                "ServiceDate": "2024-01-15"
            },
            "expected": ["Missing documentation"]
        },
        
        # Test 5: High-audit-risk diagnosis I50
        {
            "name": "High-audit-risk diagnosis I50",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "I50.9",
                "ProcCode": "99213",
                "Provider": "Dr. Test",
                "DocStatus": "Complete",
                "ServiceDate": "2024-01-15"
            },
            "expected": ["High-audit-risk diagnosis"]
        },
        
        # Test 6: High-audit-risk diagnosis C50
        {
            "name": "High-audit-risk diagnosis C50",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "C50.911",
                "ProcCode": "99213",
                "Provider": "Dr. Test",
                "DocStatus": "Complete",
                "ServiceDate": "2024-01-15"
            },
            "expected": ["High-audit-risk diagnosis"]
        },
        
        # Test 7: High-cost procedure J9355 without attached doc
        {
            "name": "High-cost procedure J9355 without attached doc",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "Z51.11",
                "ProcCode": "J9355",
                "Provider": "Dr. Test",
                "DocStatus": "Complete",
                "ServiceDate": "2024-01-15"
            },
            "expected": ["High-cost procedure requires attached documentation"]
        },
        
        # Test 8: High-cost procedure J1940 without attached doc
        {
            "name": "High-cost procedure J1940 without attached doc",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "Z51.11",
                "ProcCode": "J1940",
                "Provider": "Dr. Test",
                "DocStatus": "Pending",
                "ServiceDate": "2024-01-15"
            },
            "expected": ["High-cost procedure requires attached documentation"]
        },
        
        # Test 9: High-cost procedure J9355 with attached doc
        {
            "name": "High-cost procedure J9355 with attached doc",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "Z51.11",
                "ProcCode": "J9355",
                "Provider": "Dr. Test",
                "DocStatus": "Attached",
                "ServiceDate": "2024-01-15"
            },
            "expected": []
        },
        
        # Test 10: High-cost procedure J1940 with attached doc
        {
            "name": "High-cost procedure J1940 with attached doc",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "Z51.11",
                "ProcCode": "J1940",
                "Provider": "Dr. Test",
                "DocStatus": "Attached",
                "ServiceDate": "2024-01-15"
            },
            "expected": []
        },
        
        # Test 11: Multiple issues
        {
            "name": "Multiple issues combined",
            "input": {
                "ClaimID": "CLM001",
                "PatientID": "PAT001",
                "ICD10": "I50.9",
                "ProcCode": "J9355",
                "Provider": "Dr. Test",
                "DocStatus": "",
                "ServiceDate": "2024-01-15"
            },
            "expected": ["Missing documentation", "High-audit-risk diagnosis", "High-cost procedure requires attached documentation"]
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        result = check_claim(test_case["input"])
        passed = result == test_case["expected"]
        all_passed = all_passed and passed
        
        print(f"\nTest {i}: {test_case['name']}")
        print(f"  Input: {test_case['input']}")
        print(f"  Result: {result}")
        print(f"  Expected: {test_case['expected']}")
        print(f"  Pass: {passed}")
        
        if not passed:
            print(f"  ❌ FAILED")
        else:
            print(f"  ✅ PASSED")
    
    print(f"\n{'='*50}")
    print(f"Overall result: {'ALL TESTS PASSED ✅' if all_passed else 'SOME TESTS FAILED ❌'}")
    print(f"{'='*50}")
    
    return all_passed


if __name__ == "__main__":
    run_tests()
