"""
PulsePoint Cyber-Medical Intelligence System
Data Exporter, Ingestion & Clinical Alert Trigger Engine
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from core.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, TABLEAU_DIR, DB_PATH
from core.database import get_connection, execute_db, query_db, init_database
from data_pipeline.synthetic_generator import generate_synthetic_cohort
from data_pipeline.validator import DataValidator
from data_pipeline.feature_engineering import engineer_features

RAW_FILE_PATH = RAW_DATA_DIR / "chronic_disease_raw.csv"
CLEANED_FILE_PATH = PROCESSED_DATA_DIR / "chronic_disease_cleaned.csv"
TABLEAU_FILE_PATH = PROCESSED_DATA_DIR / "chronic_disease_tableau_ready.csv"
DICTIONARY_FILE_PATH = TABLEAU_DIR / "chronic_disease_data_dictionary.csv"


DATA_DICTIONARY_ROWS = [
    {"Column_Name": "patient_id", "Data_Type": "String", "Description": "Synthetic Unique Patient Identifier (e.g. PT-10042)", "Unit": "N/A"},
    {"Column_Name": "age", "Data_Type": "Integer", "Description": "Patient age in completed years", "Unit": "Years"},
    {"Column_Name": "gender", "Data_Type": "String", "Description": "Self-reported gender identity", "Unit": "Categories (Male/Female/Other)"},
    {"Column_Name": "region", "Data_Type": "String", "Description": "Healthcare network administrative geographic region", "Unit": "Region name"},
    {"Column_Name": "bmi", "Data_Type": "Float", "Description": "Body Mass Index (weight in kg / height in meters squared)", "Unit": "kg/m^2"},
    {"Column_Name": "bmi_category", "Data_Type": "String", "Description": "WHO standard BMI clinical category", "Unit": "Underweight/Normal/Overweight/Obesity"},
    {"Column_Name": "systolic_bp", "Data_Type": "Integer", "Description": "Resting Systolic Blood Pressure", "Unit": "mmHg"},
    {"Column_Name": "diastolic_bp", "Data_Type": "Integer", "Description": "Resting Diastolic Blood Pressure", "Unit": "mmHg"},
    {"Column_Name": "bp_category", "Data_Type": "String", "Description": "2017 AHA/ACC clinical blood pressure category", "Unit": "Normal/Elevated/Stage 1/Stage 2/Crisis"},
    {"Column_Name": "mean_arterial_pressure", "Data_Type": "Float", "Description": "Calculated Mean Arterial Pressure (DBP + PP/3)", "Unit": "mmHg"},
    {"Column_Name": "pulse_pressure", "Data_Type": "Integer", "Description": "Calculated Pulse Pressure (SBP - DBP)", "Unit": "mmHg"},
    {"Column_Name": "cholesterol_total", "Data_Type": "Float", "Description": "Total serum cholesterol concentration", "Unit": "mg/dL"},
    {"Column_Name": "cholesterol_hdl", "Data_Type": "Float", "Description": "High-Density Lipoprotein serum concentration", "Unit": "mg/dL"},
    {"Column_Name": "cholesterol_ldl", "Data_Type": "Float", "Description": "Low-Density Lipoprotein serum concentration", "Unit": "mg/dL"},
    {"Column_Name": "cholesterol_ratio", "Data_Type": "Float", "Description": "Atherogenic index ratio (Total Chol / HDL)", "Unit": "Ratio"},
    {"Column_Name": "fasting_glucose", "Data_Type": "Float", "Description": "Fasting blood glucose concentration", "Unit": "mg/dL"},
    {"Column_Name": "glucose_category", "Data_Type": "String", "Description": "ADA Fasting Glucose Diagnostic Category", "Unit": "Normal/Prediabetes/Diabetes"},
    {"Column_Name": "hba1c", "Data_Type": "Float", "Description": "Glycated Hemoglobin concentration", "Unit": "%"},
    {"Column_Name": "smoking_status", "Data_Type": "String", "Description": "Current tobacco smoking history", "Unit": "Never/Former/Current"},
    {"Column_Name": "alcohol_consumption", "Data_Type": "String", "Description": "Self-reported alcohol intake intensity", "Unit": "None/Moderate/Heavy"},
    {"Column_Name": "physical_activity_mins", "Data_Type": "Integer", "Description": "Moderate-to-vigorous exercise per week", "Unit": "Minutes/week"},
    {"Column_Name": "exercise_level", "Data_Type": "String", "Description": "WHO aerobic recommendation adherence", "Unit": "Sedentary/Lightly Active/Active"},
    {"Column_Name": "fatigue_reported", "Data_Type": "Integer", "Description": "Persistent clinical fatigue symptom (1=Yes, 0=No)", "Unit": "Binary flag"},
    {"Column_Name": "chest_pain_type", "Data_Type": "String", "Description": "Clinical angina classification", "Unit": "None/Typical Angina/Atypical Angina/Non-Anginal"},
    {"Column_Name": "dizziness_reported", "Data_Type": "Integer", "Description": "Episodes of lightheadedness or vertigo (1=Yes, 0=No)", "Unit": "Binary flag"},
    {"Column_Name": "shortness_of_breath", "Data_Type": "Integer", "Description": "Exertional dyspnea (1=Yes, 0=No)", "Unit": "Binary flag"},
    {"Column_Name": "heart_disease", "Data_Type": "Integer", "Description": "Confirmed coronary/myocardial heart condition (1=Yes, 0=No)", "Unit": "Binary outcome"},
    {"Column_Name": "diabetes", "Data_Type": "Integer", "Description": "Confirmed Type 2 Diabetes diagnosis (1=Yes, 0=No)", "Unit": "Binary outcome"},
    {"Column_Name": "stroke", "Data_Type": "Integer", "Description": "Documented cerebrovascular event / stroke (1=Yes, 0=No)", "Unit": "Binary outcome"},
    {"Column_Name": "multimorbidity_count", "Data_Type": "Integer", "Description": "Sum of diagnosed chronic conditions (0 to 3)", "Unit": "Count"},
    {"Column_Name": "data_completeness_pct", "Data_Type": "Float", "Description": "Calculated patient record completeness percentage", "Unit": "Percentage"},
    {"Column_Name": "assessment_date", "Data_Type": "Date", "Description": "Assessment clinical visit date", "Unit": "YYYY-MM-DD"},
    {"Column_Name": "review_status", "Data_Type": "String", "Description": "Clinical review workflow stage", "Unit": "Reviewed/Pending/Follow-Up Scheduled"},
    {"Column_Name": "is_synthetic", "Data_Type": "Integer", "Description": "De-identification / Demonstration marker flag (Always 1)", "Unit": "Binary flag"}
]


def generate_and_ingest_data(num_records: int = 6000, seed: int = 42) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Complete end-to-end data pipeline execution:
    1. Generates synthetic cohort
    2. Saves raw CSV
    3. Runs validator and cleaner
    4. Engineers clinical features
    5. Exports cleaned & Tableau-ready CSVs and Data Dictionary
    6. Ingests into SQLite database
    7. Evaluates and registers clinical threshold alerts
    """
    init_database()

    # Step 1: Generate Raw Cohort
    raw_df = generate_synthetic_cohort(num_records=num_records, seed=seed, introduce_imperfections=True)
    raw_df.to_csv(RAW_FILE_PATH, index=False)

    # Step 2: Validate & Clean
    validator = DataValidator(raw_df)
    clean_df, quality_metrics = validator.validate_and_clean()

    # Step 3: Feature Engineering
    engineered_df = engineer_features(clean_df)

    # Step 4: Export Processed Datasets
    engineered_df.to_csv(CLEANED_FILE_PATH, index=False)
    engineered_df.to_csv(TABLEAU_FILE_PATH, index=False)

    # Save Data Dictionary
    dict_df = pd.DataFrame(DATA_DICTIONARY_ROWS)
    dict_df.to_csv(DICTIONARY_FILE_PATH, index=False)

    # Step 5: Ingest into SQLite
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patient_records;") # Refresh table
    
    insert_sql = """
    INSERT INTO patient_records (
        patient_id, age, gender, region, bmi, bmi_category,
        systolic_bp, diastolic_bp, bp_category,
        cholesterol_total, cholesterol_hdl, cholesterol_ldl, cholesterol_ratio,
        fasting_glucose, glucose_category, hba1c,
        smoking_status, alcohol_consumption, physical_activity_mins, exercise_level,
        fatigue_reported, chest_pain_type, dizziness_reported, shortness_of_breath,
        heart_disease, diabetes, stroke, multimorbidity_count,
        data_completeness_pct, assessment_date, review_status, is_synthetic
    ) VALUES (
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?, ?, ?
    )
    """

    records_to_insert = []
    for _, r in engineered_df.iterrows():
        records_to_insert.append((
            str(r["patient_id"]), int(r["age"]), str(r["gender"]), str(r["region"]),
            float(r["bmi"]), str(r["bmi_category"]),
            int(r["systolic_bp"]), int(r["diastolic_bp"]), str(r["bp_category"]),
            float(r["cholesterol_total"]), float(r["cholesterol_hdl"]), float(r["cholesterol_ldl"]), float(r["cholesterol_ratio"]),
            float(r["fasting_glucose"]), str(r["glucose_category"]), float(r["hba1c"]),
            str(r["smoking_status"]), str(r["alcohol_consumption"]), int(r["physical_activity_mins"]), str(r["exercise_level"]),
            int(r["fatigue_reported"]), str(r["chest_pain_type"]), int(r["dizziness_reported"]), int(r["shortness_of_breath"]),
            int(r["heart_disease"]), int(r["diabetes"]), int(r["stroke"]), int(r["multimorbidity_count"]),
            float(r["data_completeness_pct"]), str(r["assessment_date"]), str(r["review_status"]), 1
        ))

    cursor.executemany(insert_sql, records_to_insert)
    conn.commit()

    # Step 6: Trigger Initial Clinical Alerts
    trigger_clinical_alerts(engineered_df, conn)
    conn.close()

    return engineered_df, quality_metrics


