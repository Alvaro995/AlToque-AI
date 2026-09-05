"""Modelos para reportes médicos longitudinales."""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    adherence_food_order_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    adherence_sleep_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    adherence_exercise_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    report_pdf_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
