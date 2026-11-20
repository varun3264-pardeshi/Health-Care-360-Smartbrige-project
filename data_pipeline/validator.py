"""
PulsePoint Cyber-Medical Intelligence System
Automated Data Quality & Validation Engine
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from core.database import execute_db

REQUIRED_COLUMNS = [
    "patient_id", "age", "gender", "region", "bmi",
    "systolic_bp", "diastolic_bp", "cholesterol_total", "cholesterol_hdl", "cholesterol_ldl",
    "fasting_glucose", "hba1c", "smoking_status", "alcohol_consumption",
    "physical_activity_mins", "fatigue_reported", "chest_pain_type",
    "dizziness_reported", "shortness_of_breath", "heart_disease", "diabetes", "stroke"
]

PHYSIOLOGICAL_RANGES = {
    "age": (18, 120),
    "bmi": (12.0, 70.0),
    "systolic_bp": (60, 260),
    "diastolic_bp": (40, 160),
    "cholesterol_total": (60.0, 500.0),
    "cholesterol_hdl": (10.0, 140.0),
    "cholesterol_ldl": (20.0, 350.0),
    "fasting_glucose": (40.0, 500.0),
    "hba1c": (3.5, 18.0),
    "physical_activity_mins": (0, 1440)
}

class DataValidator:
    """Validates clinical schema, values, missingness, and physiological consistency."""

    def __init__(self, df: pd.DataFrame):
        self.raw_df = df.copy()
        self.clean_df = df.copy()
        self.issues = []
        self.quality_metrics = {}

    def validate_and_clean(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Executes full validation pipeline and returns cleaned DataFrame with quality audit."""
        total_initial = len(self.raw_df)

        # 1. Schema Check
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in self.raw_df.columns]
        if missing_cols:
            self.issues.append(f"Missing required schema columns: {missing_cols}")

        # 2. Duplicate Detection
        dup_count = int(self.clean_df.duplicated(subset=["patient_id"]).sum())
        if dup_count > 0:
            self.issues.append(f"Detected {dup_count} duplicate patient IDs. Retaining latest distinct record.")
            self.clean_df = self.clean_df.drop_duplicates(subset=["patient_id"], keep="last")

        # 3. Missing Value Analysis
        missing_summary = self.clean_df[REQUIRED_COLUMNS].isnull().sum().to_dict()
        total_missing_cells = int(sum(missing_summary.values()))
        
        # Impute numerical features using median, categorical with mode
        for col in REQUIRED_COLUMNS:
            if self.clean_df[col].isnull().sum() > 0:
                if pd.api.types.is_numeric_dtype(self.clean_df[col]):
                    median_val = self.clean_df[col].median()
                    self.clean_df[col] = self.clean_df[col].fillna(median_val)
                else:
                    mode_val = self.clean_df[col].mode()[0]
                    self.clean_df[col] = self.clean_df[col].fillna(mode_val)

        # 4. Range Validation & Outlier Clamping
        range_violations = 0
        for col, (min_v, max_v) in PHYSIOLOGICAL_RANGES.items():
            if col in self.clean_df.columns:
                out_of_bounds = (self.clean_df[col] < min_v) | (self.clean_df[col] > max_v)
                count_oob = int(out_of_bounds.sum())
                if count_oob > 0:
                    range_violations += count_oob
                    self.clean_df[col] = self.clean_df[col].clip(lower=min_v, upper=max_v)

        if range_violations > 0:
            self.issues.append(f"Rectified {range_violations} out-of-range clinical measurements via physiological bounding.")

        # 5. Logical Consistency: SBP must exceed DBP
        bp_inversion = self.clean_df["systolic_bp"] <= self.clean_df["diastolic_bp"]
        inversion_count = int(bp_inversion.sum())
        if inversion_count > 0:
            self.clean_df.loc[bp_inversion, "systolic_bp"] = self.clean_df.loc[bp_inversion, "diastolic_bp"] + 25
            self.issues.append(f"Corrected {inversion_count} inverted blood pressure records.")

        # 6. Quality Score Computation (0 - 100)
        completeness_pct = np.round(
            (1.0 - (total_missing_cells / max(total_initial * len(REQUIRED_COLUMNS), 1))) * 100.0, 2
        )
        duplicate_penalty = min(dup_count * 0.5, 15.0)
        missing_penalty = min((total_missing_cells / max(total_initial, 1)) * 10.0, 20.0)
        range_penalty = min(range_violations * 0.2, 10.0)
        
        quality_score = max(np.round(100.0 - duplicate_penalty - missing_penalty - range_penalty, 1), 0.0)

        self.quality_metrics = {
            "execution_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_initial_records": total_initial,
            "total_cleaned_records": len(self.clean_df),
            "duplicate_count": dup_count,
            "missing_cells_imputed": total_missing_cells,
            "range_violations_corrected": range_violations,
            "completeness_pct": completeness_pct,
            "quality_score": quality_score,
            "issues": self.issues
        }

        # Persist data quality metrics to DB
        execute_db(
            """
            INSERT INTO data_quality_metrics (execution_timestamp, total_records, duplicate_count, missing_count, completeness_pct, quality_score, issues_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.quality_metrics["execution_timestamp"],
                total_initial,
                dup_count,
                total_missing_cells,
                completeness_pct,
                quality_score,
                json.dumps(self.issues)
            )
        )

        return self.clean_df, self.quality_metrics
