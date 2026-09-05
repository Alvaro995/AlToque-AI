from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HabitEvent(Base):
    __tablename__ = "habit_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(50),
        index=True
    )

    habit_type: Mapped[str] = mapped_column(
        String(50),
        index=True
    )

    value: Mapped[float] = mapped_column(
        Float
    )

    unit: Mapped[str] = mapped_column(
        String(30)
    )

    source: Mapped[str] = mapped_column(
        String(30),
        default="APP"
    )

    event_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )