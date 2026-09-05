"""Servicio de planificación de rutinas de fuerza progresiva (F-08)."""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.physical import StrengthPlan
from app.models.user import PatientProfile


class StrengthPlannerService:
    """Generates biomechanically safe resistance training plans adapted to patient age and mobility."""

    STANDARD_EXERCISES = [
        {"name": "Sentadilla Asistida o Libre", "target": "Cuadriceps y Gluteos", "reps": "3 series de 10-12 reps", "rest_sec": 60},
        {"name": "Puente de Gluteos en Suelo", "target": "Cadena posterior y gluteos", "reps": "3 series de 12-15 reps", "rest_sec": 45},
        {"name": "Remo con Banda Elastica", "target": "Dorsal y escapulares", "reps": "3 series de 12 reps", "rest_sec": 60},
        {"name": "Zancadas Estaticas (Lunge)", "target": "Miembros inferiores", "reps": "2 series de 8 reps por pierna", "rest_sec": 60},
    ]

    SENIOR_EXERCISES = [
        {"name": "Sentarse y Levantarse de Silla", "target": "Movilidad y cuadriceps", "reps": "2 series de 8-10 reps", "rest_sec": 90},
        {"name": "Flexiones contra la Pared", "target": "Pectoral y triceps sin carga lumbar", "reps": "2 series de 10 reps", "rest_sec": 60},
        {"name": "Puente de Gluteos Modificado", "target": "Gluteo medio y estabilidad pelvica", "reps": "2 series de 8-10 reps", "rest_sec": 60},
        {"name": "Elevacion de Talones de Pie con Apoyo", "target": "Soleo y gastrocnemio", "reps": "3 series de 12 reps", "rest_sec": 45},
    ]

    async def generate_weekly_plan(
        self,
        db: AsyncSession,
        user_id: str,
        week_number: int = 1,
        focus_area: str = "lower_body",
    ) -> StrengthPlan:
        """Create or retrieve a personalized progressive strength protocol."""
        profile_res = await db.execute(
            select(PatientProfile).where(PatientProfile.user_id == user_id)
        )
        profile = profile_res.scalar_one_or_none()

        is_senior = False
        if profile and profile.birth_date:
            from datetime import date
            age = (date.today() - profile.birth_date).days // 365
            if age >= 60:
                is_senior = True

        variant = "senior" if is_senior else "standard"
        exercise_list = self.SENIOR_EXERCISES if is_senior else self.STANDARD_EXERCISES

        plan = StrengthPlan(
            user_id=user_id,
            plan_variant=variant,
            focus_area=focus_area,
            week_number=week_number,
            exercises={"protocol": exercise_list, "weekly_frequency": "3 veces por semana"},
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        return plan
