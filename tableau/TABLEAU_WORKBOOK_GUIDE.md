# SMARTBRIDGE TABLEAU PROJECT GUIDE — CHRONIC DISEASE RISK ANALYSIS
### Heart Disease, Diabetes & Stroke Across 3 Stakeholder Scenarios

---

## 1. Quick Files Overview
- **Cleaned Dataset (5,000 Patients):** [`data/processed/chronic_disease_tableau_ready.csv`](file:///c:/Users/HP/Downloads/smartbridge%20project/data/processed/chronic_disease_tableau_ready.csv)
- **Pre-Built Tableau Workbook (`.twb`):** [`tableau/Chronic_Disease_Intelligence.twb`](file:///c:/Users/HP/Downloads/smartbridge%20project/tableau/Chronic_Disease_Intelligence.twb)
- **Calculated Fields Reference:** [`tableau/calculated_fields.txt`](file:///c:/Users/HP/Downloads/smartbridge%20project/tableau/calculated_fields.txt)
- **Web Application Entrypoint:** [`app.py`](file:///c:/Users/HP/Downloads/smartbridge%20project/app.py) (`python app.py` $\rightarrow$ `http://127.0.0.1:8000`)

---

## 2. How to Open or Publish in Tableau Public / Desktop

1. Open **Tableau Public** or **Tableau Desktop**.
2. You can directly open **`tableau/Chronic_Disease_Intelligence.twb`**, OR connect fresh to **`data/processed/chronic_disease_tableau_ready.csv`** via **Connect $\rightarrow$ Text File**.

---

## 3. Calculated Fields (Analysis $\rightarrow$ Create Calculated Field)

1. **`Heart Disease Prevalence %`**
   ```tableau
   SUM([heart_disease]) / COUNT([patient_id]) * 100
   ```
2. **`Diabetes Prevalence %`**
   ```tableau
   SUM([diabetes]) / COUNT([patient_id]) * 100
   ```
3. **`Stroke Prevalence %`**
   ```tableau
   SUM([stroke]) / COUNT([patient_id]) * 100
   ```
4. **`High Risk Patient Flag`**
   ```tableau
   IF [systolic_bp] >= 140 OR [fasting_glucose] >= 126 OR [bmi] >= 30 OR [multimorbidity_count] >= 1
   THEN "High Risk"
   ELSE "Low/Moderate Risk"
   END
   ```

---

## 4. Three Scenario Dashboards (SmartBridge Rubric)

### Scenario 1 Dashboard: Dr. Michael Carter — *Clinical Risk Assessment Officer*
- **Objective:** Identify high-risk patients early using BMI, Blood Pressure, Cholesterol, and Glucose levels.
- **Sheet 1 (`Sc1_BP_Category_vs_Disease_Prevalence`):**
  - **Columns:** `bp_category`
  - **Rows:** `Measure Values` (`Heart Disease Prevalence %`, `Diabetes Prevalence %`, `Stroke Prevalence %`)
  - **Marks:** Side-by-Side Bar Chart
- **Sheet 2 (`Sc1_Glucose_Category_vs_Diabetes`):**
  - **Columns:** `glucose_category`
  - **Rows:** `Diabetes Prevalence %`, `AVG(hba1c)`
  - **Marks:** Dual-Axis Bar + Line Chart
- **Sheet 3 (`Sc1_Cholesterol_and_BMI_Risk_Profile`):**
  - **Columns:** `High Risk Patient Flag`
  - **Rows:** `AVG(cholesterol_total)`, `AVG(systolic_bp)`, `AVG(bmi)`
  - **Marks:** Bar Chart with Labels

---

### Scenario 2 Dashboard: Emily Rodriguez — *Healthcare Data Analyst*
- **Objective:** Uncover correlations between lifestyle behaviors (Smoking, Alcohol consumption, Exercise levels) and chronic diseases.
- **Sheet 4 (`Sc2_Smoking_Habit_vs_Chronic_Disease`):**
  - **Columns:** `smoking_status` (`Never`, `Former`, `Current`)
  - **Rows:** `Heart Disease Prevalence %`, `Stroke Prevalence %`
  - **Marks:** Grouped Bar Chart
- **Sheet 5 (`Sc2_Exercise_Level_vs_Diabetes`):**
  - **Columns:** `exercise_level` (`Sedentary (<60m)`, `Lightly Active (60-149m)`, `Active (>=150m)`)
  - **Rows:** `Diabetes Prevalence %`, `Heart Disease Prevalence %`
  - **Marks:** Bar Chart
- **Sheet 6 (`Sc2_Alcohol_Consumption_Impact`):**
  - **Columns:** `alcohol_consumption` (`None`, `Moderate`, `Heavy`)
  - **Rows:** `Stroke Prevalence %`, `Heart Disease Prevalence %`, `Diabetes Prevalence %`

---

### Scenario 3 Dashboard: Dr. Priya Nair — *Public Health Researcher*
- **Objective:** Study population-wide disease patterns across Age groups, BMI categories, and Symptoms (`Chest Pain`, `Fatigue`, `Dizziness`).
- **Sheet 7 (`Sc3_Age_Group_Disease_Trend`):**
  - **Columns:** `age_group` (`18-35`, `36-50`, `51-65`, `65+`)
  - **Rows:** `Heart Disease Prevalence %`, `Diabetes Prevalence %`, `Stroke Prevalence %`
  - **Marks:** Multi-Line Trend Chart
- **Sheet 8 (`Sc3_Age_x_BMI_Vulnerability_Heatmap`):**
  - **Columns:** `age_group`
  - **Rows:** `bmi_category`
  - **Color & Text Label:** `AVG(multimorbidity_count)` or `% of High Risk Patients`
  - **Marks:** Square (Highlight Table / Heatmap)
- **Sheet 9 (`Sc3_Symptom_Chest_Pain_Fatigue_Dizziness`):**
  - **Columns:** `chest_pain_type`, `fatigue_reported`, `dizziness_reported`
  - **Rows:** `Heart Disease Prevalence %`, `Stroke Prevalence %`

---

## 5. Tableau Story (`Story_Chronic_Disease_Risk_Intelligence`)

Create a **New Story** in Tableau and add **5 Story Points**:
1. **Executive Overview:** Overall Chronic Disease Burden (5,000 Patients: Diabetes 10.6%, Heart Disease 6.9%, Stroke 1.7%).
2. **Scenario 1 (Dr. Michael Carter):** Clinical Indicators — Hypertension Stage 2/Crisis & Hyperglycemia Thresholds.
3. **Scenario 2 (Emily Rodriguez):** Behavioral Drivers — Tobacco Smoking & Sedentary Activity Impact.
4. **Scenario 3 (Dr. Priya Nair):** Vulnerable Demographics — Age 65+ & Obesity Class I/II Heatmap + Angina/Fatigue Symptoms.
5. **Action Plan:** Early Screening & Preventive Resource Allocation.

---

## 6. Embedding into the Web Application
1. Run the web application:
   ```bash
   python app.py
   ```
2. Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.
3. All 3 Scenario Dashboards and the 5-Point Story work **immediately** out of the box using live data from `chronic_disease_tableau_ready.csv`.
4. If you publish to **Tableau Public**, click **🌐 Tableau Public Live Embed** on the Dashboard or Story section and paste your Tableau Public Share Link to embed your hosted Tableau Public view directly!
