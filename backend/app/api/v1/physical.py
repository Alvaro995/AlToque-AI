"""Endpoints para actividad física, contracción muscular GLUT4 y fuerza (F-07, F-08)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.physical import ExerciseTrigger, StrengthPlan, ExerciseLog
from app.schemas.physical import (
    ExerciseTriggerResponse,
    ExerciseTriggerComplete,
    StrengthPlanGenerate,
    StrengthPlanResponse,
    ExerciseLogCreate,
    ExerciseLogResponse,
)
from app.services.muscle_sink_service import MuscleSinkService
from app.services.strength_planner_service import StrengthPlannerService

router = APIRouter(prefix="/physical", tags=["Actividad Física"])

muscle_service = MuscleSinkService()
strength_service = StrengthPlannerService()


@router.get("/triggers", response_model=List[ExerciseTriggerResponse])
async def list_exercise_triggers(
    completed: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista los recordatorios de activación muscular postprandial."""
    query = select(ExerciseTrigger).where(ExerciseTrigger.user_id == current_user.id)
    if completed is not None:
        query = query.where(ExerciseTrigger.completed == completed)
    query = query.order_by(ExerciseTrigger.trigger_at.desc())

    res = await db.execute(query)
    return list(res.scalars().all())


@router.post("/triggers/{trigger_id}/complete", response_model=ExerciseLogResponse)
async def complete_exercise_trigger(
    trigger_id: str,
    complete_in: ExerciseTriggerComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Marca un recordatorio de contracción como completado y registra la duración."""
    try:
        log = await muscle_service.mark_trigger_completed(
            db=db,
            trigger_id=trigger_id,
            duration_min=complete_in.duration_min,
            notes=f"Tipo: {complete_in.exercise_type}",
        )
        return log
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/strength-plan/generate", response_model=StrengthPlanResponse)
async def generate_strength_plan(
    plan_in: StrengthPlanGenerate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Genera una rutina de fuerza progresiva para sensibilización insulínica."""
    plan = await strength_service.generate_weekly_plan(
        db=db,
        user_id=current_user.id,
        focus_area=plan_in.focus_area.value,
    )
    return plan


@router.get("/strength-plan/active", response_model=StrengthPlanResponse)
async def get_active_strength_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene el plan de fuerza activo actualmente para el paciente."""
    res = await db.execute(
        select(StrengthPlan)
        .where(StrengthPlan.user_id == current_user.id)
        .order_by(StrengthPlan.created_at.desc())
    )
    plan = res.scalars().first()
    if not plan:
        plan = await strength_service.generate_weekly_plan(db=db, user_id=current_user.id)
    return plan


@router.post("/logs", response_model=ExerciseLogResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise_log(
    log_in: ExerciseLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Registra manualmente una sesión de ejercicio o actividad física."""
    log = ExerciseLog(
        user_id=current_user.id,
        plan_id=log_in.plan_id,
        trigger_id=log_in.trigger_id,
        duration_min=log_in.duration_min,
        notes=log_in.notes,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.get("/logs", response_model=List[ExerciseLogResponse])
async def list_exercise_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista las sesiones de actividad física completadas recientemente."""
    res = await db.execute(
        select(ExerciseLog)
        .where(ExerciseLog.user_id == current_user.id)
        .order_by(ExerciseLog.completed_at.desc())
    )
    return list(res.scalars().all())
