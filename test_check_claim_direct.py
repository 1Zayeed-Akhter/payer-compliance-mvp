#!/usr/bin/env python3
"""
Test script to directly test the check_claim function without pandas.
"""

import sys
sys.path.append('.')
from scrub import check_claim

def test_check_claim_direct():
    """Test the check_claim function directly."""
    
    print("🧪 Testing check_claim Function Directly")
    print("=" * 50)
    
    # Test data from our CSV
    test_cases = [
        {
            'name': 'Dr. Sarah Johnson (Row 1)',
            'data': {
                'ClaimID': 'CLM0001',
                'PatientID': 'PAT0001',
                'ICD10': 'Z51.11',
                'ProcCode': '99213',
                'Provider': 'Dr. Sarah Johnson - Cardiology',
                'DocStatus': '',
                'ServiceDate': '2025-01-15'
            },
            'expected': ['Missing documentation']
        },
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
            'name': 'Dr. Emily Rodriguez (Row 3)',
            'data': {
                'ClaimID': 'CLM0003',
                'PatientID': 'PAT0003',
                'ICD10': 'I50.9',
                'ProcCode': '99215',
                'Provider': 'Dr. Emily Rodriguez - Internal Medicine',
                'DocStatus': 'Complete',
                'ServiceDate': '2025-01-17'
            },
            'expected': ['High-audit-risk diagnosis']
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
        },
        {
            'name': 'Dr. Lisa Thompson (Row 5)',
            'data': {
                'ClaimID': 'CLM0005',
                'PatientID': 'PAT0005',
                'ICD10': 'C50.911',
                'ProcCode': '99213',
                'Provider': 'Dr. Lisa Thompson - Pediatrics',
                'DocStatus': '',
                'ServiceDate': '2025-01-19'
            },
            'expected': ['Missing documentation', 'High-audit-risk diagnosis']
        },
        {
            'name': 'Dr. Robert Smith (Row 6)',
            'data': {
                'ClaimID': 'CLM0006',
                'PatientID': 'PAT0006',
                'ICD10': 'Z51.11',
                'ProcCode': '99213',
                'Provider': 'Dr. Robert Smith - Family Medicine',
                'DocStatus': 'Complete',
                'ServiceDate': '2025-01-20'
            },
            'expected': []
        }
    ]
    
    print("🔍 Testing each case:")
    print("-" * 30)
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        print(f"  Data: {case['data']}")
        
        try:
            actual_issues = check_claim(case['data'])
            print(f"  Expected: {case['expected']}")
            print(f"  Actual:   {actual_issues}")
            print(f"  Match:    {actual_issues == case['expected']}")
            
            if actual_issues != case['expected']:
                print(f"  ❌ MISMATCH!")
            else:
                print(f"  ✅ CORRECT!")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    print("\n🎉 Direct check_claim function test complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_check_claim_direct()
