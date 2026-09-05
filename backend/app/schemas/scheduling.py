"""Modelos para ventanas metabólicas circadianas y metas de sueño."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time
from enum import Enum


class WindowType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"
    micro_exercise = "micro_exercise"


class MetabolicWindowResponse(BaseModel):
    id: str
    user_id: str
    window_type: str
    optimal_start: time
    optimal_end: time
    day_of_week: int
    generated_at: datetime

    model_config = {"from_attributes": True}


class SleepTargetUpdate(BaseModel):
    target_hours: float = Field(ge=4.0, le=12.0)
    bedtime_target: time
    wakeup_target: time


class SleepTargetResponse(BaseModel):
    id: str
    user_id: str
    target_hours: float
    bedtime_target: time
    wakeup_target: time
    updated_at: datetime

    model_config = {"from_attributes": True}
