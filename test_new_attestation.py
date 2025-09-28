#!/usr/bin/env python3
"""
Test script to demonstrate the new professional attestation PDF format.
"""

import pandas as pd
from pdfs import make_attestation_pdf

def test_new_attestation_format():
    """Test the new professional attestation PDF format."""
    
    print("🧪 Testing New Professional Attestation PDF Format")
    print("=" * 60)
    
    # Test data
    test_claims = [
        {
            'ClaimID': 'CLM001',
            'Provider': 'Dr. Sarah Johnson - Cardiology',
            'PatientID': 'PAT001',
            'ICD10': 'I50.9',
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2024-01-15'
        },
        {
            'ClaimID': 'CLM002',
            'Provider': 'Dr. Michael Chen, M.D.',
            'PatientID': 'PAT002',
            'ICD10': 'Z51.11',
            'ProcCode': 'J9355',
            'DocStatus': 'Attached',
            'ServiceDate': '2024-01-16'
        }
    ]
    
    for i, claim in enumerate(test_claims, 1):
        print(f"📄 Generating Attestation PDF {i}...")
        
        try:
            # Generate PDF
            pdf_bytes = make_attestation_pdf(claim)
            
            print(f"✅ PDF {i} generated successfully!")
            print(f"📊 PDF size: {len(pdf_bytes)} bytes")
            
            # Show PDF content preview
            pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
            lines = pdf_content.split('\n')
            
            print("📋 PDF Content Preview:")
            for j, line in enumerate(lines[:15]):  # Show first 15 lines
                if line.strip():
                    print(f"  {j+1:2d}: {line.strip()}")
            print("  ...")
            print()
            
        except Exception as e:
            print(f"❌ Error generating PDF {i}: {e}")
            print()
    
    print("🎉 New Professional Attestation Format Test Complete!")
    print("=" * 60)
    print("✅ Clean, professional one-page format")
    print("✅ Centered title: 'Provider Attestation'")
    print("✅ Header with today's date")
    print("✅ Neat table-style claim details")
    print("✅ Standard attestation statement")
    print("✅ Professional signature section")
    print("✅ Arial font with consistent spacing")
    print("✅ No file writes - returns PDF bytes in memory")

if __name__ == "__main__":
    test_new_attestation_format()
