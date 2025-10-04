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
import db


def main() -> None:
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Payer Compliance Scrub",
        page_icon="🏥",
        layout="wide"
    )
    
    # Initialize database
    db.init_db()
    
    st.title("🏥 Payer Compliance Scrub")
    st.markdown("**Demo MVP** - Claims compliance checking and provider attestation")
    
    # HIPAA Disclaimer
    st.error("🚨 **CRITICAL HIPAA WARNING** 🚨")
    st.warning("⚠️ **DEMO ONLY** - This is a demonstration tool. Do not use with real PHI data.")
    st.info("ℹ️ This tool is NOT HIPAA compliant and should not be used in production.")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📁 Upload Claims", "🔍 Compliance Review", "📋 Attestation Dashboard"])
    
    with tab1:
        upload_claims_tab()
    
    with tab2:
        compliance_review_tab()
    
    with tab3:
        attestation_dashboard_tab()
    


def upload_claims_tab() -> None:
    """Upload Claims tab - handles file upload and compliance checking."""
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
                        
                        # Persist flagged claims to database
                        db.upsert_claims(df_with_issues)
                        st.success("✅ Compliance results saved to database")
                        
                    except Exception as e:
                        st.error(f"❌ Error running compliance checks: {str(e)}")
                        st.exception(e)
                    
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


def compliance_review_tab() -> None:
    """Compliance Review tab - shows results and downloads."""
    st.header("🔍 Compliance Review")
    
    # Check if we have compliance results in session state
    if 'df_with_issues' in st.session_state:
        df_with_issues = st.session_state['df_with_issues']
        
        # Display results
        display_compliance_results(df_with_issues)
        
        # Generate downloads
        generate_download_buttons(df_with_issues)
    else:
        st.info("ℹ️ Please upload and process claims in the 'Upload Claims' tab first.")


