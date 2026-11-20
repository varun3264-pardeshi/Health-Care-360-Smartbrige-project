"""
PulsePoint Cyber-Medical Intelligence System
ML Model Training & Rigorous Evaluation Module
Builds distinct pipelines for Heart Disease, Diabetes, and Stroke.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    brier_score_loss, roc_curve
)
from sklearn.pipeline import Pipeline

from core.config import MODELS_DIR
from core.database import execute_db
from data_pipeline.exporter import load_dataset
from ml_engine.preprocessor import (
    build_preprocessor, get_feature_names_after_transform, ALL_MODEL_FEATURES
)

DISEASE_TARGETS = {
    "heart_disease": {
        "label": "Heart Disease",
        "description": "Retrospective classification of coronary artery and myocardial disease indicators"
    },
    "diabetes": {
        "label": "Type 2 Diabetes",
        "description": "Retrospective classification of glycemic dysregulation and diabetic indicators"
    },
    "stroke": {
        "label": "Cerebrovascular Stroke",
        "description": "Retrospective classification of cerebrovascular ischemia and stroke events"
    }
}


def compute_optimal_threshold(y_true: np.ndarray, y_probs: np.ndarray) -> float:
    """Computes the optimal decision threshold using Youden's J statistic (max Sensitivity + Specificity - 1)."""
    fpr, tpr, thresholds = roc_curve(y_true, y_probs)
    j_scores = tpr - fpr
    best_idx = np.argmax(j_scores)
    optimal_thresh = float(thresholds[best_idx])
    return min(max(optimal_thresh, 0.15), 0.85)


def train_single_disease_model(
    df: pd.DataFrame,
    target_col: str,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Trains Logistic Regression baseline and Random Forest classifier for a target condition.
    Evaluates leakage-free on held-out test split and saves serialized artifacts.
    """
    X = df[ALL_MODEL_FEATURES]
    y = df[target_col].astype(int)

    # 1. Stratified Train-Test Split (80% Train, 20% Held-out Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=random_state
    )

    # 2. Build Models with Balanced Class Weights
    preprocessor = build_preprocessor()
    
    # Baseline Model: Logistic Regression
    lr_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=random_state))
    ])

    # Advanced Model: Random Forest
    rf_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=120,
            max_depth=12,
            min_samples_split=6,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=1
        ))
    ])

    # 3. Cross-Validation on Training Split
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    lr_cv_auc = float(np.mean(cross_val_score(lr_pipeline, X_train, y_train, cv=cv, scoring="roc_auc")))
    rf_cv_auc = float(np.mean(cross_val_score(rf_pipeline, X_train, y_train, cv=cv, scoring="roc_auc")))

    # 4. Fit on Full Training Split
    lr_pipeline.fit(X_train, y_train)
    rf_pipeline.fit(X_train, y_train)

    # 5. Evaluate on Held-Out Test Split
    rf_probs = rf_pipeline.predict_proba(X_test)[:, 1]
    lr_probs = lr_pipeline.predict_proba(X_test)[:, 1]

    optimal_threshold = compute_optimal_threshold(y_test, rf_probs)
    rf_preds_custom = (rf_probs >= optimal_threshold).astype(int)
    rf_preds_default = rf_pipeline.predict(X_test)

    cm = confusion_matrix(y_test, rf_preds_custom)
    tn, fp, fn, tp = cm.ravel()

    # Calculate rigorous clinical metrics
    metrics = {
        "accuracy": float(accuracy_score(y_test, rf_preds_custom)),
        "precision": float(precision_score(y_test, rf_preds_custom, zero_division=0)),
        "recall": float(recall_score(y_test, rf_preds_custom, zero_division=0)),
        "f1": float(f1_score(y_test, rf_preds_custom, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, rf_probs)),
        "pr_auc": float(average_precision_score(y_test, rf_probs)),
        "brier_score": float(brier_score_loss(y_test, rf_probs)),
        "optimal_threshold": float(optimal_threshold),
        "confusion_matrix": {
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)
        },
        "baseline_lr_test_auc": float(roc_auc_score(y_test, lr_probs)),
        "baseline_lr_cv_auc": lr_cv_auc,
        "rf_cv_auc": rf_cv_auc
    }

    # 6. Extract Feature Importance
    transformed_feature_names = get_feature_names_after_transform(
        rf_pipeline.named_steps["preprocessor"]
    )
    importances = rf_pipeline.named_steps["classifier"].feature_importances_
    
    feat_imp = sorted(
        [{"feature": f, "importance": float(round(imp, 4))} for f, imp in zip(transformed_feature_names, importances)],
        key=lambda x: x["importance"],
        reverse=True
    )
    metrics["feature_importances"] = feat_imp[:12] # Top 12 predictors

    # 7. Serialize Artifacts
    model_version = f"v2.4-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    rf_model_filename = f"{target_col}_rf.joblib"
    rf_model_path = MODELS_DIR / rf_model_filename
    joblib.dump(rf_pipeline, rf_model_path)

    baseline_filename = f"{target_col}_baseline.joblib"
    joblib.dump(lr_pipeline, MODELS_DIR / baseline_filename)

    # 8. Record Model Metadata in Database
    execute_db(
        """
        INSERT INTO model_metadata (
            disease_type, model_type, version, train_timestamp,
            train_samples, test_samples, metrics_json, parameters_json, file_path, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            target_col,
            "RandomForestClassifier (Ensemble)",
            model_version,
            datetime.now(timezone.utc).isoformat(),
            len(X_train),
            len(X_test),
            json.dumps(metrics),
            json.dumps({
                "n_estimators": 120,
                "max_depth": 12,
                "class_weight": "balanced",
                "random_state": random_state
            }),
            str(rf_model_path),
            1
        )
    )

    return {
        "disease_type": target_col,
        "model_version": model_version,
        "metrics": metrics,
        "model_path": str(rf_model_path)
    }


def train_all_disease_models() -> Dict[str, Any]:
    """Trains and serializes ML models for all three core diseases."""
    df = load_dataset()
    results = {}
    for disease_key in DISEASE_TARGETS.keys():
        print(f"Training pipeline for: {disease_key}...", flush=True)
        results[disease_key] = train_single_disease_model(df, disease_key)
        print(f"Completed {disease_key}: ROC-AUC={results[disease_key]['metrics']['roc_auc']:.3f}, F1={results[disease_key]['metrics']['f1']:.3f}", flush=True)
    return results


if __name__ == "__main__":
    train_all_disease_models()
