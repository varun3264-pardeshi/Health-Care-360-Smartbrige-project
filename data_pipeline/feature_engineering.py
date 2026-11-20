"""
PulsePoint Cyber-Medical Intelligence System
Clinical Feature Engineering Pipeline
"""

import pandas as pd
import numpy as np

def categorize_bmi(bmi: float) -> str:
    """Categorize Body Mass Index per WHO standards."""
    if pd.isna(bmi):
        return "Unknown"
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal"
    elif bmi < 30.0:
        return "Overweight"
    elif bmi < 35.0:
        return "Obesity Class I"
    else:
        return "Obesity Class II+"


def categorize_blood_pressure(sbp: float, dbp: float) -> str:
    """Categorize Blood Pressure per 2017 AHA/ACC guidelines."""
    if pd.isna(sbp) or pd.isna(dbp):
        return "Unknown"
    if sbp >= 180 or dbp >= 120:
        return "Hypertensive Crisis"
    elif sbp >= 140 or dbp >= 90:
        return "Hypertension Stage 2"
    elif (130 <= sbp <= 139) or (80 <= dbp <= 89):
        return "Hypertension Stage 1"
    elif (120 <= sbp <= 129) and dbp < 80:
        return "Elevated"
    else:
        return "Normal"


def categorize_glucose(glucose: float) -> str:
    """Categorize Fasting Plasma Glucose per ADA criteria."""
    if pd.isna(glucose):
        return "Unknown"
    if glucose < 100.0:
        return "Normal"
    elif glucose <= 125.0:
        return "Prediabetes"
    else:
        return "Diabetes"


def categorize_exercise(mins: float) -> str:
    """Categorize Physical Activity per WHO recommended aerobic minutes."""
    if pd.isna(mins):
        return "Unknown"
    if mins < 60:
        return "Sedentary (<60m)"
    elif mins < 150:
        return "Lightly Active (60-149m)"
    else:
        return "Active (>=150m)"


def categorize_age(age: int) -> str:
    """Group age into standard epidemiological cohorts."""
    if pd.isna(age):
        return "Unknown"
    if age <= 35:
        return "18-35"
    elif age <= 50:
        return "36-50"
    elif age <= 65:
        return "51-65"
    else:
        return "65+"


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes derived clinical ratios, hemodynamic metrics, and categorical bins.
    Does not mutate input DataFrame in place.
    """
    df = df.copy()

    # Derived Hemodynamics
    df["pulse_pressure"] = df["systolic_bp"] - df["diastolic_bp"]
    df["mean_arterial_pressure"] = np.round(df["diastolic_bp"] + (df["pulse_pressure"] / 3.0), 1)

    # Derived Lipid Ratios
    hdl_safe = df["cholesterol_hdl"].replace(0, np.nan)
    df["cholesterol_ratio"] = np.round(df["cholesterol_total"] / hdl_safe, 2)

    # Categorical Bins
    df["bmi_category"] = df["bmi"].apply(categorize_bmi)
    df["bp_category"] = df.apply(lambda r: categorize_blood_pressure(r["systolic_bp"], r["diastolic_bp"]), axis=1)
    df["glucose_category"] = df["fasting_glucose"].apply(categorize_glucose)
    df["exercise_level"] = df["physical_activity_mins"].apply(categorize_exercise)
    df["age_group"] = df["age"].apply(categorize_age)

    # Multimorbidity & Risk Overlap
    df["multimorbidity_count"] = df["heart_disease"] + df["diabetes"] + df["stroke"]

    # Overall completeness metric per record (1.0 = all fields filled)
    df["data_completeness_pct"] = np.round((1.0 - df.isnull().mean(axis=1)) * 100.0, 1)

    return df
