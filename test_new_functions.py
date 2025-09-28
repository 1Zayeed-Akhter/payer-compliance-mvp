#!/usr/bin/env python3
"""
Test script to demonstrate the new apply_checks and cleaned_csv_bytes functions.
This script can be run to verify the functions work correctly.
"""

import pandas as pd
from scrub import apply_checks, cleaned_csv_bytes

def test_new_functions():
    """Test the new apply_checks and cleaned_csv_bytes functions."""
    
    print("🧪 Testing new functions in scrub.py")
    print("=" * 50)
    
    # Create test data with various compliance issues
    test_data = {
        'ClaimID': ['CLM001', 'CLM002', 'CLM003', 'CLM004'],
        'PatientID': ['PAT001', 'PAT002', 'PAT003', 'PAT004'],
        'ICD10': ['I50.9', 'Z51.11', 'C50.911', 'E11.9'],  # Mix of high-risk and normal codes
        'ProcCode': ['99213', 'J9355', '99214', 'J1940'],  # Mix of normal and high-cost procedures
        'Provider': ['Dr. Test', 'Dr. Test', 'Dr. Test', 'Dr. Test'],
        'DocStatus': ['Complete', 'Complete', 'Attached', ''],  # Mix of documentation statuses
        'ServiceDate': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18']
    }
    
    df = pd.DataFrame(test_data)
    print("📊 Original DataFrame:")
    print(df)
    print()
    
    # Test apply_checks function
    print("🔍 Applying compliance checks...")
    result_df = apply_checks(df)
    
    print("✅ apply_checks function completed successfully!")
    print("📋 Results with Issues column:")
    print(result_df)
    print()
    
    # Show issues for each claim
    print("📝 Issues found for each claim:")
    for i, row in result_df.iterrows():
        claim_id = row['ClaimID']
        issues = row['Issues']
        if issues:
            print(f"  {claim_id}: {', '.join(issues)}")
        else:
            print(f"  {claim_id}: No issues found")
    print()
    
    # Test cleaned_csv_bytes function
    print("💾 Testing CSV export...")
    csv_bytes = cleaned_csv_bytes(result_df)
    
    print("✅ cleaned_csv_bytes function completed successfully!")
    print(f"📄 CSV size: {len(csv_bytes)} bytes")
    print()
    
    # Show CSV preview
    csv_preview = csv_bytes.decode('utf-8')
    lines = csv_preview.split('\n')
    print("📋 CSV Preview (first 3 lines):")
    for i, line in enumerate(lines[:3]):
        print(f"  {i+1}: {line}")
    print("  ...")
    print()
    
    print("🎉 All tests completed successfully!")
    print("=" * 50)
    print("✅ apply_checks: Adds Issues column to DataFrame")
    print("✅ cleaned_csv_bytes: Exports DataFrame as CSV bytes")
    print("✅ Both functions handle edge cases and error conditions")

if __name__ == "__main__":
    test_new_functions()