def attestation_dashboard_tab() -> None:
    """Attestation Dashboard tab - shows flagged claims from database with actions."""
    st.header("📋 Attestation Dashboard")
    
    # Load flagged claims from database
    try:
        claims_df = db.list_claims()
        
        if claims_df.empty:
            st.info("ℹ️ No flagged claims found in the database.")
            return
        
        # Filter out claims without attestations (shouldn't happen, but safety check)
        claims_with_attestations = claims_df[claims_df['attestation_status'].notna()]
        
        if claims_with_attestations.empty:
            st.info("ℹ️ No attestations found in the database.")
            return
        
        # Display summary stats
        stats = db.get_attestation_stats()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Flagged Claims", len(claims_with_attestations))
        with col2:
            st.metric("Pending", stats.get('Pending', 0))
        with col3:
            st.metric("Signed", stats.get('Signed', 0))
        with col4:
            st.metric("Verified", stats.get('Verified', 0))
        
        # Debug info (remove this after fixing)
        with st.expander("🔍 Debug Info", expanded=False):
            st.write(f"Total claims in database: {len(claims_df)}")
            st.write(f"Claims with attestations: {len(claims_with_attestations)}")
            st.write(f"Unique claim IDs: {claims_with_attestations['claim_id'].nunique()}")
            st.write(f"Duplicate claim IDs: {claims_with_attestations['claim_id'].duplicated().sum()}")
            
            # Show detailed breakdown
            st.write("**Status breakdown:**")
            status_counts = claims_with_attestations['attestation_status'].value_counts()
            for status, count in status_counts.items():
                st.write(f"- {status}: {count}")
            
            # Show unique vs total
            st.write(f"**Count analysis:**")
            st.write(f"- Total rows: {len(claims_with_attestations)}")
            st.write(f"- Unique claims: {claims_with_attestations['claim_id'].nunique()}")
            st.write(f"- Difference (duplicates): {len(claims_with_attestations) - claims_with_attestations['claim_id'].nunique()}")
            
            if claims_with_attestations['claim_id'].duplicated().any():
                duplicates = claims_with_attestations[claims_with_attestations['claim_id'].duplicated(keep=False)]
                st.write("**Duplicate claims:**")
                st.dataframe(duplicates[['claim_id', 'provider', 'attestation_status']])
            
            # Session state debug
            st.write("**Session state modal info:**")
            if 'selected_claim_for_attestation' in st.session_state:
                claim_info = st.session_state['selected_claim_for_attestation']
                st.write(f"- selected_claim_for_attestation: {claim_info['unique_key']}")
            else:
                st.write("- No modal selected")
        
        # Add filters
        st.subheader("🔍 Filters")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            # Provider filter
            unique_providers = ['All'] + sorted(claims_with_attestations['provider'].unique().tolist())
            selected_provider = st.selectbox("Provider", unique_providers)
        
        with filter_col2:
            # Status filter
            unique_statuses = claims_with_attestations['attestation_status'].unique().tolist()
            selected_statuses = st.multiselect("Status", unique_statuses, default=unique_statuses)
        
        with filter_col3:
            # Issue search
            issue_search = st.text_input("Search Issues", placeholder="Enter issue text...")
        
        # Apply filters
        filtered_df = claims_with_attestations.copy()
        
        if selected_provider != 'All':
            filtered_df = filtered_df[filtered_df['provider'] == selected_provider]
        
        if selected_statuses:
            filtered_df = filtered_df[filtered_df['attestation_status'].isin(selected_statuses)]
        
        if issue_search:
            filtered_df = filtered_df[filtered_df['issues'].str.contains(issue_search, case=False, na=False)]
        
        # Remind pending > 48h button
        st.subheader("📧 Actions")
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("🔔 Remind Pending > 48h", type="secondary"):
                remind_pending_attestations(claims_with_attestations)
        
        with col2:
            if st.button("🧹 Clean Duplicates", type="secondary"):
                deleted_count = db.cleanup_duplicate_attestations()
                if deleted_count > 0:
                    st.success(f"✅ Removed {deleted_count} duplicate attestation records")
                    st.rerun()
                else:
                    st.info("ℹ️ No duplicate records found")
        
        # Display filtered claims table with actions
        st.subheader("📊 Flagged Claims Overview")
        
        if filtered_df.empty:
            st.info("No claims match the current filters.")
            return
        
        # Create a table with actions for each row
        for idx, row in filtered_df.iterrows():
            # Create unique key using both claim_id and row index to avoid duplicates
            unique_key = f"{row['claim_id']}_{idx}"
            
            with st.expander(f"Claim {row['claim_id']} - {row['provider']} ({row['attestation_status']})", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Issues:** {row['issues']}")
                    if pd.notna(row['signed_at']):
                        st.write(f"**Signed:** {row['signed_at']} by {row['signed_name']}")
                    if pd.notna(row['verified_at']):
                        st.write(f"**Verified:** {row['verified_at']}")
                
                with col2:
                    if row['attestation_status'] == 'Pending':
                        if st.button(f"📝 Open Attestation", key=f"open_{unique_key}"):
                            st.session_state['selected_claim_for_attestation'] = {
                                'claim_data': row.to_dict(),
                                'unique_key': unique_key
                            }
                            st.write(f"DEBUG: Set modal state for {unique_key}")
                            st.rerun()
                    elif row['attestation_status'] == 'Signed':
                        if st.button(f"✅ Verify", key=f"verify_{unique_key}"):
                            db.set_attestation_status(row['claim_id'], 'Verified')
                            st.success(f"Claim {row['claim_id']} verified!")
                            st.rerun()
                
                with col3:
                    if st.button(f"🔄 Refresh", key=f"refresh_{unique_key}"):
                        st.rerun()
        
        # Handle attestation modal (outside the main loop)
        if 'selected_claim_for_attestation' in st.session_state:
            claim_info = st.session_state['selected_claim_for_attestation']
            claim_data = claim_info['claim_data']
            unique_key = claim_info['unique_key']
            st.write(f"DEBUG: Opening modal for {unique_key}")
            show_attestation_modal(claim_data, unique_key)
        
    except Exception as e:
        st.error(f"❌ Error loading attestation data: {str(e)}")


def show_attestation_modal(claim_row, unique_key) -> None:
    """Show attestation modal for signature capture."""
    # Convert dict back to Series if needed
    if isinstance(claim_row, dict):
        import pandas as pd
        claim_row = pd.Series(claim_row)
    
    with st.container():
        st.markdown("---")
        st.subheader(f"📝 Attestation for Claim {claim_row['claim_id']}")
        
        # Claim details
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Claim Details:**")
            st.write(f"- **Claim ID:** {claim_row['claim_id']}")
            st.write(f"- **Provider:** {claim_row['provider']}")
            st.write(f"- **Patient ID:** {claim_row['patient_id']}")
            st.write(f"- **Service Date:** {claim_row['service_date']}")
        
        with col2:
            st.write("**Clinical Details:**")
            st.write(f"- **ICD-10:** {claim_row['icd10']}")
            st.write(f"- **ProcCode:** {claim_row['proc_code']}")
        
        # Issues
        st.write("**Compliance Issues Identified:**")
        issues_list = claim_row['issues'].split('; ') if claim_row['issues'] else []
        for issue in issues_list:
            st.write(f"• {issue}")
        
        # Attestation statement
        st.write("**Attestation Statement:**")
        attestation_text = """I attest that the diagnoses and procedures billed on this claim are supported by contemporaneous clinical documentation for the date of service listed above. I understand that falsification or omission may result in penalties under applicable law."""
        st.info(attestation_text)
        
        # Signature capture
        st.write("**Electronic Signature:**")
        
        # Required checkbox
        attest_checkbox = st.checkbox("I attest", key=f"attest_checkbox_{unique_key}")
        
        # Name input (default to provider name)
        default_name = claim_row['provider']
        signed_name = st.text_input("Name", value=default_name, key=f"signature_name_{unique_key}")
        
        # Sign button
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("✍️ Sign", key=f"sign_button_{unique_key}"):
                if attest_checkbox and signed_name:
                    # Update database
                    db.set_attestation_status(claim_row['claim_id'], 'Signed', signed_name)
                    
                    # Create signature record
                    from datetime import datetime
                    signature_record = f"Electronically signed by {signed_name} on {datetime.utcnow().isoformat()}"
                    
                    st.success(f"✅ Attestation signed by {signed_name}")
                    # Clear the modal state
                    if 'selected_claim_for_attestation' in st.session_state:
                        del st.session_state['selected_claim_for_attestation']
                    st.rerun()
                else:
                    st.error("Please check 'I attest' and enter your name.")
        
        with col2:
            if st.button("❌ Cancel", key=f"cancel_button_{unique_key}"):
                # Clear the modal state
                if 'selected_claim_for_attestation' in st.session_state:
                    del st.session_state['selected_claim_for_attestation']
                st.rerun()


def remind_pending_attestations(claims_df) -> None:
    """Send reminders for pending attestations > 48 hours old."""
    from datetime import datetime, timedelta
    
    cutoff_time = datetime.utcnow() - timedelta(hours=48)
    reminded_count = 0
    
    for idx, row in claims_df.iterrows():
        if row['attestation_status'] == 'Pending':
            # Check if reminder needed
            needs_reminder = False
            
            if pd.isna(row['last_reminder_at']):
                # Never reminded
                needs_reminder = True
            else:
                # Check if last reminder was > 48h ago
                try:
                    last_reminder = pd.to_datetime(row['last_reminder_at'])
                    if last_reminder < cutoff_time:
                        needs_reminder = True
                except:
                    needs_reminder = True
            
            if needs_reminder:
                # Mock send reminder (console log)
                print(f"📧 REMINDER SENT: Provider {row['provider']} for Claim {row['claim_id']}")
                
                # Update last_reminder_at
                db.mark_reminded(row['claim_id'])
                reminded_count += 1
    
    if reminded_count > 0:
        st.success(f"🔔 Sent {reminded_count} reminder(s)")
        st.toast(f"Sent {reminded_count} reminder(s) for pending attestations")
    else:
        st.info("ℹ️ No reminders needed - all pending attestations are within 48 hours")


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
