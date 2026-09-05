"""Modelos para contracción muscular GLUT4, rutinas de fuerza y ejercicio."""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, Boolean, Integer, Enum, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ExerciseTrigger(Base):
    __tablename__ = "exercise_triggers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    food_log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("food_logs.id", ondelete="CASCADE"), nullable=False
    )
    trigger_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    notified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    exercise_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_min: Mapped[int] = mapped_column(Integer, default=5)


class StrengthPlan(Base):
    __tablename__ = "strength_plans"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_variant: Mapped[str] = mapped_column(
        Enum("standard", "senior", name="plan_variant_enum"), default="standard"
    )
    focus_area: Mapped[str] = mapped_column(
        Enum("lower_body", "back", "full", name="focus_area_enum"), default="lower_body"
    )
    exercises: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    week_number: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("strength_plans.id", ondelete="SET NULL"), nullable=True
    )
    trigger_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("exercise_triggers.id", ondelete="SET NULL"), nullable=True
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
