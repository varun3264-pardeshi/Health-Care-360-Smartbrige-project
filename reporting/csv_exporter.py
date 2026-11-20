"""
PulsePoint Cyber-Medical Intelligence System
Role-Aware, Filter-Responsive Data Export Service
Enforces data minimization, patient de-identification, and security audit logging.
"""

import io
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
from core.audit import log_audit_event, EVENT_EXPORT_DATA
from core.security import check_permission, ROLE_RESEARCHER, ROLE_VIEWER

def export_filtered_dataset(
    df: pd.DataFrame,
    filters_applied: Dict[str, Any],
    username: str,
    role: str
) -> Optional[str]:
    """
    Applies active dashboard filters, enforces role-based privacy masking,
    logs the audit trail, and returns a CSV formatted string.
    Returns None if the user's role lacks export permissions.
    """
    # 1. Enforce Role Permissions
    if not check_permission(role, "export_aggregates") and not check_permission(role, "export_patient_level"):
        log_audit_event(
            username=username,
            role=role,
            event_type=EVENT_EXPORT_DATA,
            resource="patient_records_csv",
            status="BLOCKED_UNAUTHORIZED",
            details={"reason": "Role lacks export permission"}
        )
        return None

    export_df = df.copy()

    # 2. Apply Active UI Filters
    if "age_min" in filters_applied and "age_max" in filters_applied:
        export_df = export_df[
            (export_df["age"] >= filters_applied["age_min"]) &
            (export_df["age"] <= filters_applied["age_max"])
        ]

    if filters_applied.get("gender") and filters_applied["gender"] != "All Genders":
        export_df = export_df[export_df["gender"] == filters_applied["gender"]]

    if filters_applied.get("region") and filters_applied["region"] != "All Regions":
        export_df = export_df[export_df["region"] == filters_applied["region"]]

    if filters_applied.get("smoking") and filters_applied["smoking"] != "All Statuses":
        export_df = export_df[export_df["smoking_status"] == filters_applied["smoking"]]

    if filters_applied.get("disease_selected") and filters_applied["disease_selected"] != "All Conditions":
        col_map = {
            "Heart Disease": "heart_disease",
            "Type 2 Diabetes": "diabetes",
            "Stroke": "stroke"
        }
        col = col_map.get(filters_applied["disease_selected"])
        if col and col in export_df.columns:
            export_df = export_df[export_df[col] == 1]

    # 3. Privacy Masking & Minimization for Researchers
    if role == ROLE_RESEARCHER:
        # Mask patient ID with anonymous sequential token
        export_df["patient_id"] = [f"ANON-RES-{i+1:05d}" for i in range(len(export_df))]
        # Strip exact assessment dates down to assessment year only
        if "assessment_date" in export_df.columns:
            export_df["assessment_year"] = pd.to_datetime(export_df["assessment_date"]).dt.year
            export_df = export_df.drop(columns=["assessment_date"])

    # 4. Generate CSV String
    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    # 5. Log Security Audit Record
    log_audit_event(
        username=username,
        role=role,
        event_type=EVENT_EXPORT_DATA,
        resource="patient_records_csv",
        status="SUCCESS",
        details={
            "exported_rows": len(export_df),
            "filters": filters_applied,
            "privacy_masked": (role == ROLE_RESEARCHER)
        }
    )

    return csv_data
