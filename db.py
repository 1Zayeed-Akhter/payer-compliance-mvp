"""
Database helpers for compliance audit workflow.
Handles SQLite operations for claims and attestations tracking.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
import os


def init_db(path: str = "compliance.db") -> None:
    """
    Initialize the compliance database with required tables.
    
    Args:
        path: Path to the SQLite database file
    """
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Create claims table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id TEXT PRIMARY KEY,
            patient_id TEXT,
            provider TEXT,
            icd10 TEXT,
            proc_code TEXT,
            doc_status TEXT,
            service_date TEXT,
            issues TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create attestations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attestations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id TEXT,
            status TEXT CHECK(status IN ('Pending', 'Signed', 'Verified')),
            signed_name TEXT NULL,
            signed_at TIMESTAMP NULL,
            verified_at TIMESTAMP NULL,
            last_reminder_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (claim_id) REFERENCES claims (id)
        )
    """)
    
    conn.commit()
    conn.close()


def upsert_claims(df: pd.DataFrame, db_path: str = "compliance.db") -> None:
    """
    Insert or update claims in the database.
    Only processes claims with issues and creates attestation records.
    
    Args:
        df: DataFrame with claims data including 'Issues' column
        db_path: Path to the SQLite database file
    """
    if df.empty or 'Issues' not in df.columns:
        return
    
    # Filter to only claims with issues
    flagged_df = df[df['Issues'].apply(lambda x: len(x) > 0)].copy()
    
    if flagged_df.empty:
        return
    
    # Convert issues list to semicolon-separated string
    flagged_df = flagged_df.copy()
    flagged_df['Issues'] = flagged_df['Issues'].apply(
        lambda issues: '; '.join(issues) if issues else ''
    )
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        for _, row in flagged_df.iterrows():
            claim_id = str(row.get('ClaimID', ''))
            if not claim_id:
                continue
                
            # Insert or update claims table
            cursor.execute("""
                INSERT OR REPLACE INTO claims 
                (id, patient_id, provider, icd10, proc_code, doc_status, service_date, issues)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                claim_id,
                str(row.get('PatientID', '')),
                str(row.get('Provider', '')),
                str(row.get('ICD10', '')),
                str(row.get('ProcCode', '')),
                str(row.get('DocStatus', '')),
                str(row.get('ServiceDate', '')),
                str(row.get('Issues', ''))
            ))
            
            # Insert attestation record if it doesn't exist (only if no attestation exists)
            cursor.execute("""
                INSERT OR IGNORE INTO attestations (claim_id, status)
                SELECT ?, 'Pending'
                WHERE NOT EXISTS (SELECT 1 FROM attestations WHERE claim_id = ?)
            """, (claim_id, claim_id))
            
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def list_claims(filters: Dict[str, Any] = None, db_path: str = "compliance.db") -> pd.DataFrame:
    """
    List claims from the database with optional filtering.
    
    Args:
        filters: Dictionary of filter criteria
        db_path: Path to the SQLite database file
        
    Returns:
        DataFrame with claims and attestation data
    """
    conn = sqlite3.connect(db_path)
    
    # Base query joining claims and attestations (only most recent attestation per claim)
    query = """
        SELECT 
            c.id as claim_id,
            c.patient_id,
            c.provider,
            c.icd10,
            c.proc_code,
            c.doc_status,
            c.service_date,
            c.issues,
            a.status as attestation_status,
            a.signed_name,
            a.signed_at,
            a.verified_at,
            a.last_reminder_at,
            c.created_at
        FROM claims c
        LEFT JOIN (
            SELECT claim_id, status, signed_name, signed_at, verified_at, last_reminder_at,
                   ROW_NUMBER() OVER (PARTITION BY claim_id ORDER BY created_at DESC) as rn
            FROM attestations
        ) a ON c.id = a.claim_id AND a.rn = 1
    """
    
    conditions = []
    params = []
    
    if filters:
        if 'provider' in filters:
            conditions.append("c.provider LIKE ?")
            params.append(f"%{filters['provider']}%")
        
        if 'status' in filters:
            conditions.append("a.status = ?")
            params.append(filters['status'])
        
        if 'issue_substring' in filters:
            conditions.append("c.issues LIKE ?")
            params.append(f"%{filters['issue_substring']}%")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY c.created_at DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df


def set_attestation_status(
    claim_id: str, 
    status: str, 
    signed_name: Optional[str] = None,
    when: Optional[datetime] = None,
    db_path: str = "compliance.db"
) -> None:
    """
    Update the status of an attestation.
    
    Args:
        claim_id: The claim ID
        status: New status ('Pending', 'Signed', 'Verified')
        signed_name: Name of person who signed (for 'Signed' status)
        when: Timestamp for the status change (defaults to now)
        db_path: Path to the SQLite database file
    """
    if status not in ['Pending', 'Signed', 'Verified']:
        raise ValueError(f"Invalid status: {status}")
    
    if when is None:
        when = datetime.now()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        if status == 'Signed':
            cursor.execute("""
                UPDATE attestations 
                SET status = ?, signed_name = ?, signed_at = ?
                WHERE claim_id = ?
            """, (status, signed_name, when, claim_id))
        elif status == 'Verified':
            cursor.execute("""
                UPDATE attestations 
                SET status = ?, verified_at = ?
                WHERE claim_id = ?
            """, (status, when, claim_id))
        else:  # Pending
            cursor.execute("""
                UPDATE attestations 
                SET status = ?
                WHERE claim_id = ?
            """, (status, claim_id))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def mark_reminded(claim_id: str, when: Optional[datetime] = None, db_path: str = "compliance.db") -> None:
    """
    Mark that a reminder was sent for an attestation.
    
    Args:
        claim_id: The claim ID
        when: Timestamp for the reminder (defaults to now)
        db_path: Path to the SQLite database file
    """
    if when is None:
        when = datetime.now()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE attestations 
            SET last_reminder_at = ?
            WHERE claim_id = ?
        """, (when, claim_id))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_attestation_stats(db_path: str = "compliance.db") -> Dict[str, int]:
    """
    Get statistics about attestation statuses.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Dictionary with status counts
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Use the same deduplication logic as list_claims
    cursor.execute("""
        SELECT status, COUNT(*) 
        FROM (
            SELECT claim_id, status,
                   ROW_NUMBER() OVER (PARTITION BY claim_id ORDER BY created_at DESC) as rn
            FROM attestations
        ) deduped
        WHERE rn = 1
        GROUP BY status
    """)
    
    stats = dict(cursor.fetchall())
    conn.close()
    
    return stats


def cleanup_duplicate_attestations(db_path: str = "compliance.db") -> int:
    """
    Remove duplicate attestation records, keeping only the most recent one per claim.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Number of duplicate records removed
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Count duplicates before cleanup
        cursor.execute("""
            SELECT COUNT(*) - COUNT(DISTINCT claim_id)
            FROM attestations
        """)
        duplicate_count = cursor.fetchone()[0]
        
        if duplicate_count > 0:
            # Delete duplicates, keeping only the most recent
            cursor.execute("""
                DELETE FROM attestations 
                WHERE id NOT IN (
                    SELECT id FROM (
                        SELECT id,
                               ROW_NUMBER() OVER (PARTITION BY claim_id ORDER BY created_at DESC) as rn
                        FROM attestations
                    ) ranked
                    WHERE rn = 1
                )
            """)
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
        else:
            return 0
            
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
