"""Modelos de registro de alimentos, buffer glucémico y simulaciones."""

import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, Float, Boolean, Integer,
    Enum, ForeignKey, DateTime, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class FoodLog(Base):
    __tablename__ = "food_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    meal_type: Mapped[str] = mapped_column(
        Enum("breakfast", "lunch", "dinner", "snack", name="meal_type_enum"),
        nullable=False,
    )
    window_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("metabolic_windows.id", ondelete="SET NULL"), nullable=True
    )
    order_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    items: Mapped[list["FoodItem"]] = relationship(
        "FoodItem", back_populates="food_log", cascade="all, delete-orphan"
    )
    buffer_evaluation: Mapped["BufferEvaluation | None"] = relationship(
        "BufferEvaluation", back_populates="food_log", uselist=False
    )
    glucose_simulation: Mapped["GlucoseSimulation | None"] = relationship(
        "GlucoseSimulation", back_populates="food_log", uselist=False
    )


class FoodItem(Base):
    __tablename__ = "food_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    food_log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("food_logs.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(
        Enum("carbohydrate", "protein", "fat", "fiber", "mixed", name="food_category_enum"),
        nullable=False,
    )
    gi_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    order_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    food_log: Mapped["FoodLog"] = relationship("FoodLog", back_populates="items")


class BufferEvaluation(Base):
    __tablename__ = "buffer_evaluations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    food_log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("food_logs.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    has_buffer: Mapped[bool] = mapped_column(Boolean, default=False)
    buffer_score: Mapped[float] = mapped_column(Float, default=0.0)
    alert_type: Mapped[str] = mapped_column(
        Enum(
            "isolated_carb", "partial_buffer", "synergy_ok", "acid_boost",
            name="buffer_alert_enum",
        ),
        nullable=False,
    )
    recommendation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    food_log: Mapped["FoodLog"] = relationship("FoodLog", back_populates="buffer_evaluation")


class GlucoseSimulation(Base):
    __tablename__ = "glucose_simulations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    food_log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("food_logs.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    curve_isolated: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    curve_buffered: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    peak_reduction_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    simulated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    food_log: Mapped["FoodLog"] = relationship("FoodLog", back_populates="glucose_simulation")
