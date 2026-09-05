"""Modelos para evaluaciones predictivas de riesgo metabólico y factores SHAP."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Enum, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assessed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(
        Enum("low", "moderate", "high", "critical", name="risk_level_enum"),
        nullable=False,
    )
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    features_used: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    shap_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
