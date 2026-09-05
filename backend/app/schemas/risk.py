"""Modelos para evaluaciones predictivas de riesgo metabólico y factores SHAP."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"


class ShapFeature(BaseModel):
    feature_name: str
    feature_value: float
    shap_value: float
    contribution_direction: str  # "increases_risk" or "decreases_risk"
    human_readable: str  # Translated explanation for the user


class RiskAssessmentResponse(BaseModel):
    id: str
    user_id: str
    assessed_at: datetime
    risk_score: float
    risk_level: str
    model_version: str
    features_used: Optional[dict] = None
    shap_values: Optional[dict] = None
    top_factors: Optional[list[ShapFeature]] = None

    model_config = {"from_attributes": True}


class RiskHistoryResponse(BaseModel):
    assessments: list[RiskAssessmentResponse]
    trend: str  # "improving", "stable", "worsening"
