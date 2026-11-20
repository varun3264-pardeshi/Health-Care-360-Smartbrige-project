"""
Integration Tests: FastAPI REST Endpoints, Authentication & RBAC Enforcement
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from core.security import create_access_token, ROLE_ADMIN, ROLE_CLINICIAN, ROLE_RESEARCHER

client = TestClient(app)

def test_api_health_endpoint():
    """Verify GET /api/health returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["database"] == "CONNECTED"
    assert data["models_loaded"] == 3


def test_api_login_success_and_failure():
    """Verify POST /api/auth/login validates credentials and issues token."""
    # Valid login
    res_valid = client.post("/api/auth/login", json={"username": "dr_chen", "password": "Clinician@2026!"})
    assert res_valid.status_code == 200
    token_data = res_valid.json()
    assert "access_token" in token_data
    assert token_data["role"] == ROLE_CLINICIAN

    # Invalid password
    res_invalid = client.post("/api/auth/login", json={"username": "dr_chen", "password": "WrongPassword!"})
    assert res_invalid.status_code == 401

    # Non-existent user
    res_ghost = client.post("/api/auth/login", json={"username": "ghost_user", "password": "SomePassword!"})
    assert res_ghost.status_code == 401


def test_api_analytics_summary_requires_auth():
    """Verify GET /api/analytics/summary rejects unauthenticated requests."""
    res_no_auth = client.get("/api/analytics/summary")
    assert res_no_auth.status_code == 401

    # Authenticated call
    token = create_access_token({"sub": "analyst_sarah", "role": "Healthcare Analyst"})
    res_auth = client.get("/api/analytics/summary", headers={"Authorization": f"Bearer {token}"})
    assert res_auth.status_code == 200
    data = res_auth.json()
    assert data["total_patients"] > 0
    assert 0.0 <= data["heart_disease_prevalence_pct"] <= 100.0


