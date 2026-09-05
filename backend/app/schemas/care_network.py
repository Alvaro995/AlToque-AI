"""Modelos para eventos y recordatorios de la red de cuidado."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class NudgeReason(str, Enum):
    missed_meal = "missed_meal"
    missed_exercise = "missed_exercise"
    missed_medication = "missed_medication"


class NudgeChannel(str, Enum):
    whatsapp = "whatsapp"
    push = "push"


class NudgeEventResponse(BaseModel):
    id: str
    patient_id: str
    caregiver_id: str
    trigger_reason: str
    missed_block_time: datetime
    nudge_sent_at: datetime
    channel: str
    caregiver_responded: bool
    responded_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class NudgeRespondRequest(BaseModel):
    message: Optional[str] = None
