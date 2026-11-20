"""
PulsePoint Cyber-Medical Intelligence System
High-Concurrency WAL Database Engine, User Registration/Password Reset & Per-User Data Isolation
"""

import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from core.config import DB_PATH
from core.security import DEFAULT_USERS, hash_password, verify_password, sanitize_user_input


def get_connection() -> sqlite3.Connection:
    """
    Return an open connection to SQLite configured with WAL (Write-Ahead Logging)
    and busy_timeout=15000ms so high concurrent user traffic never locks or crashes.
    """
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=15000;")
    except Exception:
        pass
    return conn


def init_database() -> None:
    """Creates all required tables if they do not exist and seeds initial users."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT
        );
        """)

        # 2. Patient Records Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_records (
            patient_id TEXT PRIMARY KEY,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            region TEXT NOT NULL,
            bmi REAL NOT NULL,
            bmi_category TEXT NOT NULL,
            systolic_bp INTEGER NOT NULL,
            diastolic_bp INTEGER NOT NULL,
            bp_category TEXT NOT NULL,
            cholesterol_total REAL NOT NULL,
            cholesterol_hdl REAL NOT NULL,
            cholesterol_ldl REAL NOT NULL,
            cholesterol_ratio REAL NOT NULL,
            fasting_glucose REAL NOT NULL,
            glucose_category TEXT NOT NULL,
            hba1c REAL NOT NULL,
            smoking_status TEXT NOT NULL,
            alcohol_consumption TEXT NOT NULL,
            physical_activity_mins INTEGER NOT NULL,
            exercise_level TEXT NOT NULL,
            fatigue_reported INTEGER NOT NULL,
            chest_pain_type TEXT NOT NULL,
            dizziness_reported INTEGER NOT NULL,
            shortness_of_breath INTEGER NOT NULL,
            heart_disease INTEGER NOT NULL,
            diabetes INTEGER NOT NULL,
            stroke INTEGER NOT NULL,
            multimorbidity_count INTEGER NOT NULL,
            data_completeness_pct REAL NOT NULL,
            assessment_date TEXT NOT NULL,
            review_status TEXT NOT NULL,
            is_synthetic INTEGER DEFAULT 0,
            owner_username TEXT DEFAULT 'hospital_cohort'
        );
        """)

        # Add owner_username column if upgrading from an older schema
        try:
            cursor.execute("ALTER TABLE patient_records ADD COLUMN owner_username TEXT DEFAULT 'hospital_cohort';")
        except Exception:
            pass

        # 3. Data Quality Metrics Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_quality_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_timestamp TEXT NOT NULL,
            total_records INTEGER NOT NULL,
            duplicate_count INTEGER NOT NULL,
            missing_count INTEGER NOT NULL,
            completeness_pct REAL NOT NULL,
            quality_score REAL NOT NULL,
            issues_json TEXT NOT NULL
        );
        """)

        # 4. Model Metadata & Evaluation Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_type TEXT NOT NULL,
            model_type TEXT NOT NULL,
            version TEXT NOT NULL,
            train_timestamp TEXT NOT NULL,
            train_samples INTEGER NOT NULL,
            test_samples INTEGER NOT NULL,
            metrics_json TEXT NOT NULL,
            parameters_json TEXT NOT NULL,
            file_path TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        );
        """)

        # 5. Clinical Alerts Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinical_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            rule_code TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL,
            resolved_by TEXT,
            resolution_notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patient_records (patient_id)
        );
        """)

        # 6. Audit Events Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            event_type TEXT NOT NULL,
            resource TEXT NOT NULL,
            status TEXT NOT NULL,
            ip_address TEXT,
            details_json TEXT
        );
        """)

        conn.commit()

        # Ensure all DEFAULT_USERS exist
        now_str = datetime.now(timezone.utc).isoformat()
        for u in DEFAULT_USERS:
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (u["username"], u["email"]))
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO users (username, full_name, email, role, password_hash, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (u["username"], u["full_name"], u["email"], u["role"], u["password"], now_str)
                )
        conn.commit()
    finally:
        conn.close()


def query_db(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Safely execute a parameterized SELECT query with guaranteed connection release."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def execute_db(query: str, params: tuple = ()) -> int:
    """Safely execute a parameterized INSERT, UPDATE, or DELETE query with guaranteed connection release."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def authenticate_db_user(identifier: str, password: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Authenticates a user by username or email against the SQLite users table.
    Returns (user_dict_or_None, message).
    """
    clean_id, is_safe, msg = sanitize_user_input(identifier)
    if not is_safe:
        return None, msg
    if not clean_id or not password:
        return None, "Please enter both Username/Email and Password."

    rows = query_db(
        "SELECT * FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
        (clean_id, clean_id)
    )
    if not rows:
        return None, "Account not found. Please check your Username/Email or click 'Register New Account'."

    user_row = rows[0]
    if not verify_password(password, user_row["password_hash"]):
        return None, "Incorrect password. Please try again or use 'Forgot Password'."

    now_str = datetime.now(timezone.utc).isoformat()
    execute_db("UPDATE users SET last_login = ? WHERE id = ?", (now_str, user_row["id"]))

    return {
        "id": user_row["id"],
        "username": user_row["username"],
        "full_name": user_row["full_name"],
        "email": user_row["email"],
        "role": user_row["role"],
    }, "Login verified."


def register_db_user(username: str, full_name: str, email: str, role: str, password: str) -> Tuple[bool, str]:
    """
    Registers a new user in the SQLite users table with PBKDF2-HMAC-SHA256 password hashing.
    """
    clean_user, ok1, m1 = sanitize_user_input(username)
    clean_name, ok2, m2 = sanitize_user_input(full_name)
    clean_email, ok3, m3 = sanitize_user_input(email)
    if not (ok1 and ok2 and ok3):
        return False, m1 or m2 or m3

    if not clean_user or not clean_name or not clean_email or not password:
        return False, "All fields (Full Name, Username, Email, and Password) are required."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    existing = query_db(
        "SELECT id FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
        (clean_user, clean_email)
    )
    if existing:
        return False, "Username or Email is already registered. Please log in or use Forgot Password."

    pw_hash = hash_password(password)
    now_str = datetime.now(timezone.utc).isoformat()
    execute_db(
        """
        INSERT INTO users (username, full_name, email, role, password_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (clean_user, clean_name, clean_email, role, pw_hash, now_str)
    )
    return True, f"Account '{clean_user}' registered successfully! You can now log in."


def reset_db_user_password(identifier: str, new_password: str) -> Tuple[bool, str]:
    """
    Resets a user's password in the SQLite users table after 2FA OTP verification.
    """
    clean_id, is_safe, msg = sanitize_user_input(identifier)
    if not is_safe:
        return False, msg
    if not clean_id or not new_password:
        return False, "Please provide your registered Username/Email and a new password."
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    rows = query_db(
        "SELECT id, username FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
        (clean_id, clean_id)
    )
    if not rows:
        return False, "No registered account matches that Username or Email."

    pw_hash = hash_password(new_password)
    execute_db("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, rows[0]["id"]))
    return True, f"Password updated successfully for '{rows[0]['username']}'. You can now log in."
