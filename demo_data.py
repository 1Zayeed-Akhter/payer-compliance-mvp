"""
Demo data generation for Payer Compliance Scrub.
Generates synthetic claims data for demonstration purposes.
"""

import pandas as pd
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta


def generate_demo_dataset(num_rows: int = 50) -> pd.DataFrame:
    """
    Generate a comprehensive demo dataset with ~50% flagged claims.
    
    Args:
        num_rows: Number of rows to generate (default: 50)
        
    Returns:
        DataFrame with synthetic claims data including new POS and Modifiers columns
    """
    # Set random seed for reproducible demo data
    random.seed(42)
    
    # Provider specialties and names
    providers = [
        "Dr. Sarah Johnson - Cardiology",
        "Dr. Michael Chen - Orthopedics", 
        "Dr. Emily Rodriguez - Internal Medicine",
        "Dr. James Wilson - Dermatology",
        "Dr. Lisa Thompson - Pediatrics",
        "Dr. Robert Martinez - Family Practice"
    ]
    
    # ICD-10 codes including high-audit-risk ones (I50, C50)
    icd10_codes = [
        "Z51.11",  # Encounter for antineoplastic chemotherapy
        "E11.9",   # Type 2 diabetes mellitus without complications
        "M25.561", # Pain in right knee
        "L70.9",   # Acne, unspecified
        "I50.9",   # Heart failure, unspecified (high-audit-risk)
        "C50.911", # Malignant neoplasm of unspecified site of right female breast (high-audit-risk)
        "J44.1",   # Chronic obstructive pulmonary disease with acute exacerbation
        "N39.0",   # Urinary tract infection, site not specified
        "M79.3",   # Panniculitis, unspecified
        "G47.00"   # Insomnia, unspecified
    ]
    
    # CPT codes including high-cost J-codes and telehealth codes
    cpt_codes = [
        "99213",  # Office visit, established patient, expanded problem focused
        "99214",  # Office visit, established patient, detailed
        "99215",  # Office visit, established patient, comprehensive
        "99212",  # Office visit, established patient, problem focused (telehealth)
        "J9355",  # Injection, trastuzumab, 10 mg (high-cost)
        "J1940",  # Injection, furosemide, up to 20 mg (high-cost)
        "11055",  # Paring or cutting of benign hyperkeratotic lesion (NCCI pair demo)
        "99202",  # Office visit, new patient, expanded problem focused
        "99203",  # Office visit, new patient, detailed
        "99204"   # Office visit, new patient, comprehensive
    ]
    
    # Documentation statuses
    doc_statuses = [
        "Complete",    # Should trigger mismatch for J-codes
        "Attached",    # Correct for J-codes
        "Pending",     # Should trigger missing documentation
        "",            # Should trigger missing documentation
        "Review"       # Additional variety
    ]
    
    # Place of Service codes (11=Office, 02=Telehealth, 10=Home)
    pos_codes = ["11", "02", "10"]
    
    # Modifier combinations
    modifier_options = [
        "",           # No modifiers (should trigger telehealth issues)
        "95",         # Telehealth modifier
        "25",         # Significant, separately identifiable evaluation and management service
        "95,25",      # Multiple modifiers
        "95,52"       # Telehealth + reduced services
    ]
    
    data = []
    
    for i in range(num_rows):
        # Generate base claim data
        claim_id = f"CLM{i+1:04d}"
        provider = random.choice(providers)
        patient_id = f"PAT{random.randint(1000, 9999)}"
        
        # Select codes with some bias toward high-audit-risk combinations
        icd10 = random.choice(icd10_codes)
        proc_code = random.choice(cpt_codes)
        doc_status = random.choice(doc_statuses)
        pos = random.choice(pos_codes)
        modifiers = random.choice(modifier_options)
        
        # Generate service date (within last 6 months)
        base_date = datetime.now() - timedelta(days=random.randint(1, 180))
        service_date = base_date.strftime("%Y-%m-%d")
        
        # Create claim record
        claim = {
            "ClaimID": claim_id,
            "Provider": provider,
            "PatientID": patient_id,
            "ICD10": icd10,
            "ProcCode": proc_code,
            "DocStatus": doc_status,
            "ServiceDate": service_date,
            "POS": pos,
            "Modifiers": modifiers
        }
        
        data.append(claim)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Ensure ~50% flagged distribution by strategically adjusting some records
    # This ensures we get a good mix of compliance issues for demonstration
    flagged_count = 0
    target_flagged = num_rows // 2
    
    for i, row in df.iterrows():
        if flagged_count >= target_flagged:
            break
            
        # Force some issues to ensure good demo distribution
        if i % 3 == 0:  # Every 3rd record gets missing documentation
            df.at[i, 'DocStatus'] = ""
        elif i % 5 == 0:  # Every 5th record gets telehealth without modifier
            df.at[i, 'ProcCode'] = "99213"
            df.at[i, 'POS'] = "02"
            df.at[i, 'Modifiers'] = ""
        elif i % 7 == 0:  # Every 7th record gets high-cost procedure without attached docs
            df.at[i, 'ProcCode'] = "J9355"
            df.at[i, 'DocStatus'] = "Complete"
        
        flagged_count += 1
    
    return df


def get_demo_dataset_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get statistics about the generated demo dataset.
    
    Args:
        df: Generated demo DataFrame
        
    Returns:
        Dictionary with dataset statistics
    """
    return {
        "total_rows": len(df),
        "unique_providers": df['Provider'].nunique(),
        "unique_icd10": df['ICD10'].nunique(),
        "unique_cpt": df['ProcCode'].nunique(),
        "pos_distribution": df['POS'].value_counts().to_dict(),
        "doc_status_distribution": df['DocStatus'].value_counts().to_dict(),
        "high_audit_risk_diagnoses": len(df[df['ICD10'].str.startswith(('I50', 'C50'))]),
        "high_cost_procedures": len(df[df['ProcCode'].isin(['J9355', 'J1940'])]),
        "telehealth_claims": len(df[df['POS'].isin(['02', '10'])])
    }


if __name__ == "__main__":
    # Generate and display demo dataset
    demo_df = generate_demo_dataset(50)
    print("Demo Dataset Generated:")
    print(f"Rows: {len(demo_df)}")
    print("\nFirst 10 rows:")
    print(demo_df.head(10))
    
    print("\nDataset Statistics:")
    stats = get_demo_dataset_stats(demo_df)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Save to CSV for testing
    demo_df.to_csv("demo_claims_50.csv", index=False)
    print(f"\nDemo dataset saved to: demo_claims_50.csv")
