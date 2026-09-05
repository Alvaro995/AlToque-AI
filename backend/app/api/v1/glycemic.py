"""Endpoints del motor glucémico: registro, buffer, secuenciación y simulación (F-04 a F-06)."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.glycemic import FoodLog, FoodItem, BufferEvaluation, GlucoseSimulation
from app.schemas.glycemic import (
    FoodLogCreate,
    FoodLogResponse,
    FoodOrderConfirm,
    BufferEvaluationResponse,
    GlucoseSimulationResponse,
)
from app.services.glycemic_buffer_service import GlycemicBufferService
from app.services.food_order_service import FoodOrderService
from app.services.glucose_simulator_service import GlucoseSimulatorService
from app.services.muscle_sink_service import MuscleSinkService

router = APIRouter(prefix="/glycemic", tags=["Motor Glucémico"])

buffer_service = GlycemicBufferService()
order_service = FoodOrderService()
simulator_service = GlucoseSimulatorService()
muscle_service = MuscleSinkService()


@router.post("/food-logs", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def log_meal(
    log_in: FoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Registra una comida, evalúa buffer glucémico y genera curva simulada."""
    food_log = FoodLog(
        user_id=current_user.id,
        meal_type=log_in.meal_type.value,
        window_id=log_in.window_id,
        order_confirmed=False,
    )
    db.add(food_log)
    await db.flush()

    for item_data in log_in.items:
        food_item = FoodItem(
            food_log_id=food_log.id,
            name=item_data.name,
            category=item_data.category.value,
            gi_estimate=item_data.gi_estimate,
            order_position=item_data.order_position,
            notes=item_data.notes,
        )
        db.add(food_item)

    await db.commit()
    await db.refresh(food_log)

    # Recargar con alimentos asociados
    res = await db.execute(
        select(FoodLog).where(FoodLog.id == food_log.id).options(selectinload(FoodLog.items))
    )
    full_log = res.scalar_one()

    # 1. Evaluación de amortiguación glucémica
    await buffer_service.evaluate_and_persist(db=db, food_log=full_log)

    # 2. Simulación de curva de glucosa postprandial
    await simulator_service.simulate_for_food_log(db=db, food_log=full_log)

    # 3. Programación de contracción muscular (35 min postprandial)
    await muscle_service.schedule_postprandial_trigger(
        db=db,
        user_id=current_user.id,
        food_log_id=full_log.id,
    )

    return full_log


@router.get("/food-logs", response_model=List[FoodLogResponse])
async def list_food_logs(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista las comidas registradas en orden cronológico."""
    res = await db.execute(
        select(FoodLog)
        .where(FoodLog.user_id == current_user.id)
        .options(selectinload(FoodLog.items))
        .order_by(FoodLog.logged_at.desc())
        .limit(limit)
    )
    return list(res.scalars().all())


@router.get("/food-logs/{log_id}/buffer", response_model=BufferEvaluationResponse)
async def get_buffer_evaluation(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene la evaluación de buffer glucémico y recomendaciones de mitigación."""
    res = await db.execute(
        select(BufferEvaluation)
        .join(FoodLog)
        .where(BufferEvaluation.food_log_id == log_id, FoodLog.user_id == current_user.id)
    )
    evaluation = res.scalar_one_or_none()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluación de buffer no encontrada para esta comida",
        )
    return evaluation


@router.get("/food-logs/{log_id}/simulation")
async def get_glucose_simulation(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene curvas comparativas de glucosa postprandial simuladas."""
    res = await db.execute(
        select(GlucoseSimulation)
        .join(FoodLog)
        .where(GlucoseSimulation.food_log_id == log_id, FoodLog.user_id == current_user.id)
    )
    sim = res.scalar_one_or_none()
    if not sim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulación glucémica no encontrada para esta comida",
        )
    return {
        "id": sim.id,
        "food_log_id": sim.food_log_id,
        "curve_isolated": sim.curve_isolated.get("points", []) if sim.curve_isolated else [],
        "curve_buffered": sim.curve_buffered.get("points", []) if sim.curve_buffered else [],
        "peak_reduction_pct": sim.peak_reduction_pct,
        "simulated_at": sim.simulated_at,
    }


@router.post("/sequence-optimize")
async def optimize_food_sequence(items: List[Dict[str, Any]]):
    """Calcula el orden cronológico óptimo de ingesta (fibra -> proteína -> carbohidrato)."""
    ordered = order_service.get_optimal_sequence(items)
    return {
        "optimized_sequence": ordered,
        "protocol": "Weill Cornell / Shukla GLP-1 mucosal buffering",
    }


@router.post("/simulate")
async def simulate_custom_curve(
    baseline_glucose: float = 95.0,
    carb_load_grams: float = 50.0,
    buffer_score: float = 7.0,
):
    """Simulador educativo interactivo de curvas glucémicas postprandiales."""
    return simulator_service.generate_curves(
        baseline_glucose=baseline_glucose,
        carb_load_grams=carb_load_grams,
        buffer_score=buffer_score,
    )
