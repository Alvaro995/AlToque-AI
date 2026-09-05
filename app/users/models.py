from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):

    __tablename__ = "users"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )


    name: Mapped[str] = mapped_column(
        String(100)
    )


    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )


    age: Mapped[int] = mapped_column(
        Integer
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


    habits = relationship(
        "HabitEvent",
        back_populates="user"
    )