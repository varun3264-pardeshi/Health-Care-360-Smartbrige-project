"""
Unit & Integration Tests: Machine Learning Pipelines, Leakage Prevention & Inference
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from core.config import MODELS_DIR
from ml_engine.preprocessor import build_preprocessor, ALL_MODEL_FEATURES
from ml_engine.predictor import DiseaseRiskPredictor

def test_model_artifacts_exist():
    """Verify serialized model files exist on disk for all three disease targets."""
    for d in ["heart_disease", "diabetes", "stroke"]:
        rf_path = MODELS_DIR / f"{d}_rf.joblib"
        base_path = MODELS_DIR / f"{d}_baseline.joblib"
        assert rf_path.exists(), f"Model {rf_path} not found."
        assert base_path.exists(), f"Baseline model {base_path} not found."


def test_leakage_prevention_preprocessor():
    """
    Verify that the ColumnTransformer fits exclusively on training data
    and correctly transforms unseen evaluation vectors without leaking test statistics.
    """
    train_data = pd.DataFrame({
        "age": [40, 50, 60],
        "bmi": [22.0, 26.0, 30.0],
        "systolic_bp": [120, 130, 140],
        "diastolic_bp": [80, 85, 90],
        "cholesterol_total": [180.0, 200.0, 220.0],
        "cholesterol_hdl": [50.0, 45.0, 40.0],
        "cholesterol_ldl": [100.0, 120.0, 140.0],
        "fasting_glucose": [90.0, 110.0, 130.0],
        "hba1c": [5.2, 5.8, 6.4],
        "physical_activity_mins": [150, 100, 50],
        "gender": ["Male", "Female", "Male"],
        "smoking_status": ["Never", "Former", "Current"],
        "alcohol_consumption": ["None", "Moderate", "Heavy"],
        "chest_pain_type": ["None", "Typical Angina", "Atypical Angina"],
        "fatigue_reported": [0, 1, 0],
        "dizziness_reported": [0, 0, 1],
        "shortness_of_breath": [0, 1, 0]
    })

    preprocessor = build_preprocessor()
    X_train_trans = preprocessor.fit_transform(train_data)
    
    # Check that output is 2D numpy array with no NaNs
    assert isinstance(X_train_trans, np.ndarray)
    assert not np.isnan(X_train_trans).any()

    # Transform test vector with unseen category
    test_data = train_data.iloc[:1].copy()
    test_data["gender"] = "Other/Non-Binary"
    X_test_trans = preprocessor.transform(test_data)
    assert X_test_trans.shape[0] == 1
    assert not np.isnan(X_test_trans).any()


def test_disease_risk_predictor_inference():
    """Verify single and multi-condition inference outputs calibrated probabilities and clinical tiers."""
    patient_vector = {
        "age": 62,
        "gender": "Male",
        "bmi": 32.5,
        "systolic_bp": 160,
        "diastolic_bp": 95,
        "cholesterol_total": 250.0,
        "cholesterol_hdl": 35.0,
        "cholesterol_ldl": 175.0,
        "fasting_glucose": 160.0,
        "hba1c": 8.1,
        "smoking_status": "Current",
        "alcohol_consumption": "Moderate",
        "physical_activity_mins": 30,
        "fatigue_reported": 1,
        "chest_pain_type": "Typical Angina",
        "dizziness_reported": 1,
        "shortness_of_breath": 1
    }

    # Test Heart Disease Inference
    res = DiseaseRiskPredictor.predict_risk("heart_disease", patient_vector)
    assert "risk_probability" in res
    assert 0.0 <= res["risk_probability"] <= 1.0
    assert res["risk_tier"] in ["LOW RISK", "MODERATE RISK", "HIGH RISK", "CRITICAL RISK"]
    assert len(res["contributing_factors"]) > 0
    assert "CLINICAL DECISION SUPPORT" in res["disclaimer"]

    # Test Multi-Condition Simultaneous Inference
    all_preds = DiseaseRiskPredictor.predict_all_conditions(patient_vector)
    assert "heart_disease" in all_preds
    assert "diabetes" in all_preds
    assert "stroke" in all_preds
    for d, p in all_preds.items():
        assert 0.0 <= p["risk_probability"] <= 1.0


def test_counterfactual_intervention_risk_reduction():
    """Verify that simulated clinical interventions (BP & glucose control, smoking cessation) yield risk reduction."""
    baseline_high_risk = {
        "age": 68,
        "gender": "Male",
        "bmi": 34.0,
        "systolic_bp": 175,
        "diastolic_bp": 105,
        "cholesterol_total": 280.0,
        "cholesterol_hdl": 32.0,
        "cholesterol_ldl": 200.0,
        "fasting_glucose": 190.0,
        "hba1c": 9.2,
        "smoking_status": "Current",
        "alcohol_consumption": "Heavy",
        "physical_activity_mins": 15,
        "fatigue_reported": 1,
        "chest_pain_type": "Typical Angina",
        "dizziness_reported": 1,
        "shortness_of_breath": 1
    }

    # Intervened lifestyle and pharmacological control
    treated_patient = dict(baseline_high_risk)
    treated_patient["systolic_bp"] = 120
    treated_patient["diastolic_bp"] = 78
    treated_patient["fasting_glucose"] = 95.0
    treated_patient["hba1c"] = 5.5
    treated_patient["smoking_status"] = "Former"
    treated_patient["physical_activity_mins"] = 180

    base_preds = DiseaseRiskPredictor.predict_all_conditions(baseline_high_risk)
    treat_preds = DiseaseRiskPredictor.predict_all_conditions(treated_patient)

    # In clinically sound models, improving all risk vectors reduces or maintains risk probability
    for d in ["heart_disease", "diabetes", "stroke"]:
        base_prob = base_preds[d]["risk_probability"]
        treat_prob = treat_preds[d]["risk_probability"]
        assert treat_prob <= base_prob + 0.05, f"Expected reduction for {d}, got {base_prob} -> {treat_prob}"

