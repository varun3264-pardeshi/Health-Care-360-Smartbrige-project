"""
Unit & Integration Tests: Clinical Alerts, Audit Logging & PDF / CSV Reporting
"""

import os
import pytest
import pandas as pd
from pathlib import Path
from core.database import query_db, execute_db
from core.audit import log_audit_event, get_audit_trail
from reporting.csv_exporter import export_filtered_dataset
from reporting.pdf_generator import generate_executive_pdf_report
from ml_engine.evaluator import get_latest_model_metrics
from data_pipeline.exporter import load_dataset
from core.security import ROLE_ADMIN, ROLE_CLINICIAN, ROLE_RESEARCHER, ROLE_VIEWER

def test_clinical_alerts_exist_in_db():
    """Verify that clinical alerts were registered for severe thresholds."""
    alerts = query_db("SELECT * FROM clinical_alerts WHERE status = 'ACTIVE'")
    assert len(alerts) > 0

    severities = {a["severity"] for a in alerts}
    assert "CRITICAL" in severities or "HIGH" in severities


def test_audit_logging_and_retrieval():
    """Verify immutable audit records can be logged and queried."""
    init_logs = get_audit_trail(limit=5)
    
    # Log test event
    log_audit_event(
        username="unit_test_user",
        role="Administrator",
        event_type="TEST_AUDIT_ACTION",
        resource="test_resource",
        status="SUCCESS",
        details={"test_metric": 42}
    )

    updated_logs = get_audit_trail(limit=10)
    assert len(updated_logs) >= len(init_logs)
    top_log = updated_logs[0]
    assert top_log["username"] == "unit_test_user"
    assert top_log["event_type"] == "TEST_AUDIT_ACTION"


def test_csv_exporter_role_deidentification():
    """Verify CSV export sanitizes patient IDs for researchers and denies read-only viewers."""
    df = load_dataset().head(20)

    # 1. Clinician export retains patient ID
    csv_clin = export_filtered_dataset(df, {}, "dr_chen", ROLE_CLINICIAN)
    assert csv_clin is not None
    assert "PT-" in csv_clin

    # 2. Researcher export masks patient ID
    csv_res = export_filtered_dataset(df, {}, "researcher_alex", ROLE_RESEARCHER)
    assert csv_res is not None
    assert "ANON-RES-" in csv_res
    assert "assessment_date" not in csv_res # Stripped for privacy

    # 3. Viewer export is denied (returns None)
    csv_view = export_filtered_dataset(df, {}, "viewer_guest", ROLE_VIEWER)
    assert csv_view is None


def test_pdf_report_compilation():
    """Verify ReportLab compiles a valid, non-empty PDF binary."""
    df = load_dataset().head(100)
    models = get_latest_model_metrics()

    pdf_path = generate_executive_pdf_report(
        df=df,
        quality_metrics={"quality_score": 94.0},
        models_summary=models,
        output_filename="test_run_report.pdf",
        generated_by="Automated Test Runner"
    )

    assert os.path.exists(pdf_path)
    file_size = os.path.getsize(pdf_path)
    assert file_size > 5000, f"PDF file size {file_size} is suspiciously small."
