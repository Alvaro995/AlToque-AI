"""Endpoints para conciliación de ventanas metabólicas y cronobiología (F-03)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.scheduling import MetabolicWindow, SleepTarget
from app.schemas.scheduling import (
    MetabolicWindowResponse,
    SleepTargetResponse,
    SleepTargetUpdate,
)
from app.services.metabolic_window_service import MetabolicWindowService

router = APIRouter(prefix="/scheduling", tags=["Cronobiología"])
window_service = MetabolicWindowService()


@router.post("/reconcile", response_model=List[MetabolicWindowResponse])
async def reconcile_metabolic_windows(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calcula y concilia las ventanas metabólicas óptimas para el paciente."""
    windows = await window_service.calculate_and_reconcile_windows(
        db=db,
        user_id=current_user.id,
    )
    return windows


@router.get("/windows", response_model=List[MetabolicWindowResponse])
async def list_metabolic_windows(
    day_of_week: Optional[int] = Query(None, ge=0, le=6),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista las ventanas metabólicas programadas para el paciente."""
    query = select(MetabolicWindow).where(MetabolicWindow.user_id == current_user.id)
    if day_of_week is not None:
        query = query.where(MetabolicWindow.day_of_week == day_of_week)
    query = query.order_by(MetabolicWindow.day_of_week, MetabolicWindow.optimal_start)

    res = await db.execute(query)
    return list(res.scalars().all())


@router.get("/sleep-target", response_model=SleepTargetResponse)
async def get_sleep_target(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene la meta de descanso circadiano configurada."""
    res = await db.execute(select(SleepTarget).where(SleepTarget.user_id == current_user.id))
    target = res.scalar_one_or_none()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se ha configurado meta de sueño para este usuario",
        )
    return target


@router.put("/sleep-target", response_model=SleepTargetResponse)
async def update_sleep_target(
    target_in: SleepTargetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza metas de sueño y recalcula ventanas metabólicas automáticamente."""
    res = await db.execute(select(SleepTarget).where(SleepTarget.user_id == current_user.id))
    target = res.scalar_one_or_none()

    if not target:
        target = SleepTarget(
            user_id=current_user.id,
            target_hours=target_in.target_hours,
            bedtime_target=target_in.bedtime_target,
            wakeup_target=target_in.wakeup_target,
        )
        db.add(target)
    else:
        target.target_hours = target_in.target_hours
        target.bedtime_target = target_in.bedtime_target
        target.wakeup_target = target_in.wakeup_target

    await db.commit()
    await db.refresh(target)

    # Reconcile windows with updated sleep targets
    await window_service.calculate_and_reconcile_windows(db=db, user_id=current_user.id)
    return target
