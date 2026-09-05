"""Servicio de activación de captación muscular GLUT4 postprandial (F-07)."""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.physical import ExerciseTrigger, ExerciseLog


class MuscleSinkService:
    """Manages post-meal muscle contraction prompts to optimize non-insulin glucose clearance."""

    EXERCISE_OPTIONS = [
        {
            "type": "soleus_pushups",
            "name": "Elevaciones de Talón en Sedestación (Soleus Pushups)",
            "duration_min": 10,
            "description": "Contracciones ritmicas del soleo sentado en escritorio. Activa el metabolismo oxidativo sin fatiga sistemica.",
            "setting": "desk/work",
        },
        {
            "type": "brisk_walk",
            "name": "Caminata Ligera Postprandial",
            "duration_min": 15,
            "description": "Paseo a paso comodo y continuo para drenar la glucosa circulante hacia las extremidades inferiores.",
            "setting": "outdoor/indoor",
        },
        {
            "type": "chair_squats",
            "name": "Sentadillas en Silla",
            "duration_min": 5,
            "description": "2 series de 10-12 repeticiones de sentarse y levantarse. Moviliza los grandes grupos musculares cuadriceps y gluteos.",
            "setting": "home/office",
        },
    ]

    async def schedule_postprandial_trigger(
        self,
        db: AsyncSession,
        user_id: str,
        food_log_id: str,
        meal_time: Optional[datetime] = None,
        delay_minutes: int = 35,
    ) -> ExerciseTrigger:
        """
        Create an exercise trigger scheduled 30-45 minutes post meal,
        aligning with the onset of postprandial glucose elevation.
        """
        base_time = meal_time or datetime.utcnow()
        trigger_target = base_time + timedelta(minutes=delay_minutes)

        trigger = ExerciseTrigger(
            user_id=user_id,
            food_log_id=food_log_id,
            trigger_at=trigger_target,
            completed=False,
            exercise_type="soleus_pushups",
            duration_min=10,
        )
        db.add(trigger)
        await db.commit()
        await db.refresh(trigger)
        return trigger

    async def mark_trigger_completed(
        self,
        db: AsyncSession,
        trigger_id: str,
        duration_min: int = 10,
        notes: Optional[str] = None,
    ) -> ExerciseLog:
        """Log exercise completion and link with trigger."""
        result = await db.execute(select(ExerciseTrigger).where(ExerciseTrigger.id == trigger_id))
        trigger = result.scalar_one_or_none()
        if not trigger:
            raise ValueError("Trigger not found")

        trigger.completed = True
        log = ExerciseLog(
            user_id=trigger.user_id,
            trigger_id=trigger.id,
            completed_at=datetime.utcnow(),
            duration_min=duration_min,
            notes=notes or f"Completado: {trigger.exercise_type}",
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log
