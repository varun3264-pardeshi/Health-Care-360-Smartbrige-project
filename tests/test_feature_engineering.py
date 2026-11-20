"""
Unit Tests: Clinical Feature Engineering, Bins & Derived Hemodynamics
"""

import pytest
import pandas as pd
import numpy as np
from data_pipeline.feature_engineering import (
    categorize_bmi, categorize_blood_pressure, categorize_glucose,
    categorize_exercise, categorize_age, engineer_features
)

def test_categorize_bmi():
    """Verify WHO BMI standard classification."""
    assert categorize_bmi(16.5) == "Underweight"
    assert categorize_bmi(22.0) == "Normal"
    assert categorize_bmi(27.4) == "Overweight"
    assert categorize_bmi(32.1) == "Obesity Class I"
    assert categorize_bmi(38.5) == "Obesity Class II+"
    assert categorize_bmi(np.nan) == "Unknown"


def test_categorize_blood_pressure():
    """Verify 2017 AHA/ACC guidelines categorization."""
    assert categorize_blood_pressure(115, 75) == "Normal"
    assert categorize_blood_pressure(125, 75) == "Elevated"
    assert categorize_blood_pressure(135, 82) == "Hypertension Stage 1"
    assert categorize_blood_pressure(150, 95) == "Hypertension Stage 2"
    assert categorize_blood_pressure(190, 110) == "Hypertensive Crisis"
    assert categorize_blood_pressure(140, 125) == "Hypertensive Crisis"


def test_categorize_glucose():
    """Verify ADA diagnostic thresholds."""
    assert categorize_glucose(85.0) == "Normal"
    assert categorize_glucose(110.0) == "Prediabetes"
    assert categorize_glucose(145.0) == "Diabetes"


def test_engineer_features_calculations():
    """Verify derived columns (MAP, pulse pressure, ratios, and multimorbidity)."""
    df = pd.DataFrame([{
        "patient_id": "PT-99999",
        "age": 60,
        "gender": "Male",
        "region": "North Region",
        "bmi": 28.0,
        "systolic_bp": 140,
        "diastolic_bp": 80,
        "cholesterol_total": 240.0,
        "cholesterol_hdl": 60.0,
        "cholesterol_ldl": 150.0,
        "fasting_glucose": 130.0,
        "hba1c": 6.8,
        "smoking_status": "Former",
        "alcohol_consumption": "None",
        "physical_activity_mins": 180,
        "fatigue_reported": 1,
        "chest_pain_type": "Typical Angina",
        "dizziness_reported": 0,
        "shortness_of_breath": 0,
        "heart_disease": 1,
        "diabetes": 1,
        "stroke": 0
    }])

    res = engineer_features(df)

    # Pulse Pressure = SBP - DBP = 140 - 80 = 60
    assert res.loc[0, "pulse_pressure"] == 60
    # MAP = DBP + PP/3 = 80 + 20 = 100.0
    assert res.loc[0, "mean_arterial_pressure"] == 100.0
    # Cholesterol Ratio = 240 / 60 = 4.0
    assert res.loc[0, "cholesterol_ratio"] == 4.0
    # Multimorbidity = HD(1) + Diab(1) + Stroke(0) = 2
    assert res.loc[0, "multimorbidity_count"] == 2
    assert res.loc[0, "bmi_category"] == "Overweight"
    assert res.loc[0, "bp_category"] == "Hypertension Stage 2"
    assert res.loc[0, "glucose_category"] == "Diabetes"
    assert res.loc[0, "exercise_level"] == "Active (>=150m)"
    assert res.loc[0, "age_group"] == "51-65"
