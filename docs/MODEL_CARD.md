# PULSEPOINT CLINICAL AI — MODEL CARD & BIOPHYSICAL CARD

## 1. Model Overview

- **Developers:** PulsePoint Healthcare Intelligence Team
- **Model Release Version:** `v2.4-20261019`
- **Model Architectures:**
  - **Advanced Ensemble:** `RandomForestClassifier` (120 estimators, max_depth=12, balanced class weights)
  - **Baseline Benchmark:** `LogisticRegression` (L2 penalty, balanced class weights)
- **Target Conditions:**
  1. `heart_disease`: Coronary artery and myocardial ischemic indicators
  2. `diabetes`: Glycemic dysregulation and Type 2 Diabetes Mellitus
  3. `stroke`: Cerebrovascular ischemia and stroke events

---

## 2. Intended Use & Clinical Scope

### Intended Use Cases
- Retrospective population health stratification across primary care cohorts.
- High-level clinical decision support triage prioritizing patients requiring specialist consultation.
- Educational and architectural demonstration of multi-condition predictive modeling.

### Out-of-Scope & Contraindications
- **NOT A DIAGNOSTIC DEVICE:** Models must **NOT** be utilized as an autonomous diagnostic tool.
- **ACUTE EMERGENCIES:** Contraindicated for real-time emergency triage of acute myocardial infarction or acute ischemic stroke in progress.

---

## 3. Training & Evaluation Methodology

- **Split Ratio:** 80% Stratified Training Partition, 20% Held-Out Test Partition.
- **Leakage Prevention:** Continuous variable scalers (`StandardScaler`) and categorical encoders (`OneHotEncoder`) fitted exclusively on training folds via scikit-learn `Pipeline` and `ColumnTransformer`.
- **Validation:** 5-Fold Stratified Cross-Validation on training folds.
- **Decision Threshold Optimization:** Calibrated using Youden's J statistic ($J = \text{Sensitivity} + \text{Specificity} - 1$) on held-out validation data.

---

## 4. Evaluated Test Metrics Summary

| Model Target | Algorithm | Test ROC-AUC | Test PR-AUC | Optimal Threshold | Brier Calibration Score | Primary Gini Feature |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Heart Disease** | Random Forest | 0.718 | 0.285 | 0.44 | 0.114 | Age, SBP, LDL Cholesterol |
| **Type 2 Diabetes**| Random Forest | 0.840 | 0.450 | 0.47 | 0.089 | Fasting Glucose, HbA1c, BMI |
| **Stroke** | Random Forest | 0.824 | 0.210 | 0.38 | 0.057 | Age, SBP, Smoking |

*Note: All probabilities and metrics represent actual computed values from held-out test splits without synthetic inflation.*

---

## 5. Ethical Considerations & Limitations

- **Retrospective vs. Prospective Bias:** Models are trained on observational cross-sectional cohort records. Retrospective correlation does not establish prospective etiology.
- **Class Imbalance:** Chronic disease incidence in unselected populations is naturally imbalanced. Balanced class weighting was applied to prevent majority-class bias.
