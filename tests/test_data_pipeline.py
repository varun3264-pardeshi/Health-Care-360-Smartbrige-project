"""
Unit & Integration Tests: Data Ingestion, Validation & Quality Pipeline
"""

import pytest
import pandas as pd
import numpy as np
from data_pipeline.synthetic_generator import generate_synthetic_cohort
from data_pipeline.validator import DataValidator, PHYSIOLOGICAL_RANGES, REQUIRED_COLUMNS

def test_synthetic_cohort_generation():
    """Verify synthetic cohort generation produces correct shape, schema, and outcome ranges."""
    df = generate_synthetic_cohort(num_records=200, seed=123, introduce_imperfections=False)
    
    assert len(df) == 200
    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Missing required column: {col}"

    assert df["heart_disease"].isin([0, 1]).all()
    assert df["diabetes"].isin([0, 1]).all()
    assert df["stroke"].isin([0, 1]).all()
    assert (df["age"] >= 18).all() and (df["age"] <= 89).all()


def test_validator_duplicate_detection():
    """Verify that duplicates are detected, logged, and dropped."""
    df = generate_synthetic_cohort(num_records=100, seed=42, introduce_imperfections=False)
    # Force duplicate rows
    dups = df.iloc[:5].copy()
    df_with_dups = pd.concat([df, dups], ignore_index=True)
    assert len(df_with_dups) == 105

    validator = DataValidator(df_with_dups)
    clean_df, metrics = validator.validate_and_clean()

    assert len(clean_df) == 100
    assert metrics["duplicate_count"] == 5
    assert any("duplicate" in issue.lower() for issue in metrics["issues"])


def test_validator_missing_imputation():
    """Verify that missing values in required features are imputed cleanly."""
    df = generate_synthetic_cohort(num_records=100, seed=42, introduce_imperfections=False)
    df.loc[0:4, "cholesterol_ldl"] = np.nan
    df.loc[10:14, "smoking_status"] = np.nan

    validator = DataValidator(df)
    clean_df, metrics = validator.validate_and_clean()

    assert clean_df["cholesterol_ldl"].isnull().sum() == 0
    assert clean_df["smoking_status"].isnull().sum() == 0
    assert metrics["missing_cells_imputed"] >= 10


def test_validator_range_bounding():
    """Verify that impossible physiological outliers are clamped to medical bounds."""
    df = generate_synthetic_cohort(num_records=50, seed=42, introduce_imperfections=False)
    # Inject impossible values
    df.loc[0, "systolic_bp"] = 350 # Impossible high
    df.loc[1, "fasting_glucose"] = 800 # Extreme high
    df.loc[2, "bmi"] = 5.0 # Impossible low

    validator = DataValidator(df)
    clean_df, metrics = validator.validate_and_clean()

    max_sbp = PHYSIOLOGICAL_RANGES["systolic_bp"][1]
    max_gluc = PHYSIOLOGICAL_RANGES["fasting_glucose"][1]
    min_bmi = PHYSIOLOGICAL_RANGES["bmi"][0]

    assert clean_df.loc[0, "systolic_bp"] <= max_sbp
    assert clean_df.loc[1, "fasting_glucose"] <= max_gluc
    assert clean_df.loc[2, "bmi"] >= min_bmi
    assert metrics["range_violations_corrected"] >= 3


def test_validator_bp_inversion_correction():
    """Verify that inverted BP (diastolic >= systolic) is corrected."""
    df = generate_synthetic_cohort(num_records=50, seed=42, introduce_imperfections=False)
    df.loc[0, "systolic_bp"] = 80
    df.loc[0, "diastolic_bp"] = 100 # Inversion

    validator = DataValidator(df)
    clean_df, _ = validator.validate_and_clean()

    assert clean_df.loc[0, "systolic_bp"] > clean_df.loc[0, "diastolic_bp"]


def test_quality_score_calculation():
    """Verify data quality score is calculated within 0 - 100."""
    df = generate_synthetic_cohort(num_records=100, seed=42, introduce_imperfections=True)
    validator = DataValidator(df)
    _, metrics = validator.validate_and_clean()

    score = metrics["quality_score"]
    assert 0.0 <= score <= 100.0
    assert metrics["completeness_pct"] >= 90.0
