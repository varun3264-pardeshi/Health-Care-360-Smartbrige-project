# PULSEPOINT OS v3.0 — CHRONIC DISEASE RISK ANALYSIS & TABLEAU INTELLIGENCE SYSTEM
### SmartBridge Healthcare Analytics, Interactive Tableau Studio & Cyber-Medical Command Center

[![Python Version](https://img.shields.io/badge/Python-3.10%20--%203.14-00f2fe.svg)](https://python.org)
[![Web App](https://img.shields.io/badge/Web%20App-Interactive%20Command%20Center-00f2fe.svg)](http://127.0.0.1:8000)
[![Frontend](https://img.shields.io/badge/Companion-Streamlit%20Cyber--UI-4facfe.svg)](https://streamlit.io)
[![API](https://img.shields.io/badge/Backend-FastAPI%20REST-00f5a0.svg)](https://fastapi.tiangolo.com)
[![Tableau](https://img.shields.io/badge/BI-Tableau%20(.twb%20%26%20.twbx)-ffaa00.svg)](tableau/)
[![Test Suite](https://img.shields.io/badge/Pytest-34%20Passed%20(100%25)-00f5a0.svg)](tests/)

---

## 1. Executive Summary & Problem Statement

**PulsePoint OS v3.0** addresses the growing prevalence of **Coronary Heart Disease**, **Type 2 Diabetes Mellitus**, and **Cerebrovascular Stroke** by enabling healthcare providers to identify high-risk patients at an early stage across **5,000 patient records**.

The platform analyzes:
- **Patient Demographics:** Age, Age Group (`18-35`, `36-50`, `51-65`, `65+`), Gender, Geographic Region
- **Clinical Indicators:** Body Mass Index (`BMI` & `BMI Category`), Systolic & Diastolic Blood Pressure (`AHA BP Category`), Total/HDL/LDL Cholesterol, Fasting Glucose & HbA1c (`ADA Glucose Category`)
- **Lifestyle Behaviors:** Tobacco Smoking Status (`Never`, `Former`, `Current`), Alcohol Consumption (`None`, `Moderate`, `Heavy`), Physical Activity & Exercise Level (`Sedentary`, `Lightly Active`, `Active`)
- **Clinical Symptoms:** Chest Pain (`Typical Angina`, `Atypical Angina`, `Non-Anginal`), Chronic Fatigue, Dizziness Pattern, Shortness of Breath

---

## 2. Quickstart Launch Instructions

### Option A: Launch the Interactive Web Application & Tableau Command Center (Recommended)
```bash
python app.py
```
- **Live Command Center UI:** **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
- **Interactive OpenAPI Documentation:** **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Option B: Launch Both Web API/UI (`:8000`) & Streamlit Companion (`:8501`)
```bash
python run_system.py --mode all
```

---

## 3. Three Stakeholder Scenarios Implemented (SmartBridge Rubric)

### Scenario 1: Dr. Michael Carter — *Clinical Risk Assessment Officer*
- **Focus:** Early identification of high-risk individuals via BMI, Blood Pressure, Cholesterol, and Glucose biomarkers.
- **Interactive Visualizations:**
  - `1A.` Blood Pressure Stage (AHA) vs. Chronic Disease Rate (%)
  - `1B.` Glycemic Tier (Fasting Glucose / HbA1c) vs. Disease Rate (%)
  - `1C.` **Interactive 2D Patient Biomarker Scatter (`Systolic BP vs. Fasting Glucose`)** — click any patient point to load their EHR record!
  - `1D.` Clinical Indicator Shift: Disease-Positive vs. Disease-Negative Mean Biomarkers

### Scenario 2: Emily Rodriguez — *Healthcare Data Analyst*
- **Focus:** Uncovering correlations between lifestyle behaviors (Smoking, Alcohol consumption, Exercise levels) and chronic disease occurrence.
- **Interactive Visualizations:**
  - `2A.` Tobacco Smoking Status (`Never`, `Former`, `Current`) vs. Disease Prevalence (%)
  - `2B.` Physical Activity & Exercise Level (`Sedentary`, `Lightly Active`, `Active`) Protective Gradient (%)
  - `2C.` Alcohol Consumption Intensity (`None`, `Moderate`, `Heavy`) Dose-Response (%)
  - `2D.` **5-Axis Behavioral Risk Radar Chart (`Smoker + Sedentary` vs. `Non-Smoker + Active`)**

### Scenario 3: Dr. Priya Nair — *Public Health Researcher*
- **Focus:** Studying population-wide disease distributions across Age groups, BMI categories, and clinical symptoms to identify vulnerable populations.
- **Interactive Visualizations:**
  - `3A.` Age Cohort Disease Trajectory (`18–35` to `65+` Years Multi-Line Trend)
  - `3B.` BMI Category Vulnerability Distribution (%)
  - `3C.` Clinical Symptom Surveillance (`Chest Pain / Angina`, `Chronic Fatigue`, `Dizziness`)
  - `3D.` **Clickable 2D Age Group × BMI Category Vulnerability Heatmap** — click any cell to cross-filter the entire dashboard!

---

## 4. Advanced Cyber-Medical Command Center Modules

1. **Interactive Visual Tableau Storyboard (with `▶ Auto-Play Story`):**
   - 5 data-driven Story Points with a dynamically morphing chart (`Bar` $\rightarrow$ `Line` $\rightarrow$ `ROI Comparison`), 4 telemetry mini-cards, and 1-click **Tableau Public Live Embed** mode.
2. **Anatomical Organ Digital Twin (Interactive SVG HUD):**
   - Real-time human body schematic mapping biomarker risk to **Cerebral (Stroke)**, **Coronary (Heart Disease)**, **Glycemic (Pancreas/Diabetes)**, and **Arterial (MAP/BP)** organ nodes with dynamic pulse rings.
3. **Multi-Condition AI Risk Predictor & Counterfactual Sliders:**
   - Calibrated Random Forest & biophysical inference with real-time **What-If Intervention Sliders** (`Systolic BP Reduction` and `BMI Reduction`).
4. **Live 5,000-Patient Cohort Explorer (`⚡ Simulate` & `📥 Export Filtered CSV`):**
   - Filter by disease condition, search by Patient ID or Region, export filtered subsets to CSV, or click **`⚡ Simulate`** on any row to load that patient into the AI Risk Predictor and Organ Digital Twin.
5. **Protected Patient 360 & Real-Time Clinical Alert Center:**
   - Server-side RBAC-protected EHR lookup, physician review workflow, and 1-click alert resolution.

---

## 5. Tableau Enterprise Integration Artifacts

- **Tableau Workbook (`.twb`):** [`tableau/Chronic_Disease_Intelligence.twb`](file:///c:/Users/HP/Downloads/smartbridge%20project/tableau/Chronic_Disease_Intelligence.twb)
- **Tableau Packaged Workbook (`.twbx`):** [`tableau/Chronic_Disease_Intelligence.twbx`](file:///c:/Users/HP/Downloads/smartbridge%20project/tableau/Chronic_Disease_Intelligence.twbx)
- **Tableau-Ready Cleaned Dataset (5,000 rows):** [`data/processed/chronic_disease_tableau_ready.csv`](file:///c:/Users/HP/Downloads/smartbridge%20project/data/processed/chronic_disease_tableau_ready.csv)
- **Tableau Data Dictionary:** [`tableau/chronic_disease_data_dictionary.csv`](file:///c:/Users/HP/Downloads/smartbridge%20project/tableau/chronic_disease_data_dictionary.csv)
- **Verified Calculated Fields:** [`tableau/calculated_fields.txt`](file:///c:/Users/HP/Downloads/smartbridge%20project/tableau/calculated_fields.txt)
- **Step-by-Step Tableau Public Guide:** [`tableau/TABLEAU_WORKBOOK_GUIDE.md`](file:///c:/Users/HP/Downloads/smartbridge%20project/tableau/TABLEAU_WORKBOOK_GUIDE.md)
- **SmartBridge Project Report:** [`docs/SMARTBRIDGE_PROJECT_REPORT.md`](file:///c:/Users/HP/Downloads/smartbridge%20project/docs/SMARTBRIDGE_PROJECT_REPORT.md)
- **Executive Clinical PDF Report:** [`reports/pulsepoint_executive_report_latest.pdf`](file:///c:/Users/HP/Downloads/smartbridge%20project/reports/pulsepoint_executive_report_latest.pdf)

---

## 6. Automated Testing (34/34 Passed)

Run the complete test suite:
```bash
python -m pytest -v
```

---

## 7. Demo Credentials & RBAC Roles

| Username | Password | Role | Permissions |
| :--- | :--- | :--- | :--- |
| `dr_chen` | `Clinician@2026!` | **Authorized Clinician** | View Dashboards, Patient 360, Manage Alerts, Patient Exports |
| `admin` | `Admin@2026!` | **Administrator** | Full Access: Train Models, Audit Logs, Users, Exports |
| `analyst_sarah` | `Analyst@2026!` | **Healthcare Analyst** | View Dashboards, Train Models, Aggregate Exports, Alert Review |
| `researcher_alex`| `Research@2026!` | **Researcher** | Dashboards, De-Identified Pseudonymized Cohort Exports |
| `viewer_guest` | `Viewer@2026!` | **Read-only Viewer** | View Basic Dashboards only (Exports & Patient 360 Blocked) |
