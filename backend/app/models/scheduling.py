"""Modelos para ventanas metabólicas circadianas y metas de sueño."""

import uuid
from datetime import datetime, time
from sqlalchemy import String, Float, Integer, Time, Enum, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MetabolicWindow(Base):
    __tablename__ = "metabolic_windows"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    window_type: Mapped[str] = mapped_column(
        Enum(
            "breakfast", "lunch", "dinner", "snack", "micro_exercise",
            name="window_type_enum",
        ),
        nullable=False,
    )
    optimal_start: Mapped[time] = mapped_column(Time, nullable=False)
    optimal_end: Mapped[time] = mapped_column(Time, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SleepTarget(Base):
    __tablename__ = "sleep_targets"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    target_hours: Mapped[float] = mapped_column(Float, default=7.0)
    bedtime_target: Mapped[time] = mapped_column(Time, nullable=False)
    wakeup_target: Mapped[time] = mapped_column(Time, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
