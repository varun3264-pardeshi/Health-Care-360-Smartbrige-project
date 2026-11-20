"""
PulsePoint Cyber-Medical Intelligence System
Audit Logging & Differential Privacy / Small Cell Suppression Utility
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from core.database import execute_db, query_db
from core.config import SMALL_CELL_SUPPRESSION_THRESHOLD

# Event Types
EVENT_LOGIN = "USER_LOGIN"
EVENT_LOGOUT = "USER_LOGOUT"
EVENT_LOGIN_FAILED = "AUTH_FAILED"
EVENT_ACCESS_DENIED = "ACCESS_DENIED"
EVENT_VIEW_PATIENT = "PATIENT_RECORD_VIEWED"
EVENT_EXPORT_DATA = "DATA_EXPORTED"
EVENT_ALERT_RESOLVED = "ALERT_STATUS_CHANGED"
EVENT_MODEL_RETRAIN = "MODEL_RETRAINED"
EVENT_CONFIG_CHANGE = "SECURITY_CONFIG_MODIFIED"


def sanitize_audit_details(details: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Strip out any sensitive keys such as passwords, tokens, full credentials, or raw SSNs."""
    if not details:
        return {}
    sanitized = {}
    forbidden_substrings = ["password", "token", "secret", "auth", "key", "credential"]
    for k, v in details.items():
        if any(sub in k.lower() for sub in forbidden_substrings):
            sanitized[k] = "[REDACTED]"
        else:
            sanitized[k] = v
    return sanitized


def log_audit_event(
    username: str,
    role: str,
    event_type: str,
    resource: str,
    status: str = "SUCCESS",
    details: Optional[Dict[str, Any]] = None,
    ip_address: str = "127.0.0.1"
) -> int:
    """
    Records an immutable audit event in SQLite without logging sensitive credentials.
    """
    clean_details = sanitize_audit_details(details)
    details_str = json.dumps(clean_details)
    now_str = datetime.now(timezone.utc).isoformat()

    return execute_db(
        """
        INSERT INTO audit_events (timestamp, username, role, event_type, resource, status, ip_address, details_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (now_str, username, role, event_type, resource, status, ip_address, details_str)
    )


def apply_small_cell_suppression(count: int, threshold: int = SMALL_CELL_SUPPRESSION_THRESHOLD) -> str:
    """
    Suppresses reporting of small cell frequencies (1 <= count < threshold) to prevent
    identity disclosure in stratified cross-tabulations.
    """
    if 0 < count < threshold:
        return f"<{threshold} (Suppressed for Privacy)"
    return str(count)


def get_audit_trail(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve the most recent audit logs for administration inspection."""
    return query_db(
        """
        SELECT id, timestamp, username, role, event_type, resource, status, ip_address, details_json
        FROM audit_events
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )
