"""
PulsePoint Cyber-Medical Intelligence System
Inference & Multi-Disease Risk Prediction Service
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np

from core.config import MODELS_DIR
from ml_engine.preprocessor import ALL_MODEL_FEATURES

DISCLAIMER_TEXT = (
    "CLINICAL DECISION SUPPORT PROTOTYPE ONLY. NOT A CLINICAL DIAGNOSTIC DEVICE. "
    "Predictions represent retrospective statistical risk associations and must not "
    "replace professional clinical judgment, laboratory diagnostics, or specialist review."
)


class DiseaseRiskPredictor:
    """Loads trained pipelines and performs validated multi-condition risk inference."""

    _models = {}

    @classmethod
    def get_model(cls, disease_key: str):
        """Lazy loads and caches model pipeline."""
        if disease_key not in cls._models:
            model_path = MODELS_DIR / f"{disease_key}_rf.joblib"
            if not model_path.exists():
                raise FileNotFoundError(f"Model for '{disease_key}' not found at {model_path}. Train models first.")
            cls._models[disease_key] = joblib.load(model_path)
        return cls._models[disease_key]

    @classmethod
    def predict_risk(cls, disease_key: str, patient_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates predicted risk probability, risk category, and major contributing biomarkers.
        """
        model = cls.get_model(disease_key)

        # Convert dictionary to single-row DataFrame with expected schema
        input_data = {}
        for col in ALL_MODEL_FEATURES:
            input_data[col] = [patient_features.get(col, np.nan)]
        df_input = pd.DataFrame(input_data)

        # Predict probability
        prob = float(model.predict_proba(df_input)[0, 1])

        # Assign Risk Stratification Tier
        if prob < 0.20:
            risk_tier = "LOW RISK"
            status_color = "#00f5a0" # Green
            clinical_action = "Routine annual preventive screening recommended."
        elif prob < 0.50:
            risk_tier = "MODERATE RISK"
            status_color = "#ffaa00" # Amber
            clinical_action = "Lifestyle intervention, nutrition counseling, and 6-month clinical review."
        elif prob < 0.75:
            risk_tier = "HIGH RISK"
            status_color = "#ff6b6b" # Coral Red
            clinical_action = "Priority specialist referral, diagnostic workup, and pharmacotherapy evaluation."
        else:
            risk_tier = "CRITICAL RISK"
            status_color = "#ff0055" # Neon Red
            clinical_action = "Urgent clinical assessment, intensive hemodynamic and metabolic stabilization."

        # Identify personal key risk factors based on physiological criteria
        contributing_factors = []
        if patient_features.get("systolic_bp", 0) >= 140:
            contributing_factors.append(f"Elevated Systolic Blood Pressure ({patient_features['systolic_bp']} mmHg)")
        if patient_features.get("fasting_glucose", 0) >= 126:
            contributing_factors.append(f"Hyperglycemia ({patient_features['fasting_glucose']} mg/dL)")
        if patient_features.get("hba1c", 0) >= 6.5:
            contributing_factors.append(f"Elevated Glycated Hemoglobin ({patient_features['hba1c']}%)")
        if patient_features.get("bmi", 0) >= 30.0:
            contributing_factors.append(f"Classified Obesity (BMI {patient_features['bmi']} kg/m^2)")
        if patient_features.get("cholesterol_ldl", 0) >= 160:
            contributing_factors.append(f"High LDL Cholesterol ({patient_features['cholesterol_ldl']} mg/dL)")
        if patient_features.get("smoking_status") == "Current":
            contributing_factors.append("Active Tobacco Use")
        if patient_features.get("chest_pain_type") in ["Typical Angina", "Atypical Angina"]:
            contributing_factors.append(f"Reported {patient_features['chest_pain_type']}")
        if patient_features.get("physical_activity_mins", 100) < 60:
            contributing_factors.append("Sedentary Physical Activity Profile")

        if not contributing_factors:
            contributing_factors.append("Biomarkers largely within normal reference physiological limits")

        return {
            "disease": disease_key,
            "risk_probability": round(prob, 4),
            "risk_percentage": round(prob * 100.0, 1),
            "risk_tier": risk_tier,
            "status_color": status_color,
            "clinical_recommendation": clinical_action,
            "contributing_factors": contributing_factors,
            "disclaimer": DISCLAIMER_TEXT
        }

    @classmethod
    def predict_all_conditions(cls, patient_features: Dict[str, Any]) -> Dict[str, Any]:
        """Runs predictions across all three diseases simultaneously."""
        results = {}
        for d in ["heart_disease", "diabetes", "stroke"]:
            results[d] = cls.predict_risk(d, patient_features)
        return results
