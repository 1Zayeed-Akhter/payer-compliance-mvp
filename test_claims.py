# test_claims.py — generate a test_claims.csv with all rules triggered

csv_content = """ClaimID,PatientID,ICD10,ProcCode,Provider,DocStatus,ServiceDate
CLM0001,PAT0001,Z51.11,99213,Dr. Sarah Johnson - Cardiology,,2025-01-15
CLM0002,PAT0002,E11.9,J9355,Dr. Michael Chen - Orthopedics,Complete,2025-01-16
CLM0003,PAT0003,I50.9,99215,Dr. Emily Rodriguez - Internal Medicine,Complete,2025-01-17
CLM0004,PAT0004,L70.9,J1940,Dr. James Wilson - Dermatology,Complete,2025-01-18
CLM0005,PAT0005,C50.911,99213,Dr. Lisa Thompson - Pediatrics,,2025-01-19
CLM0006,PAT0006,Z51.11,99213,Dr. Robert Smith - Family Medicine,Complete,2025-01-20
"""

with open("test_claims.csv", "w") as f:
    f.write(csv_content)

print("✅ test_claims.csv generated successfully.")
