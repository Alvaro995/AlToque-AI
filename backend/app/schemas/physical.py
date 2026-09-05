"""Modelos para contracción muscular GLUT4, rutinas de fuerza y ejercicio."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PlanVariant(str, Enum):
    standard = "standard"
    senior = "senior"


class FocusArea(str, Enum):
    lower_body = "lower_body"
    back = "back"
    full = "full"


# --- Exercise Trigger Schemas ---

class ExerciseTriggerResponse(BaseModel):
    id: str
    user_id: str
    food_log_id: str
    trigger_at: datetime
    notified_at: Optional[datetime] = None
    completed: bool
    exercise_type: Optional[str] = None
    duration_min: int

    model_config = {"from_attributes": True}


class ExerciseTriggerComplete(BaseModel):
    exercise_type: str = Field(min_length=1, max_length=100)
    duration_min: int = Field(ge=1, le=120)


# --- Strength Plan Schemas ---

class StrengthPlanGenerate(BaseModel):
    plan_variant: PlanVariant = PlanVariant.standard
    focus_area: FocusArea = FocusArea.lower_body


class ExerciseDetail(BaseModel):
    name: str
    sets: int
    reps: int
    rest_seconds: int
    notes: Optional[str] = None


class StrengthPlanResponse(BaseModel):
    id: str
    user_id: str
    plan_variant: str
    focus_area: str
    exercises: Optional[list[ExerciseDetail]] = None
    week_number: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Exercise Log Schemas ---

class ExerciseLogCreate(BaseModel):
    plan_id: Optional[str] = None
    trigger_id: Optional[str] = None
    duration_min: int = Field(ge=1, le=180)
    notes: Optional[str] = None


class ExerciseLogResponse(BaseModel):
    id: str
    user_id: str
    plan_id: Optional[str] = None
    trigger_id: Optional[str] = None
    completed_at: datetime
    duration_min: int
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
