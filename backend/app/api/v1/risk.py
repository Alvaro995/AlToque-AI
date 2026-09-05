"""Endpoints del pipeline predictivo de riesgo metabólico y explicabilidad SHAP."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.risk import RiskAssessment
from app.schemas.risk import RiskAssessmentResponse, RiskHistoryResponse, ShapFeature
from app.services.risk_service import RiskService

router = APIRouter(prefix="/risk", tags=["Riesgo Metabólico"])
risk_service = RiskService()


def _format_shap_features(shap_dict: Optional[dict], features_dict: Optional[dict]) -> List[ShapFeature]:
    """Convierte valores SHAP en factores interpretables para el usuario."""
    if not shap_dict or not features_dict:
        return []

    from app.ml.explainability import ModelExplainer

    formatted = []
    for k, val in shap_dict.items():
        if abs(val) < 0.04:
            continue
        direction = "increases_risk" if val > 0 else "decreases_risk"
        label = ModelExplainer.FEATURE_DESCRIPTIONS.get(k, k)
        f_val = float(features_dict.get(k, 0.0))

        if direction == "increases_risk":
            readable = f"{label} incrementa el riesgo estimado (+{round(val * 10, 1)} pts)."
        else:
            readable = f"{label} actúa como factor protector (-{abs(round(val * 10, 1))} pts)."

        formatted.append(
            ShapFeature(
                feature_name=k,
                feature_value=f_val,
                shap_value=val,
                contribution_direction=direction,
                human_readable=readable,
            )
        )
    formatted.sort(key=lambda x: abs(x.shap_value), reverse=True)
    return formatted[:5]


@router.post("/assess", response_model=RiskAssessmentResponse)
async def run_risk_assessment(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ejecuta inferencia predictiva XGBoost con atribución local SHAP."""
    assessment = await risk_service.assess_patient_risk(db=db, user_id=current_user.id)
    top_factors = _format_shap_features(assessment.shap_values, assessment.features_used)

    return RiskAssessmentResponse(
        id=assessment.id,
        user_id=assessment.user_id,
        assessed_at=assessment.assessed_at,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        model_version=assessment.model_version,
        features_used=assessment.features_used,
        shap_values=assessment.shap_values,
        top_factors=top_factors,
    )


@router.get("/latest", response_model=RiskAssessmentResponse)
async def get_latest_risk_assessment(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene la evaluación de riesgo más reciente del paciente."""
    res = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.user_id == current_user.id)
        .order_by(RiskAssessment.assessed_at.desc())
    )
    assessment = res.scalars().first()
    if not assessment:
        assessment = await risk_service.assess_patient_risk(db=db, user_id=current_user.id)

    top_factors = _format_shap_features(assessment.shap_values, assessment.features_used)
    return RiskAssessmentResponse(
        id=assessment.id,
        user_id=assessment.user_id,
        assessed_at=assessment.assessed_at,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        model_version=assessment.model_version,
        features_used=assessment.features_used,
        shap_values=assessment.shap_values,
        top_factors=top_factors,
    )


@router.get("/history", response_model=RiskHistoryResponse)
async def get_risk_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene la trayectoria longitudinal de evaluaciones de riesgo y su tendencia."""
    res = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.user_id == current_user.id)
        .order_by(RiskAssessment.assessed_at.asc())
    )
    assessments = list(res.scalars().all())

    if len(assessments) >= 2:
        diff = assessments[-1].risk_score - assessments[0].risk_score
        trend = "improving" if diff < -3.0 else ("worsening" if diff > 3.0 else "stable")
    else:
        trend = "stable"

    formatted_list = []
    for a in assessments:
        top_f = _format_shap_features(a.shap_values, a.features_used)
        formatted_list.append(
            RiskAssessmentResponse(
                id=a.id,
                user_id=a.user_id,
                assessed_at=a.assessed_at,
                risk_score=a.risk_score,
                risk_level=a.risk_level,
                model_version=a.model_version,
                features_used=a.features_used,
                shap_values=a.shap_values,
                top_factors=top_f,
            )
        )

    return RiskHistoryResponse(assessments=formatted_list, trend=trend)
