"""Modelos para eventos y recordatorios de la red de cuidado."""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Enum, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class NudgeEvent(Base):
    __tablename__ = "nudge_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    caregiver_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    trigger_reason: Mapped[str] = mapped_column(
        Enum("missed_meal", "missed_exercise", "missed_medication", name="nudge_reason_enum"),
        nullable=False,
    )
    missed_block_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    nudge_sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    channel: Mapped[str] = mapped_column(
        Enum("whatsapp", "push", name="nudge_channel_enum"), default="push"
    )
    caregiver_responded: Mapped[bool] = mapped_column(Boolean, default=False)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