def trigger_clinical_alerts(df: pd.DataFrame, conn: sqlite3.Connection) -> int:
    """
    Evaluates evidence-based clinical rules and registers high-priority alerts in database.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clinical_alerts;") # Reset alerts on new ingestion

    alert_inserts = []
    now_str = pd.Timestamp.now().isoformat()

    for _, r in df.iterrows():
        pid = str(r["patient_id"])
        
        # Rule 1: Hypertensive Crisis / Severe Blood Pressure (SBP >= 175 or DBP >= 110)
        if r["systolic_bp"] >= 175 or r["diastolic_bp"] >= 110:
            alert_inserts.append((
                pid, "CARDIAC_CRITICAL", "CRITICAL",
                f"Severe Hypertensive Crisis Warning ({r['systolic_bp']}/{r['diastolic_bp']} mmHg)",
                f"Patient exhibits resting BP of {r['systolic_bp']}/{r['diastolic_bp']} mmHg exceeding crisis threshold. Immediate clinical evaluation advised.",
                "RULE_BP_CRISIS", "ACTIVE", now_str
            ))

        # Rule 2: Severe Hyperglycemia (Fasting Glucose >= 220 mg/dL or HbA1c >= 10.5%)
        elif r["fasting_glucose"] >= 220 or r["hba1c"] >= 10.5:
            alert_inserts.append((
                pid, "GLYCEMIC_CRITICAL", "HIGH",
                f"Severe Glycemic Dysregulation (HbA1c: {r['hba1c']}%, Glucose: {r['fasting_glucose']} mg/dL)",
                f"Marked diabetic decompensation. Fasting glucose is {r['fasting_glucose']} mg/dL with HbA1c {r['hba1c']}%.",
                "RULE_GLUCOSE_SEVERE", "ACTIVE", now_str
            ))

        # Rule 3: High-Risk Cerebrovascular Symptom Cluster (SBP >= 150 + Glucose >= 140 + Smoking + Dizziness)
        elif r["systolic_bp"] >= 150 and r["fasting_glucose"] >= 140 and r["smoking_status"] == "Current" and r["dizziness_reported"] == 1:
            alert_inserts.append((
                pid, "STROKE_WARNING", "HIGH",
                "Elevated Cerebrovascular Risk Cluster Detected",
                "Co-occurrence of Stage 2 Hypertension, elevated glucose, active smoking, and frequent dizziness indicates critical stroke vulnerability.",
                "RULE_STROKE_CLUSTER", "ACTIVE", now_str
            ))

        # Rule 4: High Multimorbidity Burden (Count >= 2 with Angina or Dyspnea)
        elif r["multimorbidity_count"] >= 2 and (r["chest_pain_type"] in ["Typical Angina", "Atypical Angina"] or r["shortness_of_breath"] == 1):
            alert_inserts.append((
                pid, "MULTIMORBIDITY_BURDEN", "MEDIUM",
                f"Multimorbidity Burden with Cardiorespiratory Symptoms (Conditions: {r['multimorbidity_count']})",
                f"Patient presents with {r['multimorbidity_count']} concurrent chronic conditions alongside symptomatic angina or exertional dyspnea.",
                "RULE_MULTIMORBIDITY", "ACTIVE", now_str
            ))

    if alert_inserts:
        cursor.executemany(
            """
            INSERT INTO clinical_alerts (patient_id, alert_type, severity, title, description, rule_code, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            alert_inserts
        )
        conn.commit()

    return len(alert_inserts)


def load_dataset() -> pd.DataFrame:
    """Loads the processed dataset from CSV if available, or regenerates if missing."""
    if CLEANED_FILE_PATH.exists():
        return pd.read_csv(CLEANED_FILE_PATH)
    else:
        df, _ = generate_and_ingest_data()
        return df
