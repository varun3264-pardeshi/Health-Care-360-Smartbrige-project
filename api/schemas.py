"""
PulsePoint Cyber-Medical Intelligence System
Pydantic Request & Response Schemas (Pydantic v2 Compatible)
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

# 1. Authentication
class LoginRequest(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "dr_chen"})
    password: str = Field(..., json_schema_extra={"example": "Clinician@2026!"})

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    username: str
    role: str
    full_name: str
    permissions: Dict[str, bool]

# 2. Prediction Feature Vector
class PatientFeatureVector(BaseModel):
    age: int = Field(..., ge=18, le=120)
    gender: str = Field("Male")
    bmi: float = Field(..., ge=10.0, le=75.0)
    systolic_bp: int = Field(..., ge=60, le=260)
    diastolic_bp: int = Field(..., ge=40, le=160)
    cholesterol_total: float = Field(..., ge=50.0, le=600.0)
    cholesterol_hdl: float = Field(..., ge=10.0, le=150.0)
    cholesterol_ldl: float = Field(..., ge=20.0, le=400.0)
    fasting_glucose: float = Field(..., ge=40.0, le=600.0)
    hba1c: float = Field(..., ge=3.5, le=18.0)
    smoking_status: str = Field("Never")
    alcohol_consumption: str = Field("None")
    physical_activity_mins: int = Field(120, ge=0, le=1440)
    fatigue_reported: int = Field(0, ge=0, le=1)
    chest_pain_type: str = Field("None")
    dizziness_reported: int = Field(0, ge=0, le=1)
    shortness_of_breath: int = Field(0, ge=0, le=1)

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        valid = ["Male", "Female", "Other/Non-Binary"]
        if v not in valid:
            return "Other/Non-Binary"
        return v

class DiseasePredictionResponse(BaseModel):
    disease: str
    risk_probability: float
    risk_percentage: float
    risk_tier: str
    status_color: str
    clinical_recommendation: str
    contributing_factors: List[str]
    disclaimer: str

class MultiDiseasePredictionResponse(BaseModel):
    patient_summary: Dict[str, Any]
    predictions: Dict[str, DiseasePredictionResponse]
    overall_risk_evaluation: str

# 3. Analytics & Quality
class AnalyticsSummaryResponse(BaseModel):
    total_patients: int
    heart_disease_prevalence_pct: float
    diabetes_prevalence_pct: float
    stroke_prevalence_pct: float
    multimorbidity_prevalence_pct: float
    data_quality_score: float
    demographics_breakdown: Dict[str, Any]
    prevalence_by_age: Dict[str, Any]

class DataQualityResponse(BaseModel):
    execution_timestamp: str
    quality_score: float
    total_records: int
    duplicate_count: int
    missing_imputed_count: int
    completeness_pct: float
    issues_detected: List[str]

# 4. Clinical Alerts & Reviews
class AlertUpdatePayload(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "RESOLVED"})
    resolution_notes: Optional[str] = Field(None, json_schema_extra={"example": "Patient reviewed in clinic. Initiated ACE inhibitor."})

class CreateAlertPayload(BaseModel):
    patient_id: str = Field(..., json_schema_extra={"example": "PT-10042"})
    alert_type: str = Field("HEMODYNAMIC", json_schema_extra={"example": "HEMODYNAMIC"})
    severity: str = Field("CRITICAL", json_schema_extra={"example": "CRITICAL"})
    title: str = Field(..., json_schema_extra={"example": "Acute Hypertensive Excursion"})
    description: str = Field(..., json_schema_extra={"example": "Systolic BP 190 mmHg recorded during routine triage."})
    rule_code: str = Field("CRIT-HTN-01", json_schema_extra={"example": "CRIT-HTN-01"})

class PatientReviewUpdatePayload(BaseModel):
    review_status: str = Field(..., json_schema_extra={"example": "Reviewed"})
    clinical_notes: Optional[str] = Field(None, json_schema_extra={"example": "Medication adjusted. Follow-up in 4 weeks."})

# 5. Batch Inference
class BatchPredictionRequest(BaseModel):
    patients: List[PatientFeatureVector]

class BatchPredictionResponse(BaseModel):
    total_processed: int
    execution_time_ms: float
    results: List[MultiDiseasePredictionResponse]
