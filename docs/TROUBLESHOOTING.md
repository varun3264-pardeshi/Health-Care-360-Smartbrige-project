# PULSEPOINT CYBER-MEDICAL INTELLIGENCE — TROUBLESHOOTING & DIAGNOSTICS GUIDE

## 1. Port Conflicts

### Symptom: `Address already in use` (Port 8000 or 8501)
- **Diagnosis:** Another background process or server is bound to port 8000 (FastAPI) or 8501 (Streamlit).
- **Resolution:**
  Specify alternate ports when launching via `run_system.py`:
  ```bash
  python run_system.py --mode all --api-port 8080 --ui-port 8502
  ```

---

## 2. Database & Data Pipeline Anomalies

### Symptom: `Table patient_records not found`
- **Resolution:**
  Initialize and populate the SQLite database schema automatically:
  ```bash
  python -c "from data_pipeline.exporter import generate_and_ingest_data; generate_and_ingest_data()"
  ```

### Symptom: Missing Model Artifacts in `models/`
- **Resolution:**
  Execute the cross-validated model training module:
  ```bash
  python -m ml_engine.train
  ```

---

## 3. Authentication & Access Issues

### Symptom: `Access Denied` on Patient 360 Interface
- **Cause:** Current user profile holds `Healthcare Analyst`, `Researcher`, or `Read-only Viewer` role.
- **Resolution:** Click the **Switch Role** button in the top navigation bar and select **Authorized Clinician** (`dr_chen`) or **Administrator** (`admin`).

### Symptom: Deprecation Warnings on Python 3.14
- **Diagnosis:** Python 3.14 introduced warnings for `datetime.utcnow()` and NumPy array shape assignments.
- **Resolution:** All PulsePoint core codebase calls utilize `datetime.now(timezone.utc)` and Pydantic v2 `json_schema_extra` syntax. Third-party library warnings from older packages can be silenced in production using `PYTHONWARNINGS="ignore"`.
