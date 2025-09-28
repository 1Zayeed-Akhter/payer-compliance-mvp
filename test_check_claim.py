#!/usr/bin/env python3
"""
Simple test script for check_claim function without pandas dependency.
"""

import pandas as pd

def check_claim(row):
    """
    Check a single claim row for specific compliance issues.
    """
    issues = []

    # Normalize all fields
    doc_status = str(row.get("DocStatus", "")).strip()
    proc_code = str(row.get("ProcCode", "")).strip().upper()  # uppercase just in case
    icd10 = str(row.get("ICD10", "")).strip().upper()

    # Rule 1: Missing documentation
    if doc_status == "":
        issues.append("Missing documentation")

    # Rule 2: Mismatched documentation
    high_risk_codes = {"J9355", "J1940", "99215"}
    if doc_status == "Complete" and proc_code in high_risk_codes:
        issues.append("Mismatched documentation")

    # Rule 3: High-audit-risk diagnosis codes
    if icd10.startswith("I50") or icd10.startswith("C50"):
        issues.append("High-audit-risk diagnosis")

    # Rule 4: High-cost procedure requires attached documentation
    if proc_code in {"J9355", "J1940"} and doc_status != "Attached":
        issues.append("High-cost procedure requires attached documentation")

    return issues


def test_check_claim():
    """Test the check_claim function."""
    
    print("Testing check_claim function...")
    
    # Test 1: Missing documentation
    print("\n1. Testing missing documentation...")
    row1 = {"DocStatus": ""}
    result1 = check_claim(row1)
    print(f"   Input: {row1}")
    print(f"   Result: {result1}")
    print(f"   Expected: ['Missing documentation']")
    print(f"   Pass: {'Missing documentation' in result1}")
    
    # Test 2: High-audit-risk diagnosis I50
    print("\n2. Testing high-audit-risk diagnosis I50...")
    row2 = {"ICD10": "I50.9", "DocStatus": "Complete"}
    result2 = check_claim(row2)
    print(f"   Input: {row2}")
    print(f"   Result: {result2}")
    print(f"   Expected: ['High-audit-risk diagnosis']")
    print(f"   Pass: {'High-audit-risk diagnosis' in result2}")
    
    # Test 3: High-audit-risk diagnosis C50
    print("\n3. Testing high-audit-risk diagnosis C50...")
    row3 = {"ICD10": "C50.911", "DocStatus": "Complete"}
    result3 = check_claim(row3)
    print(f"   Input: {row3}")
    print(f"   Result: {result3}")
    print(f"   Expected: ['High-audit-risk diagnosis']")
    print(f"   Pass: {'High-audit-risk diagnosis' in result3}")
    
    # Test 4: High-cost procedure J9355 without attached doc
    print("\n4. Testing high-cost procedure J9355 without attached doc...")
    row4 = {"ProcCode": "J9355", "DocStatus": "Complete"}
    result4 = check_claim(row4)
    print(f"   Input: {row4}")
    print(f"   Result: {result4}")
    print(f"   Expected: ['High-cost procedure requires attached documentation']")
    print(f"   Pass: {'High-cost procedure requires attached documentation' in result4}")
    
    # Test 5: High-cost procedure J1940 without attached doc
    print("\n5. Testing high-cost procedure J1940 without attached doc...")
    row5 = {"ProcCode": "J1940", "DocStatus": "Pending"}
    result5 = check_claim(row5)
    print(f"   Input: {row5}")
    print(f"   Result: {result5}")
    print(f"   Expected: ['High-cost procedure requires attached documentation']")
    print(f"   Pass: {'High-cost procedure requires attached documentation' in result5}")
    
    # Test 6: High-cost procedure with attached doc (should pass)
    print("\n6. Testing high-cost procedure J9355 with attached doc...")
    row6 = {"ProcCode": "J9355", "DocStatus": "Attached"}
    result6 = check_claim(row6)
    print(f"   Input: {row6}")
    print(f"   Result: {result6}")
    print(f"   Expected: []")
    print(f"   Pass: len(result6) == 0")
    
    # Test 7: Multiple issues
    print("\n7. Testing multiple issues...")
    row7 = {"ICD10": "I50.9", "ProcCode": "J9355", "DocStatus": ""}
    result7 = check_claim(row7)
    print(f"   Input: {row7}")
    print(f"   Result: {result7}")
    print(f"   Expected: 3 issues")
    print(f"   Pass: len(result7) == 3")
    
    # Test 8: Clean claim
    print("\n8. Testing clean claim...")
    row8 = {"ICD10": "Z51.11", "ProcCode": "99213", "DocStatus": "Complete"}
    result8 = check_claim(row8)
    print(f"   Input: {row8}")
    print(f"   Result: {result8}")
    print(f"   Expected: []")
    print(f"   Pass: len(result8) == 0")


if __name__ == "__main__":
    test_check_claim()
