#!/usr/bin/env python3
"""
Analyze the compliance rules logic to understand what should trigger.
"""

def analyze_compliance_rules():
    """Analyze what rules should trigger for each test case."""
    
    print("🧪 Analyzing Compliance Rules Logic")
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
            }
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
            }
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
            }
        }
    ]
    
    print("🔍 Rule Analysis:")
    print("-" * 30)
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        data = case['data']
        
        issues = []
        
        # Rule 1: Missing documentation
        if not data.get("DocStatus") or str(data.get("DocStatus", "")).strip() == "":
            issues.append("Missing documentation")
            print(f"  ✅ Rule 1 triggered: Missing documentation")
        else:
            print(f"  ❌ Rule 1 NOT triggered: DocStatus = '{data.get('DocStatus')}'")
        
        # Rule 2: Mismatched documentation
        if data.get("DocStatus") == "Complete" and data.get("ProcCode") in ["J9355", "J1940"]:
            issues.append("Mismatched documentation")
            print(f"  ✅ Rule 2 triggered: Mismatched documentation")
        else:
            print(f"  ❌ Rule 2 NOT triggered: DocStatus='{data.get('DocStatus')}', ProcCode='{data.get('ProcCode')}'")
        
        # Rule 3: High-audit-risk diagnosis codes
        icd10 = str(data.get("ICD10", ""))
        if icd10.startswith("I50") or icd10.startswith("C50"):
            issues.append("High-audit-risk diagnosis")
            print(f"  ✅ Rule 3 triggered: High-audit-risk diagnosis")
        else:
            print(f"  ❌ Rule 3 NOT triggered: ICD10 = '{icd10}'")
        
        # Rule 4: High-cost procedure requires attached documentation
        proc_code = str(data.get("ProcCode", ""))
        doc_status = str(data.get("DocStatus", ""))
        if proc_code in ["J9355", "J1940"] and doc_status != "Attached":
            issues.append("High-cost procedure requires attached documentation")
            print(f"  ✅ Rule 4 triggered: High-cost procedure requires attached documentation")
        else:
            print(f"  ❌ Rule 4 NOT triggered: ProcCode='{proc_code}', DocStatus='{doc_status}'")
        
        print(f"  📋 Total issues: {issues}")
        print(f"  📊 Number of issues: {len(issues)}")
    
    print("\n🎉 Rule analysis complete!")
    print("=" * 50)

if __name__ == "__main__":
    analyze_compliance_rules()