def test_api_predict_single_disease():
    """Verify POST /api/predict/{disease} validates payload and infers risk."""
    token = create_access_token({"sub": "dr_chen", "role": ROLE_CLINICIAN})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "age": 60,
        "gender": "Male",
        "bmi": 29.5,
        "systolic_bp": 155,
        "diastolic_bp": 92,
        "cholesterol_total": 235.0,
        "cholesterol_hdl": 38.0,
        "cholesterol_ldl": 160.0,
        "fasting_glucose": 135.0,
        "hba1c": 7.2,
        "smoking_status": "Current",
        "alcohol_consumption": "Moderate",
        "physical_activity_mins": 60,
        "fatigue_reported": 1,
        "chest_pain_type": "Typical Angina",
        "dizziness_reported": 0,
        "shortness_of_breath": 1
    }

    res = client.post("/api/predict/heart_disease", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["disease"] == "heart_disease"
    assert 0.0 <= data["risk_probability"] <= 1.0
    assert "risk_tier" in data

    # Invalid disease name returns 400
    res_bad = client.post("/api/predict/unknown_condition", json=payload, headers=headers)
    assert res_bad.status_code == 400


def test_api_patient_360_rbac_restriction():
    """Verify GET /api/patients/{id} permits Clinicians & Admins, but forbids Researchers."""
    # Researcher attempt should return 403 Forbidden
    res_token = create_access_token({"sub": "researcher_alex", "role": ROLE_RESEARCHER})
    res_researcher = client.get("/api/patients/PT-10001", headers={"Authorization": f"Bearer {res_token}"})
    assert res_researcher.status_code == 403

    # Clinician attempt should return 200 OK
    clin_token = create_access_token({"sub": "dr_chen", "role": ROLE_CLINICIAN})
    res_clin = client.get("/api/patients/PT-10001", headers={"Authorization": f"Bearer {clin_token}"})
    assert res_clin.status_code == 200
    assert "patient" in res_clin.json()


def test_api_predict_batch():
    """Verify POST /api/predict/batch performs high-throughput batch scoring."""
    token = create_access_token({"sub": "dr_chen", "role": ROLE_CLINICIAN})
    headers = {"Authorization": f"Bearer {token}"}

    sample_pt = {
        "age": 60, "gender": "Male", "bmi": 29.5, "systolic_bp": 155, "diastolic_bp": 92,
        "cholesterol_total": 235.0, "cholesterol_hdl": 38.0, "cholesterol_ldl": 160.0,
        "fasting_glucose": 135.0, "hba1c": 7.2, "smoking_status": "Current",
        "alcohol_consumption": "Moderate", "physical_activity_mins": 60,
        "fatigue_reported": 1, "chest_pain_type": "Typical Angina",
        "dizziness_reported": 0, "shortness_of_breath": 1
    }

    payload = {"patients": [sample_pt, sample_pt]}
    res = client.post("/api/predict/batch", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_processed"] == 2
    assert len(data["results"]) == 2
    assert "heart_disease" in data["results"][0]["predictions"]


def test_api_patient_review_update():
    """Verify PATCH /api/patients/{id}/review updates review status and logs audit."""
    token = create_access_token({"sub": "dr_chen", "role": ROLE_CLINICIAN})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "review_status": "Reviewed",
        "clinical_notes": "Automated test review completed successfully."
    }
    res = client.patch("/api/patients/PT-10001/review", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["review_status"] == "Reviewed"


def test_api_create_clinical_alert():
    """Verify POST /api/alerts registers new alert and enforces RBAC."""
    token = create_access_token({"sub": "dr_chen", "role": ROLE_CLINICIAN})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "patient_id": "PT-10001",
        "alert_type": "HEMODYNAMIC",
        "severity": "CRITICAL",
        "title": "Severe Hypertensive Excursion",
        "description": "Systolic BP 185 mmHg detected on follow-up.",
        "rule_code": "CRIT-HTN-01"
    }
    res = client.post("/api/alerts", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CREATED"
    assert data["patient_id"] == "PT-10001"


def test_api_web_scenarios_endpoint():
    """Verify GET /api/web/scenarios returns Scenario 1 (Dr. Carter), Scenario 2 (Emily), and Scenario 3 (Dr. Nair) data."""
    res = client.get("/api/web/scenarios?region=North%20Region&gender=Male")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["kpis"]["total_patients"] > 0
    assert "scenario1_clinical" in data
    assert "scenario2_lifestyle" in data
    assert "scenario3_population" in data
    assert len(data["scenario3_population"]["age_bmi_heatmap"]) > 0
    assert len(data["scenario1_clinical"]["scatter_points"]) > 0


def test_api_web_cohort_explorer_endpoint():
    """Verify GET /api/web/cohort-explorer returns filtered patient records."""
    res = client.get("/api/web/cohort-explorer?condition=multimorbid&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total_matched"] > 0
    assert len(data["records"]) <= 10
    assert data["records"][0]["multimorbidity"] >= 2


def test_api_rasp_isolation_and_anti_llm_middleware():
    """Verify Backend Isolation headers, RASP telemetry endpoint, and Anti-LLM crawler blocking."""
    res = client.get("/api/security/rasp-status")
    assert res.status_code == 200
    assert res.headers.get("X-Backend-Isolation") == "ENFORCED-ZERO-TRUST-v6"
    assert res.headers.get("X-RASP-Protection") == "ACTIVE-REALTIME"
    assert res.headers.get("X-Anti-LLM-Trap") == "CANARY-ARMED"

    data = res.json()
    assert data["status"] == "PROTECTED"
    assert data["anti_tamper_rasp"]["code_integrity_intact"] is True

    # Unauthorized AI Crawler (GPTBot) is trapped with 403 and Canary Honeytoken
    bot_res = client.get("/api/web/summary", headers={"User-Agent": "Mozilla/5.0 (compatible; GPTBot/1.0)"})
    assert bot_res.status_code == 403
    assert bot_res.json()["status"] == "ANTI_LLM_TRAP_TRIGGERED"
    assert bot_res.json()["canary_honeytoken"].startswith("CANARY-TRAP-")

    # RASP blocks SSTI / SQLi attack in query string
    rasp_res = client.get("/api/web/cohort-explorer?search=UNION%20SELECT%20*%20FROM%20users")
    assert rasp_res.status_code == 403
    assert rasp_res.json()["status"] == "RASP_RUNTIME_SHIELD_BLOCKED"




