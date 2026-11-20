"""
PulsePoint Cyber-Medical Intelligence System
Model Evaluation & Performance Reporting Utilities
"""

import json
from typing import Dict, Any, List
from core.database import query_db

def get_latest_model_metrics() -> Dict[str, Any]:
    """Retrieves the latest registered metrics and parameters for all active models."""
    rows = query_db(
        """
        SELECT disease_type, model_type, version, train_timestamp,
               train_samples, test_samples, metrics_json, parameters_json, file_path
        FROM model_metadata
        WHERE is_active = 1
        ORDER BY id DESC
        """
    )

    models_summary = {}
    for r in rows:
        d_type = r["disease_type"]
        if d_type not in models_summary: # Get latest for each disease
            metrics = json.loads(r["metrics_json"])
            params = json.loads(r["parameters_json"])
            models_summary[d_type] = {
                "disease_type": d_type,
                "model_type": r["model_type"],
                "version": r["version"],
                "train_timestamp": r["train_timestamp"],
                "train_samples": r["train_samples"],
                "test_samples": r["test_samples"],
                "metrics": metrics,
                "parameters": params,
                "file_path": r["file_path"]
            }

    return models_summary
