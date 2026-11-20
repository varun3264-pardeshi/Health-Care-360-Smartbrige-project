# PULSEPOINT CYBER-MEDICAL INTELLIGENCE — SYSTEM ARCHITECTURE

## 1. Architectural Philosophy

PulsePoint is engineered as a decoupled, multi-tier clinical intelligence platform designed for population health surveillance, retrospective chronic disease risk analysis, and clinical decision support across three primary chronic conditions:
1. **Coronary Artery & Myocardial Heart Disease**
2. **Type 2 Diabetes Mellitus**
3. **Cerebrovascular Stroke**

```
+-----------------------------------------------------------------------------------+
|                        PULSEPOINT ENTERPRISE PLATFORM                             |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ PRESENTATION TIER ]                                                            |
|  +-------------------------------------+   +------------------------------------+ |
|  | Streamlit Cyber-Medical Command     |   | Tableau Enterprise Workspace       | |
|  | - Executive Overview (Dashboard A)  |   | - Chronic_Disease_Intelligence.twb | |
|  | - Clinical Risk Matrix (Dashboard B)|   | - 4 Core Population Worksheets     | |
|  | - Lifestyle & Symptoms (Dashboard C)|   | - Calculated Fields Specification  | |
|  | - Population Insights (Dashboard D) |   | - Interactive Cross-Filtering      | |
|  | - 3D Anatomical Organ Visualizer    |   +------------------------------------+ |
|  | - Multi-Condition Risk Simulator    |                                          |
|  | - Protected Patient 360 & Alerts    |                                          |
|  +-------------------------------------+                                          |
|                     ^                                                             |
|                     | Internal Service Calls / REST                               |
|                     v                                                             |
|  [ API & APPLICATION TIER ]                                                       |
|  +------------------------------------------------------------------------------+ |
|  | FastAPI Microservice Framework (Uvicorn ASGI)                                | |
|  | - /api/health          - /api/auth/login      - /api/analytics/summary       | |
|  | - /api/predict/{cond}  - /api/patients/{id}   - /api/alerts (PATCH/GET)      | |
|  | - Cryptographic RBAC Token Validation & Least-Privilege Role Guard          | |
|  +------------------------------------------------------------------------------+ |
|                     ^                                                             |
|                     | Data Flow & Ingestion                                       |
|                     v                                                             |
|  [ ANALYTICS & INFERENCE TIER ]                                                   |
|  +-------------------------------------+   +------------------------------------+ |
|  | Machine Learning Pipelines          |   | Automated Data Quality Pipeline    | |
|  | - Heart Disease RF (ROC-AUC: 0.72)  |   | - Schema & Type Validator          | |
|  | - Type 2 Diabetes RF (ROC-AUC: 0.84)|   | - Duplicate Reconciliation Engine  | |
|  | - Stroke RF (ROC-AUC: 0.82)         |   | - Outlier Clamping & Bounding      | |
|  | - Logistic Regression Baselines     |   | - Feature Engineering (MAP/PP/BMI) | |
|  | - Calibrated Risk Stratification    |   | - Quality Scoring (0 - 100)        | |
|  +-------------------------------------+   +------------------------------------+ |
|                     ^                                                             |
|                     | Queries & Transactions                                      |
|                     v                                                             |
|  [ PERSISTENCE & DATA GOVERNANCE TIER ]                                           |
|  +------------------------------------------------------------------------------+ |
|  | SQLite Local Database (healthcare_intelligence.db)                           | |
|  | - users (Salted PBKDF2 Hashed Passwords)                                     | |
|  | - patient_records (Demographics, Biomarkers, Conditions, Reviews)           | |
|  | - clinical_alerts (High BP Crises, Severe Glycemia, Symptom Clusters)        | |
|  | - data_quality_metrics (Completeness, Imputations, Corrections)              | |
|  | - model_metadata (Versioned Parameters, Telemetry, Gini Feature Importances)  | |
|  | - audit_events (Immutable Security, Access & Data Export Logs)              | |
|  +------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

---

## 2. Component Subsystems

### 2.1 Presentation Layer
- **Streamlit Cyber-Medical Dashboard (`ui/app.py`):**
  Renders responsive command center pages using custom Midnight Navy theme CSS tokens, electric cyan highlights, glassmorphic card containers, and Plotly charts.
- **Tableau Integration Studio (`tableau/`):**
  Provides genuine XML workbook artifacts (`.twb`), ready-to-import CSV datasets, and standardized calculated field formulas.

### 2.2 Service & Ingestion Layer
- **Data Pipeline (`data_pipeline/`):**
  Ingests raw cohort data, enforces schema typing, reconciles duplicate patient records, imputes missing values via domain-appropriate central tendency, clamps non-physiological anomalies, and derives clinical indicators (Mean Arterial Pressure, Pulse Pressure, Atherogenic Lipid Ratios).
- **FastAPI Engine (`api/`):**
  Exposes validated, typed OpenAPI endpoints with cryptographic Bearer token authentication, input sanitization, and role validation.

### 2.3 Machine Learning Inference Layer
- **ML Engine (`ml_engine/`):**
  Independent pipelines for Heart Disease, Diabetes, and Stroke using stratified 80/20 train/test partitions, scikit-learn `ColumnTransformer` preprocessing fitted exclusively on training folds to prevent data leakage, balanced class weighting, and optimal decision threshold calibration via Youden's J statistic.

### 2.4 Governance & Storage Layer
- **SQLite Engine (`core/database.py`):**
  Local relational database with parameterized query interfaces preventing SQL injection. Contains full auditing, patient reference tracking, and alert logs.
