from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


HabitSource = Literal[
    "APP",
    "WHATSAPP",
    "WEARABLE",
    "IMPORTED_DOCUMENT",
    "SYSTEM"
]


class HabitEventCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=50)
    habit_type: str = Field(min_length=1, max_length=50)
    value: float
    unit: str = Field(min_length=1, max_length=30)
    source: HabitSource = "APP"
    event_at: datetime | None = None


class HabitEventResponse(BaseModel):
    id: int
    user_id: str
    habit_type: str
    value: float
    unit: str
    source: str
    event_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)