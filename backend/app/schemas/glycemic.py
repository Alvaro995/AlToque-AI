"""Modelos de registro de alimentos, buffer glucémico y simulaciones."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MealType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class FoodCategory(str, Enum):
    carbohydrate = "carbohydrate"
    protein = "protein"
    fat = "fat"
    fiber = "fiber"
    mixed = "mixed"


class BufferAlertType(str, Enum):
    isolated_carb = "isolated_carb"
    partial_buffer = "partial_buffer"
    synergy_ok = "synergy_ok"
    acid_boost = "acid_boost"


# --- Food Item Schemas ---

class FoodItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: FoodCategory
    gi_estimate: Optional[float] = Field(None, ge=0, le=100)
    order_position: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None


class FoodItemResponse(BaseModel):
    id: str
    name: str
    category: str
    gi_estimate: Optional[float] = None
    order_position: Optional[int] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


# --- Food Log Schemas ---

class FoodLogCreate(BaseModel):
    meal_type: MealType
    items: list[FoodItemCreate] = []
    window_id: Optional[str] = None


class FoodLogResponse(BaseModel):
    id: str
    user_id: str
    meal_type: str
    order_confirmed: bool
    logged_at: datetime
    items: list[FoodItemResponse] = []

    model_config = {"from_attributes": True}


class FoodOrderConfirm(BaseModel):
    order_confirmed: bool = True


# --- Buffer Evaluation Schemas ---

class BufferEvaluationResponse(BaseModel):
    id: str
    food_log_id: str
    has_buffer: bool
    buffer_score: float
    alert_type: str
    recommendation_text: Optional[str] = None
    evaluated_at: datetime

    model_config = {"from_attributes": True}


# --- Glucose Simulation Schemas ---

class GlucoseCurvePoint(BaseModel):
    time_min: int
    glucose_mg_dl: float


class GlucoseSimulationResponse(BaseModel):
    id: str
    food_log_id: str
    curve_isolated: Optional[list[GlucoseCurvePoint]] = None
    curve_buffered: Optional[list[GlucoseCurvePoint]] = None
    peak_reduction_pct: Optional[float] = None
    simulated_at: datetime

    model_config = {"from_attributes": True}
