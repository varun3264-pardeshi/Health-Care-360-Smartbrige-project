# SMARTBRIDGE PROJECT DOCUMENTATION REPORT
## Title: Chronic Disease Risk Analysis & Healthcare Intelligence System (Heart Disease, Diabetes & Stroke)

---

## 1. Problem Statement & Motivation
The growing prevalence of chronic diseases such as **Heart Disease**, **Type 2 Diabetes**, and **Cerebrovascular Stroke** has created a major challenge for healthcare providers in identifying high-risk patients at an early stage. Delayed detection and fragmented understanding of health risk factors lead to severe medical complications, increased hospitalization costs, and reduced patient outcomes.

This project analyzes **5,000 patient records** covering:
- **Demographics:** Age, Age Group (`18-35`, `36-50`, `51-65`, `65+`), Gender, Geographic Region
- **Clinical Indicators:** Body Mass Index (`BMI` & `BMI Category`), Systolic & Diastolic Blood Pressure (`AHA BP Category`), Total/HDL/LDL Cholesterol, Fasting Glucose & HbA1c (`Glucose Category`)
- **Lifestyle Behaviors:** Smoking Status (`Never`, `Former`, `Current`), Alcohol Consumption (`None`, `Moderate`, `Heavy`), Physical Activity & Exercise Level (`Sedentary`, `Lightly Active`, `Active`)
- **Clinical Symptoms:** Chest Pain (`Typical Angina`, `Atypical Angina`, `Non-Anginal`), Chronic Fatigue, Dizziness Pattern, Shortness of Breath

---

## 2. Three Stakeholder Scenarios Implemented

### Scenario 1: Dr. Michael Carter — *Clinical Risk Assessment Officer*
- **Challenge:** Identifying high-risk patients early from complex biomarker records before acute cardiovascular or diabetic crises occur.
- **Tableau Dashboard Solution (`Dashboard_1_Scenario1_Clinical_Risk_Dr_Carter`):**
  - Interactive KPI cards tracking Total Patients (`5,000`), High-Risk Cohort (`64.2%`), Heart Disease (`6.9%`), Diabetes (`10.6%`), and Stroke (`1.7%`).
  - Blood Pressure Category (AHA) vs. Disease Prevalence chart showing a **2.5× surge** in Heart Disease and Stroke in Hypertension Stage 2 and Hypertensive Crisis.
  - Glycemic Status (`Normal`, `Prediabetes`, `Diabetes`) vs. Disease Prevalence & HbA1c distribution.
  - Mean Clinical Biomarker comparison between Disease-Positive and Disease-Negative patients.

### Scenario 2: Emily Rodriguez — *Healthcare Data Analyst*
- **Challenge:** Understanding how lifestyle habits (Smoking, Alcohol consumption, Exercise levels) influence chronic disease occurrence across patient segments.
- **Tableau Dashboard Solution (`Dashboard_2_Scenario2_Lifestyle_Emily_Rodriguez`):**
  - Smoking Habit (`Never`, `Former`, `Current`) comparative chart revealing that **Current Smokers** face **2× higher Heart Disease and Stroke rates**.
  - Exercise Level (`Sedentary <60m`, `Lightly Active 60-149m`, `Active >=150m`) trend analysis showing a **46% relative reduction** in Type 2 Diabetes among physically active individuals.
  - Alcohol Consumption (`None`, `Moderate`, `Heavy`) impact analysis on multimorbidity.

### Scenario 3: Dr. Priya Nair — *Public Health Researcher*
- **Challenge:** Studying population-wide disease distributions across Age groups, BMI categories, and clinical symptoms to identify vulnerable populations and design preventive health policies.
- **Tableau Dashboard Solution (`Dashboard_3_Scenario3_Population_Dr_Priya_Nair`):**
  - Multi-line Age Cohort progression (`18-35` $\rightarrow$ `65+`) showing steep escalation after age 50.
  - **2D Age Group × BMI Category Vulnerability Heatmap** identifying the highest-risk population segment (`Age 65+` × `Obesity Class I/II` at **>33% chronic disease prevalence**).
  - Symptom Prevalence chart demonstrating that patients reporting **Chest Pain (Angina)**, **Chronic Fatigue**, or **Dizziness** have **2.8× higher underlying cardiovascular risk**.

---

## 3. System Architecture & Deliverables

1. **Dataset (`data/processed/chronic_disease_tableau_ready.csv`):** Cleaned 5,000-patient dataset with standardized clinical categories and zero missing values.
2. **Tableau Workbook (`tableau/Chronic_Disease_Intelligence.twb`):** Pre-configured XML workbook containing 9 Worksheets, 5 Calculated Fields, 3 Scenario Dashboards, and 1 Storyboard.
3. **Web Application (`app.py` + `frontend/`):**
   - Built-in interactive cohort filter bar (`Region`, `Gender`, `Age Group`, `BMI Category`)
   - Live interactive charts for Scenario 1, Scenario 2, and Scenario 3
   - Interactive 5-Point Tableau Storyboard + One-Click **Tableau Public Live Embed** mode
   - Multi-Condition AI Risk Predictor & What-If Lifestyle Simulator
   - Patient 360 Lookup & Real-Time Clinical Alert Center

---

## 4. How to Run the Project

```bash
python app.py
```
Then open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.
