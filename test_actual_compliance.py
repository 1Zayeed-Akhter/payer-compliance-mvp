#!/usr/bin/env python3
"""
Test script to actually run the compliance checking functions and see what rules are triggered.
"""

import pandas as pd
from scrub import apply_checks

def test_actual_compliance():
    """Test the actual compliance checking functions."""
    
    print("🧪 Testing Actual Compliance Checking Functions")
    print("=" * 60)
    
    # Load the test CSV
    df = pd.read_csv('test_claims.csv')
    print(f"📊 Loaded {len(df)} test claims")
    print()
    
    # Apply actual compliance checks
    df_with_issues = apply_checks(df)
    
    print("🔍 Actual Compliance Check Results:")
    print("-" * 50)
    
    for i, (_, row) in enumerate(df_with_issues.iterrows(), 1):
        claim_id = row['ClaimID']
        provider = row['Provider']
        issues = row['Issues']
        
        print(f"Row {i}: {claim_id} - {provider}")
        print(f"  Issues found: {issues}")
        print(f"  Number of issues: {len(issues)}")
        print()
    
    # Summary
    total_claims = len(df_with_issues)
    claims_with_issues = len(df_with_issues[df_with_issues['Issues'].apply(lambda x: len(x) > 0)])
    clean_claims = total_claims - claims_with_issues
    
    print("📊 Summary:")
    print(f"  Total Claims: {total_claims}")
    print(f"  Claims with Issues: {claims_with_issues}")
    print(f"  Clean Claims: {clean_claims}")
    print()
    
    # Check specific cases
    print("🎯 Specific Rule Verification:")
    print("-" * 30)
    
    # Dr. Chen (Row 2) - should have 2 issues
    chen_row = df_with_issues.iloc[1]
    chen_issues = chen_row['Issues']
    print(f"Dr. Chen (Row 2): {chen_issues}")
    print(f"  Expected: ['Mismatched documentation', 'High-cost procedure requires attached documentation']")
    print(f"  Actual: {chen_issues}")
    print(f"  Match: {chen_issues == ['Mismatched documentation', 'High-cost procedure requires attached documentation']}")
    print()
    
    # Dr. Wilson (Row 4) - should have 2 issues
    wilson_row = df_with_issues.iloc[3]
    wilson_issues = wilson_row['Issues']
    print(f"Dr. Wilson (Row 4): {wilson_issues}")
    print(f"  Expected: ['Mismatched documentation', 'High-cost procedure requires attached documentation']")
    print(f"  Actual: {wilson_issues}")
    print(f"  Match: {wilson_issues == ['Mismatched documentation', 'High-cost procedure requires attached documentation']}")
    print()
    
    print("🎉 Actual compliance checking test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_actual_compliance()
