"""Modelos para reportes médicos longitudinales."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ReportGenerateRequest(BaseModel):
    period_start: date
    period_end: date


class MedicalReportResponse(BaseModel):
    id: str
    user_id: str
    generated_at: datetime
    period_start: date
    period_end: date
    adherence_food_order_pct: Optional[float] = None
    adherence_sleep_pct: Optional[float] = None
    adherence_exercise_pct: Optional[float] = None
    report_pdf_url: Optional[str] = None

    model_config = {"from_attributes": True}
