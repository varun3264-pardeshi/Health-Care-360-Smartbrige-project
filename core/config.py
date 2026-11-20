"""
PulsePoint Cyber-Medical Intelligence System
Core Configuration Module
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
TABLEAU_DIR = BASE_DIR / "tableau"

# Ensure essential directories exist
for folder in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR, TABLEAU_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Application Metadata
APP_NAME = os.getenv("APP_NAME", "PulsePoint Cyber-Medical Intelligence")
APP_VERSION = os.getenv("APP_VERSION", "2.4.0")
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Server Network Settings
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# Security Settings
SECRET_KEY = os.getenv("SECRET_KEY", "cyber-medical-secure-key-2026-antigravity-991204")
ALGORITHM = "HS256"
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

# Database
DB_PATH = DATA_DIR / "healthcare_intelligence.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Privacy & Clinical Thresholds
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
SMALL_CELL_SUPPRESSION_THRESHOLD = int(os.getenv("SMALL_CELL_SUPPRESSION_THRESHOLD", "5"))

# Clinical Reference Ranges (Established AHA, ADA, WHO guidelines)
CLINICAL_THRESHOLDS = {
    "blood_pressure": {
        "normal_systolic": 120,
        "normal_diastolic": 80,
        "elevated_systolic": 129,
        "hypertension_stage1_systolic": 139,
        "hypertension_stage2_systolic": 180, # Crisis if above
        "critical_systolic_alert": 160
    },
    "glucose": {
        "normal_fasting": 100,
        "prediabetes_fasting": 125,
        "diabetes_fasting": 126,
        "critical_fasting_alert": 200
    },
    "hba1c": {
        "normal": 5.7,
        "prediabetes": 6.4,
        "diabetes": 6.5
    },
    "bmi": {
        "underweight": 18.5,
        "normal_upper": 24.9,
        "overweight_upper": 29.9,
        "obese_class1_upper": 34.9,
        "obese_class2_upper": 39.9
    },
    "cholesterol": {
        "desirable_total": 200,
        "borderline_high": 239,
        "high_total": 240,
        "target_ldl": 100,
        "low_hdl_male": 40,
        "low_hdl_female": 50
    }
}
