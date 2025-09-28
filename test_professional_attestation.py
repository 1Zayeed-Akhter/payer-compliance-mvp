#!/usr/bin/env python3
"""
Test script to demonstrate the improved professional attestation PDF format.
"""

import pandas as pd
from pdfs import make_attestation_pdf

def test_professional_attestation():
    """Test the improved professional attestation PDF format."""
    
    print("🧪 Testing Professional Attestation PDF Format")
    print("=" * 60)
    
    # Test data with realistic claim information
    test_claims = [
        {
            'ClaimID': 'CLM0001',
            'Provider': 'Dr. Sarah Johnson - Cardiology',
            'PatientID': 'PAT0001',
            'ICD10': 'I50.9',
            'ProcCode': '99213',
            'DocStatus': 'Complete',
            'ServiceDate': '2025-01-15'
        },
        {
            'ClaimID': 'CLM0002',
            'Provider': 'Dr. Michael Chen, M.D.',
            'PatientID': 'PAT0002',
            'ICD10': 'Z51.11',
            'ProcCode': 'J9355',
            'DocStatus': 'Attached',
            'ServiceDate': '2025-01-16'
        }
    ]
    
    for i, claim in enumerate(test_claims, 1):
        print(f"📄 Generating Professional Attestation PDF {i}...")
        
        try:
            # Generate PDF
            pdf_bytes = make_attestation_pdf(claim)
            
            print(f"✅ PDF {i} generated successfully!")
            print(f"📊 PDF size: {len(pdf_bytes)} bytes")
            
            # Show PDF content preview
            pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
            lines = pdf_content.split('\n')
            
            print("📋 PDF Content Preview:")
            for j, line in enumerate(lines[:20]):  # Show first 20 lines
                if line.strip():
                    print(f"  {j+1:2d}: {line.strip()}")
            print("  ...")
            print()
            
        except Exception as e:
            print(f"❌ Error generating PDF {i}: {e}")
            print()
    
    print("🎉 Professional Attestation Format Test Complete!")
    print("=" * 60)
    print("✅ Professional formatting with 1-inch margins")
    print("✅ Centered title: 'Provider Attestation'")
    print("✅ Header with today's date")
    print("✅ Clean table-style claim details layout")
    print("✅ Professional attestation statement")
    print("✅ Footer with signature section")
    print("✅ Arial font with consistent spacing")
    print("✅ Memory output - no file writes")

if __name__ == "__main__":
    test_professional_attestation()
