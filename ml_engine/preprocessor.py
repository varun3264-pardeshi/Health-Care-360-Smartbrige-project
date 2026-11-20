"""
PulsePoint Cyber-Medical Intelligence System
ML Preprocessing & Feature Transformation Pipeline
Prevents data leakage by strictly fitting scalers/encoders on training folds only.
"""

from typing import List, Tuple
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Clinically relevant features for predictive stratification
NUMERIC_FEATURES = [
    "age",
    "bmi",
    "systolic_bp",
    "diastolic_bp",
    "cholesterol_total",
    "cholesterol_hdl",
    "cholesterol_ldl",
    "fasting_glucose",
    "hba1c",
    "physical_activity_mins"
]

CATEGORICAL_FEATURES = [
    "gender",
    "smoking_status",
    "alcohol_consumption",
    "chest_pain_type"
]

BINARY_SYMPTOMS = [
    "fatigue_reported",
    "dizziness_reported",
    "shortness_of_breath"
]

ALL_MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES + BINARY_SYMPTOMS


def build_preprocessor() -> ColumnTransformer:
    """
    Constructs a scikit-learn ColumnTransformer that scales continuous biomarkers,
    one-hot encodes clinical categories, and passes through binary symptom flags.
    """
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    binary_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
            ("bin", binary_transformer, BINARY_SYMPTOMS)
        ],
        remainder="drop"
    )

    return preprocessor


def get_feature_names_after_transform(preprocessor: ColumnTransformer) -> List[str]:
    """Extracts human-readable feature names from the fitted ColumnTransformer."""
    feature_names = []
    
    # 1. Numeric features
    feature_names.extend(NUMERIC_FEATURES)
    
    # 2. Categorical features after one-hot encoding
    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    cat_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    feature_names.extend(cat_names)
    
    # 3. Binary symptoms
    feature_names.extend(BINARY_SYMPTOMS)
    
    return feature_names
