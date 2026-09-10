import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

DATABASE_PATH = "patients.db"


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _handle_db_error(e: Exception, operation: str) -> None:
    """Log database error and raise HTTPException."""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Database error during {operation}: {e}")
    raise Exception(f"Database error: {operation} failed")


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL CHECK(length(first_name) BETWEEN 1 AND 50),
                last_name TEXT NOT NULL CHECK(length(last_name) BETWEEN 1 AND 50),
                date_of_birth TEXT NOT NULL,
                sex TEXT NOT NULL CHECK(sex IN ('Male', 'Female', 'Other', 'Decline to Answer')),
                phone_number TEXT NOT NULL,
                email TEXT,
                address_line_1 TEXT NOT NULL,
                address_line_2 TEXT,
                city TEXT NOT NULL CHECK(length(city) BETWEEN 1 AND 100),
                state TEXT NOT NULL CHECK(length(state) = 2),
                zip_code TEXT NOT NULL,
                insurance_provider TEXT,
                insurance_member_id TEXT,
                preferred_language TEXT DEFAULT 'English',
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deleted_at TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone ON patients(phone_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_last_name ON patients(last_name)")
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        _handle_db_error(e, "init_db")
    finally:
        conn.close()


def create_patient(data: dict) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    patient_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    try:
        cursor.execute("""
            INSERT INTO patients (
                patient_id, first_name, last_name, date_of_birth, sex,
                phone_number, email, address_line_1, address_line_2,
                city, state, zip_code, insurance_provider, insurance_member_id,
                preferred_language, emergency_contact_name, emergency_contact_phone,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id, data.get("first_name"), data.get("last_name"),
            data.get("date_of_birth"), data.get("sex"), data.get("phone_number"),
            data.get("email"), data.get("address_line_1"), data.get("address_line_2"),
            data.get("city"), data.get("state"), data.get("zip_code"),
            data.get("insurance_provider"), data.get("insurance_member_id"),
            data.get("preferred_language", "English"),
            data.get("emergency_contact_name"), data.get("emergency_contact_phone"),
            now, now
        ))
        conn.commit()
        patient = dict(cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,)).fetchone())
        return patient
    except sqlite3.Error as e:
        conn.rollback()
        _handle_db_error(e, "create_patient")
    finally:
        conn.close()


def get_patient(patient_id: str) -> Optional[dict]:
    conn = get_db()
    cursor = conn.cursor()
    try:
        row = cursor.execute(
            "SELECT * FROM patients WHERE patient_id = ? AND deleted_at IS NULL",
            (patient_id,)
        ).fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        _handle_db_error(e, "get_patient")
    finally:
        conn.close()


def get_patient_by_phone(phone: str) -> Optional[dict]:
    conn = get_db()
    cursor = conn.cursor()
    try:
        row = cursor.execute(
            "SELECT * FROM patients WHERE phone_number = ? AND deleted_at IS NULL",
            (phone,)
        ).fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        _handle_db_error(e, "get_patient_by_phone")
    finally:
        conn.close()


def list_patients(last_name: Optional[str] = None, date_of_birth: Optional[str] = None,
                  phone_number: Optional[str] = None) -> list:
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM patients WHERE deleted_at IS NULL"
    params = []
    
    if last_name:
        query += " AND last_name = ?"
        params.append(last_name)
    if date_of_birth:
        query += " AND date_of_birth = ?"
        params.append(date_of_birth)
    if phone_number:
        query += " AND phone_number = ?"
        params.append(phone_number)
    
    try:
        rows = cursor.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        _handle_db_error(e, "list_patients")
    finally:
        conn.close()


def update_patient(patient_id: str, data: dict) -> Optional[dict]:
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        existing = cursor.execute(
            "SELECT * FROM patients WHERE patient_id = ? AND deleted_at IS NULL",
            (patient_id,)
        ).fetchone()
        if not existing:
            return None
        
        updates = []
        params = []
        for key, value in data.items():
            if value is not None and key in [
                "first_name", "last_name", "date_of_birth", "sex", "phone_number",
                "email", "address_line_1", "address_line_2", "city", "state",
                "zip_code", "insurance_provider", "insurance_member_id",
                "preferred_language", "emergency_contact_name", "emergency_contact_phone"
            ]:
                updates.append(f"{key} = ?")
                params.append(value)
        
        if not updates:
            return dict(existing)
        
        updates.append("updated_at = ?")
        params.append(datetime.now(timezone.utc).isoformat())
        params.append(patient_id)
        
        cursor.execute(
            f"UPDATE patients SET {', '.join(updates)} WHERE patient_id = ?",
            params
        )
        conn.commit()
        patient = dict(cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,)).fetchone())
        return patient
    except sqlite3.Error as e:
        conn.rollback()
        _handle_db_error(e, "update_patient")
    finally:
        conn.close()


def soft_delete_patient(patient_id: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE patients SET deleted_at = ? WHERE patient_id = ? AND deleted_at IS NULL",
            (datetime.now(timezone.utc).isoformat(), patient_id)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        return deleted
    except sqlite3.Error as e:
        conn.rollback()
        _handle_db_error(e, "soft_delete_patient")
    finally:
        conn.close()
