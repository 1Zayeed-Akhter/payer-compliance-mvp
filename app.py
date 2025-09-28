"""
Payer Compliance Scrub - Streamlit UI
Demo MVP for claims compliance checking and provider attestation generation.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import tempfile
import os

from scrub import apply_checks, cleaned_csv_bytes
from pdfs import zip_attestations


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Payer Compliance Scrub",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Payer Compliance Scrub")
    st.markdown("**Demo MVP** - Claims compliance checking and provider attestation")
    
    # HIPAA Disclaimer
    st.error("🚨 **CRITICAL HIPAA WARNING** 🚨")
    st.warning("⚠️ **DEMO ONLY** - This is a demonstration tool. Do not use with real PHI data.")
    st.info("ℹ️ This tool is NOT HIPAA compliant and should not be used in production.")
    
    # File upload section
    st.header("📁 Upload Claims CSV")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="Upload a claims CSV file for compliance checking. Expected columns: ClaimID, PatientID, ICD10, ProcCode, Provider, DocStatus, ServiceDate"
    )
    
    if uploaded_file is not None:
        try:
            # 🔧 Fix: force pandas to keep blanks as empty strings
            df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
            st.success(f"✅ Successfully loaded {len(df)} claims")
            
            # Display sample data
            st.subheader("📊 Data Preview")
            st.dataframe(df, use_container_width=True)
            
            # Show column information
            st.subheader("📋 Column Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Required Columns:**")
                st.write("- ClaimID: Unique claim identifier")
                st.write("- Provider: Provider name")
                st.write("- PatientID: Patient identifier")
                st.write("- ICD10: Diagnosis code")
            with col2:
                st.write("**Additional Columns:**")
                st.write("- ProcCode: Procedure code")
                st.write("- DocStatus: Documentation status")
                st.write("- ServiceDate: Date of service")
            
            # Process claims button
            if st.button("🔍 Run Compliance Checks", type="primary", use_container_width=True):
                with st.spinner("Running compliance checks..."):
                    try:
                        # Apply compliance checks
                        df_with_issues = apply_checks(df)
                        
                        # Store in session state for downloads
                        st.session_state['df_with_issues'] = df_with_issues
                        st.session_state['original_df'] = df
                        
                    except Exception as e:
                        st.error(f"❌ Error running compliance checks: {str(e)}")
                        st.exception(e)
            
            # Check if we have compliance results in session state and display them
            if 'df_with_issues' in st.session_state:
                df_with_issues = st.session_state['df_with_issues']
                
                # Display results
                display_compliance_results(df_with_issues)
                
                # Generate downloads
                generate_download_buttons(df_with_issues)
                    
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.exception(e)
    
    # Sample data section
    st.header("📋 Sample Data")
    st.markdown("Download sample claims data to test the application:")
    
    if st.button("📥 Download Sample Claims CSV", use_container_width=True):
        sample_df = create_sample_data()
        csv = sample_df.to_csv(index=False)
        st.download_button(
            label="Download sample_claims.csv",
            data=csv,
            file_name="sample_claims.csv",
            mime="text/csv",
            use_container_width=True
        )


def display_compliance_results(df_with_issues: pd.DataFrame) -> None:
    """Display compliance check results."""
    st.header("🔍 Compliance Results")
    
    total_claims = len(df_with_issues)
    claims_with_issues = len(df_with_issues[df_with_issues['Issues'].apply(lambda x: len(x) > 0)])
    clean_claims = total_claims - claims_with_issues
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Claims", total_claims)
    with col2:
        st.metric("Claims with Issues", claims_with_issues, delta=f"{claims_with_issues/total_claims*100:.1f}%")
    with col3:
        st.metric("Clean Claims", clean_claims, delta=f"{clean_claims/total_claims*100:.1f}%")
    
    st.subheader("📊 Claims with Issues")
    
    if claims_with_issues > 0:
        display_df = df_with_issues.copy()
        display_df['Issues_Formatted'] = display_df['Issues'].apply(
            lambda issues: '; '.join(issues) if issues else 'No issues'
        )
        
        display_columns = ['ClaimID', 'Provider', 'PatientID', 'ICD10', 'ProcCode', 'DocStatus', 'ServiceDate', 'Issues_Formatted']
        available_columns = [col for col in display_columns if col in display_df.columns]
        
        claims_with_issues_df = display_df[display_df['Issues'].apply(lambda x: len(x) > 0)]
        
        if not claims_with_issues_df.empty:
            st.dataframe(
                claims_with_issues_df[available_columns], 
                use_container_width=True,
                column_config={
                    "Issues_Formatted": st.column_config.TextColumn(
                        "Issues",
                        help="Compliance issues identified for this claim"
                    )
                }
            )
        else:
            st.info("ℹ️ No claims with issues found.")
    else:
        st.success("🎉 **All claims passed compliance checks!**")
        st.info("ℹ️ No compliance issues were identified in the uploaded claims data.")
        
        st.subheader("📊 All Claims (Clean)")
        display_columns = ['ClaimID', 'Provider', 'PatientID', 'ICD10', 'ProcCode', 'DocStatus', 'ServiceDate']
        available_columns = [col for col in display_columns if col in df_with_issues.columns]
        st.dataframe(df_with_issues[available_columns], use_container_width=True)


def generate_download_buttons(df_with_issues: pd.DataFrame) -> None:
    """Generate download buttons for CSV and ZIP files."""
    st.header("📥 Downloads")
    
    claims_with_issues = len(df_with_issues[df_with_issues['Issues'].apply(lambda x: len(x) > 0)])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 CSV Export")
        try:
            csv_bytes = cleaned_csv_bytes(df_with_issues)
            st.download_button(
                label="📄 Download Claims with Issues (CSV)",
                data=csv_bytes,
                file_name="claims_with_issues.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Error generating CSV: {str(e)}")
    
    with col2:
        st.subheader("📦 Provider Attestations")
        if claims_with_issues > 0:
            try:
                zip_bytes = zip_attestations(df_with_issues)
                st.download_button(
                    label="📦 Download Provider Attestation PDFs (ZIP)",
                    data=zip_bytes,
                    file_name="provider_attestations.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Error generating ZIP: {str(e)}")
        else:
            st.info("ℹ️ No attestation PDFs needed - all claims are clean!")
            st.write("**No compliance issues found, so no provider attestations are required.**")
    
    if claims_with_issues > 0:
        st.info(f"ℹ️ **{claims_with_issues} claims** require provider attestations. The ZIP file will contain individual PDF attestation forms for each provider to review and sign.")
    else:
        st.success("✅ **All claims are compliant!** No provider attestations needed.")


def create_sample_data() -> pd.DataFrame:
    """Create sample claims data for testing."""
    import random
    
    providers = [
        "Dr. Sarah Johnson - Cardiology",
        "Dr. Michael Chen - Orthopedics", 
        "Dr. Emily Rodriguez - Internal Medicine",
        "Dr. James Wilson - Dermatology",
        "Dr. Lisa Thompson - Pediatrics"
    ]
    
    procedures = ["99213", "99214", "99215", "99202", "J9355", "J1940"]
    diagnoses = ["Z51.11", "E11.9", "M25.561", "L70.9", "I50.9", "C50.911"]
    doc_statuses = ["Complete", "Attached", "Pending", ""]
    
    data = []
    for i in range(20):
        diagnosis = random.choice(diagnoses)
        procedure = random.choice(procedures)
        doc_status = random.choice(doc_statuses)
        data.append({
            "ClaimID": f"CLM{i+1:04d}",
            "Provider": random.choice(providers),
            "PatientID": f"PAT{i+1:04d}",
            "ICD10": diagnosis,
            "ProcCode": procedure,
            "DocStatus": doc_status,
            "ServiceDate": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        })
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    main()
