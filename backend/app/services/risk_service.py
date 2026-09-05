"""Servicio de evaluación de riesgo metabólico y traducción de factores SHAP."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.risk import RiskAssessment
from app.models.user import User, PatientProfile
from app.models.ingestion import ClinicalRecord, ClinicalParameter
from app.models.glycemic import FoodLog, BufferEvaluation
from app.models.physical import ExerciseTrigger
from app.services.ml_service import MLService


class RiskService:
    """Calculates, records, and tracks longitudinal patient risk progression."""

    def __init__(self):
        self.ml_service = MLService()

    async def assess_patient_risk(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> RiskAssessment:
        """Aggregate patient context from DB, run ML inference, and store RiskAssessment."""
        # 1. Fetch profile
        prof_res = await db.execute(select(PatientProfile).where(PatientProfile.user_id == user_id))
        profile = prof_res.scalar_one_or_none()
        profile_data = {}
        if profile:
            profile_data = {
                "birth_date": profile.birth_date,
                "sex": profile.sex,
                "height_cm": profile.height_cm,
                "weight_kg": profile.weight_kg,
                "activity_level": profile.activity_level,
            }

        # 2. Fetch latest clinical parameters
        record_res = await db.execute(
            select(ClinicalRecord)
            .where(ClinicalRecord.user_id == user_id)
            .order_by(ClinicalRecord.created_at.desc())
        )
        latest_record = record_res.scalars().first()

        clinical_params: Dict[str, float] = {}
        if latest_record:
            params_res = await db.execute(
                select(ClinicalParameter).where(ClinicalParameter.record_id == latest_record.id)
            )
            for cp in params_res.scalars().all():
                clinical_params[cp.parameter_name] = cp.value

        # 3. Fetch past 7 days habit metrics
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        # Glycemic
        food_res = await db.execute(
            select(FoodLog).where(
                and_(FoodLog.user_id == user_id, FoodLog.logged_at >= seven_days_ago)
            )
        )
        recent_food = list(food_res.scalars().all())
        total_meals = len(recent_food)
        confirmed_order = sum(1 for m in recent_food if m.order_confirmed)
        order_pct = (confirmed_order / max(1, total_meals)) * 100.0

        scores = [m.buffer_evaluation.buffer_score for m in recent_food if m.buffer_evaluation]
        avg_buffer = sum(scores) / max(1, len(scores)) if scores else 6.5

        # Exercise triggers
        trigger_res = await db.execute(
            select(ExerciseTrigger).where(
                and_(ExerciseTrigger.user_id == user_id, ExerciseTrigger.trigger_at >= seven_days_ago)
            )
        )
        recent_triggers = list(trigger_res.scalars().all())
        total_trig = len(recent_triggers)
        comp_trig = sum(1 for t in recent_triggers if t.completed)
        trigger_pct = (comp_trig / max(1, total_trig)) * 100.0 if total_trig > 0 else 60.0

        habit_metrics = {
            "avg_buffer_score_7d": avg_buffer,
            "pct_order_confirmed_7d": order_pct,
            "pct_triggers_completed": trigger_pct,
            "sleep_target_adherence_7d": 80.0,
        }

        # 4. Evaluate risk via ML Service
        assessment_result = self.ml_service.evaluate_risk(
            clinical_params=clinical_params,
            profile_data=profile_data,
            habit_metrics=habit_metrics,
        )

        # 5. Persist RiskAssessment
        assessment = RiskAssessment(
            user_id=user_id,
            risk_score=assessment_result["risk_score"],
            risk_level=assessment_result["risk_level"],
            model_version=assessment_result["model_version"],
            features_used=assessment_result["features_used"],
            shap_values=assessment_result["shap_values"],
        )
        db.add(assessment)
        await db.commit()
        await db.refresh(assessment)
        return assessment
