#!/usr/bin/env python3
"""
Simple verification script for test_claims.csv without external dependencies.
"""

def verify_test_claims():
    """Verify that test_claims.csv has the expected structure and content."""
    
    print("🧪 Verifying test_claims.csv Structure")
    print("=" * 50)
    
    try:
        with open('test_claims.csv', 'r') as f:
            lines = f.readlines()
        
        print(f"📊 CSV file loaded: {len(lines)} lines")
        print()
        
        # Check header
        header = lines[0].strip()
        expected_columns = ['ClaimID', 'PatientID', 'ICD10', 'ProcCode', 'Provider', 'DocStatus', 'ServiceDate']
        actual_columns = header.split(',')
        
        print("📋 Header verification:")
        print(f"  Expected: {expected_columns}")
        print(f"  Actual:   {actual_columns}")
        
        if actual_columns == expected_columns:
            print("  ✅ Header matches expected columns")
        else:
            print("  ❌ Header does not match expected columns")
        print()
        
        # Check each data row
        print("🔍 Data rows verification:")
        print("-" * 30)
        
        for i, line in enumerate(lines[1:], 1):
            parts = line.strip().split(',')
            if len(parts) == 7:
                claim_id, patient_id, icd10, proc_code, provider, doc_status, service_date = parts
                
                print(f"Row {i}: {claim_id}")
                print(f"  Patient: {patient_id}")
                print(f"  ICD10: {icd10}")
                print(f"  Procedure: {proc_code}")
                print(f"  Provider: {provider}")
                print(f"  DocStatus: '{doc_status}'")
                print(f"  ServiceDate: {service_date}")
                
                # Check for expected triggers
                triggers = []
                if doc_status == '':
                    triggers.append("Missing documentation")
                if icd10.startswith('I50') or icd10.startswith('C50'):
                    triggers.append("High-audit-risk diagnosis")
                if proc_code in ['J9355', 'J1940'] and doc_status != 'Attached':
                    triggers.append("High-cost procedure requires attached documentation")
                if not triggers and doc_status == 'Complete' and not icd10.startswith(('I50', 'C50')):
                    triggers.append("Clean (no issues)")
                
                if triggers:
                    print(f"  Expected triggers: {', '.join(triggers)}")
                else:
                    print(f"  Expected triggers: Unknown")
                print()
            else:
                print(f"Row {i}: ❌ Invalid format - {len(parts)} parts instead of 7")
                print()
        
        print("✅ CSV structure verification complete!")
        print("=" * 50)
        
    except FileNotFoundError:
        print("❌ test_claims.csv file not found")
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    verify_test_claims()
