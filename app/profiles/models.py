from datetime import datetime

from sqlalchemy import (
    Integer,
    Float,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.core.database import Base


class ClinicalProfile(Base):

    __tablename__ = "clinical_profiles"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )


    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )


    weight: Mapped[float] = mapped_column(
        Float
    )


    height: Mapped[float] = mapped_column(
        Float
    )


    glucose: Mapped[float] = mapped_column(
        Float
    )


    hba1c: Mapped[float] = mapped_column(
        Float
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )