"""
PulsePoint Cyber-Medical Intelligence System
Synthetic Healthcare Demonstration Dataset Generator
Statistically conditioned on established epidemiological risk models (Framingham / NHANES / CDC BRFSS).
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple

def generate_synthetic_cohort(
    num_records: int = 6000,
    seed: int = 42,
    introduce_imperfections: bool = True
) -> pd.DataFrame:
    """
    Generates a realistic clinical cohort with realistic correlations between
    demographics, biomarkers, lifestyle factors, and multi-disease outcomes.
    
    Includes minor real-world data flaws (duplicates, missing values) when
    `introduce_imperfections` is True to test the validation pipeline.
    """
    np.random.seed(seed)
    
    # 1. Demographics
    patient_ids = [f"PT-{10000 + i}" for i in range(num_records)]
    ages = np.random.normal(loc=54.0, scale=16.0, size=num_records)
    ages = np.clip(ages, 18, 89).astype(int)
    
    genders = np.random.choice(["Male", "Female", "Other/Non-Binary"], size=num_records, p=[0.49, 0.49, 0.02])
    regions = np.random.choice(["North Region", "South Region", "East Region", "West Region", "Central Metro"], size=num_records, p=[0.22, 0.26, 0.20, 0.18, 0.14])

    # 2. Lifestyle Habits
    smoking_options = ["Never", "Former", "Current"]
    alcohol_options = ["None", "Moderate", "Heavy"]
    
    smoking_status = np.random.choice(smoking_options, size=num_records, p=[0.55, 0.28, 0.17])
    alcohol_consumption = np.random.choice(alcohol_options, size=num_records, p=[0.48, 0.42, 0.10])
    
    # Physical activity (minutes per week)
    activity_base = np.random.exponential(scale=110, size=num_records)
    physical_activity_mins = np.clip(activity_base, 0, 480).astype(int)

    # 3. Clinical Biomarkers with Age & Lifestyle correlations
    # BMI: centered around 27.5 with right-skew
    bmi_noise = np.random.normal(0, 4.5, size=num_records)
    bmi = 26.5 + (ages / 60.0) * 1.5 - (physical_activity_mins / 300.0) * 2.0 + bmi_noise
    bmi = np.clip(np.round(bmi, 1), 16.0, 52.0)

    # Blood Pressure (correlated with age, BMI, smoking, alcohol)
    sbp_base = 105.0 + (ages * 0.45) + (bmi * 0.55)
    sbp_noise = np.random.normal(0, 12, size=num_records)
    sbp_smk = np.where(smoking_status == "Current", 6.0, 0.0)
    sbp_alc = np.where(alcohol_consumption == "Heavy", 7.0, 0.0)
    systolic_bp = np.clip(np.round(sbp_base + sbp_noise + sbp_smk + sbp_alc), 88, 215).astype(int)

    dbp_base = 65.0 + (ages * 0.18) + (bmi * 0.40)
    dbp_noise = np.random.normal(0, 8, size=num_records)
    diastolic_bp = np.clip(np.round(dbp_base + dbp_noise), 55, 128).astype(int)
    # Ensure SBP > DBP by at least 20 mmHg
    systolic_bp = np.maximum(systolic_bp, diastolic_bp + 22)

    # Total, HDL, and LDL Cholesterol
    total_chol_base = 165.0 + (ages * 0.5) + (bmi * 0.6) + np.random.normal(0, 26, size=num_records)
    cholesterol_total = np.clip(np.round(total_chol_base, 1), 110.0, 345.0)

    hdl_base = 56.0 - (bmi * 0.35) + (physical_activity_mins / 50.0) * 1.8 + np.random.normal(0, 8, size=num_records)
    hdl_gender = np.where(genders == "Female", 5.0, 0.0)
    cholesterol_hdl = np.clip(np.round(hdl_base + hdl_gender, 1), 22.0, 92.0)

    cholesterol_ldl = np.clip(np.round(cholesterol_total - cholesterol_hdl - 25.0, 1), 50.0, 240.0)
    cholesterol_ratio = np.round(cholesterol_total / np.maximum(cholesterol_hdl, 1.0), 2)

    # Glucose & HbA1c (correlated with BMI, Age, and Activity)
    glucose_base = 78.0 + (bmi * 0.8) + (ages * 0.25) - (physical_activity_mins / 100.0) * 3.0 + np.random.normal(0, 24, size=num_records)
    fasting_glucose = np.clip(np.round(glucose_base, 1), 65.0, 290.0)
    
    hba1c_base = 4.4 + (fasting_glucose / 32.0) + np.random.normal(0, 0.35, size=num_records)
    hba1c = np.clip(np.round(hba1c_base, 2), 4.2, 13.5)

    # 4. Symptoms
    fatigue_prob = 1 / (1 + np.exp(-( -1.8 + (bmi > 30)*0.7 + (fasting_glucose > 130)*0.9 + (ages > 60)*0.5 )))
    fatigue_reported = (np.random.rand(num_records) < fatigue_prob).astype(int)

    chest_pain_choices = ["None", "Typical Angina", "Atypical Angina", "Non-Anginal"]
    chest_pain_weights = [0.72, 0.10, 0.11, 0.07]
    chest_pain_type = np.random.choice(chest_pain_choices, size=num_records, p=chest_pain_weights)

    dizziness_prob = 1 / (1 + np.exp(-( -2.2 + (systolic_bp > 150)*0.8 + (ages > 65)*0.7 + (smoking_status == 'Current')*0.4 )))
    dizziness_reported = (np.random.rand(num_records) < dizziness_prob).astype(int)

    sob_prob = 1 / (1 + np.exp(-( -2.0 + (bmi > 32)*0.8 + (systolic_bp > 145)*0.6 + (smoking_status == 'Current')*0.9 )))
    shortness_of_breath = (np.random.rand(num_records) < sob_prob).astype(int)

    # 5. Realistic Clinical Outcome Equations
    # Heart Disease Probability (Logistic equation calibrated for ~14-16% baseline prevalence)
    hd_logit = (
        -4.6
        + 0.045 * (ages - 50)
        + 0.018 * (systolic_bp - 120)
        + 0.012 * (cholesterol_ldl - 100)
        + 0.45 * (smoking_status == "Current")
        + 0.22 * (smoking_status == "Former")
        + 0.35 * (genders == "Male")
        + 0.95 * (chest_pain_type == "Typical Angina")
        + 0.45 * (chest_pain_type == "Atypical Angina")
        + 0.03 * (bmi - 25)
    )
    hd_prob = 1 / (1 + np.exp(-hd_logit))
    heart_disease = (np.random.rand(num_records) < hd_prob).astype(int)

    # Diabetes Probability (calibrated for ~12-14% baseline prevalence)
    diab_logit = (
        -5.2
        + 0.035 * (fasting_glucose - 100)
        + 0.85 * (hba1c - 5.7)
        + 0.06 * (bmi - 25)
        + 0.02 * (ages - 50)
        - 0.003 * physical_activity_mins
    )
    diab_prob = 1 / (1 + np.exp(-diab_logit))
    diabetes = (np.random.rand(num_records) < diab_prob).astype(int)

    # Stroke Probability (calibrated for ~6-8% baseline prevalence)
    stroke_logit = (
        -5.5
        + 0.055 * (ages - 55)
        + 0.022 * (systolic_bp - 130)
        + 0.010 * (fasting_glucose - 100)
        + 0.55 * (smoking_status == "Current")
        + 0.65 * heart_disease
        + 0.45 * diabetes
        + 0.50 * dizziness_reported
    )
    stroke_prob = 1 / (1 + np.exp(-stroke_logit))
    stroke = (np.random.rand(num_records) < stroke_prob).astype(int)

    # 6. Dates and Review Status
    end_date = datetime.now()
    dates = [
        (end_date - timedelta(days=int(np.random.uniform(1, 720)))).strftime("%Y-%m-%d")
        for _ in range(num_records)
    ]
    
    review_status_options = ["Reviewed", "Pending Specialist Review", "Follow-Up Scheduled"]
    review_status = np.random.choice(review_status_options, size=num_records, p=[0.68, 0.20, 0.12])

    # Assemble raw DataFrame
    df = pd.DataFrame({
        "patient_id": patient_ids,
        "age": ages,
        "gender": genders,
        "region": regions,
        "bmi": bmi,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "cholesterol_total": cholesterol_total,
        "cholesterol_hdl": cholesterol_hdl,
        "cholesterol_ldl": cholesterol_ldl,
        "fasting_glucose": fasting_glucose,
        "hba1c": hba1c,
        "smoking_status": smoking_status,
        "alcohol_consumption": alcohol_consumption,
        "physical_activity_mins": physical_activity_mins,
        "fatigue_reported": fatigue_reported,
        "chest_pain_type": chest_pain_type,
        "dizziness_reported": dizziness_reported,
        "shortness_of_breath": shortness_of_breath,
        "heart_disease": heart_disease,
        "diabetes": diabetes,
        "stroke": stroke,
        "assessment_date": dates,
        "review_status": review_status,
        "is_synthetic": 1
    })

    if introduce_imperfections:
        # Intentionally duplicate 15 records to demonstrate duplicate detection
        dup_indices = np.random.choice(df.index, size=15, replace=False)
        dup_rows = df.loc[dup_indices].copy()
        df = pd.concat([df, dup_rows], ignore_index=True)

        # Intentionally inject missing values in 0.5% of optional records
        for col in ["cholesterol_ldl", "physical_activity_mins", "alcohol_consumption"]:
            mask = np.random.rand(len(df)) < 0.005
            df.loc[mask, col] = np.nan

    return df
