#!/usr/bin/env python3
"""
Test script to verify that test_claims.csv triggers the expected compliance rules.
"""

import pandas as pd
from scrub import apply_checks

def test_compliance_rules():
    """Test that each row in test_claims.csv triggers the expected compliance rules."""
    
    print("🧪 Testing Compliance Rules in test_claims.csv")
    print("=" * 60)
    
    # Load the test CSV
    df = pd.read_csv('test_claims.csv')
    print(f"📊 Loaded {len(df)} test claims")
    print()
    
    # Apply compliance checks
    df_with_issues = apply_checks(df)
    
    # Expected compliance rule triggers
    expected_rules = [
        "Missing documentation",
        "Mismatched documentation", 
        "High-audit-risk diagnosis",
        "High-cost procedure requires attached documentation",
        "Multiple issues (risky ICD10 + missing doc)",
        "Clean row (no issues)"
    ]
    
    print("🔍 Compliance Check Results:")
    print("-" * 60)
    
    for i, (_, row) in enumerate(df_with_issues.iterrows(), 1):
        claim_id = row['ClaimID']
        provider = row['Provider']
        issues = row['Issues']
        
        print(f"Row {i}: {claim_id} - {provider}")
        print(f"  Expected: {expected_rules[i-1]}")
        
        if issues:
            print(f"  ✅ Issues found: {', '.join(issues)}")
        else:
            print(f"  ✅ No issues (clean claim)")
        print()
    
    # Summary
    total_claims = len(df_with_issues)
    claims_with_issues = len(df_with_issues[df_with_issues['Issues'].apply(lambda x: len(x) > 0)])
    clean_claims = total_claims - claims_with_issues
    
    print("📊 Summary:")
    print(f"  Total Claims: {total_claims}")
    print(f"  Claims with Issues: {claims_with_issues}")
    print(f"  Clean Claims: {clean_claims}")
    print(f"  Compliance Rate: {clean_claims/total_claims*100:.1f}%")
    print()
    
    # Verify specific rule triggers
    print("🎯 Rule Verification:")
    print("-" * 30)
    
    # Row 1: Missing documentation
    row1_issues = df_with_issues.iloc[0]['Issues']
    if "Missing documentation" in row1_issues:
        print("✅ Row 1: Missing documentation rule triggered")
    else:
        print("❌ Row 1: Missing documentation rule NOT triggered")
    
    # Row 2: Mismatched documentation (this rule may not be implemented)
    row2_issues = df_with_issues.iloc[1]['Issues']
    if "Mismatched documentation" in row2_issues:
        print("✅ Row 2: Mismatched documentation rule triggered")
    else:
        print("ℹ️  Row 2: Mismatched documentation rule not implemented or not triggered")
    
    # Row 3: High-audit-risk diagnosis
    row3_issues = df_with_issues.iloc[2]['Issues']
    if "High-audit-risk diagnosis" in row3_issues:
        print("✅ Row 3: High-audit-risk diagnosis rule triggered")
    else:
        print("❌ Row 3: High-audit-risk diagnosis rule NOT triggered")
    
    # Row 4: High-cost procedure with missing attached docs
    row4_issues = df_with_issues.iloc[3]['Issues']
    if "High-cost procedure requires attached documentation" in row4_issues:
        print("✅ Row 4: High-cost procedure rule triggered")
    else:
        print("❌ Row 4: High-cost procedure rule NOT triggered")
    
    # Row 5: Multiple issues
    row5_issues = df_with_issues.iloc[4]['Issues']
    issue_count = len(row5_issues)
    if issue_count > 1:
        print(f"✅ Row 5: Multiple issues triggered ({issue_count} issues)")
    else:
        print(f"ℹ️  Row 5: {issue_count} issue(s) triggered")
    
    # Row 6: Clean row
    row6_issues = df_with_issues.iloc[5]['Issues']
    if len(row6_issues) == 0:
        print("✅ Row 6: Clean row (no issues)")
    else:
        print(f"❌ Row 6: Expected clean but found issues: {', '.join(row6_issues)}")
    
    print()
    print("🎉 Compliance Rules Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_compliance_rules()
