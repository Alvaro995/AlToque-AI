"""Modelos relacionales para identidad, perfil antropométrico y red de cuidado."""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Float, Date, Enum, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("patient", "caregiver", "doctor", name="user_role"),
        nullable=False,
        default="patient",
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    profile: Mapped["PatientProfile | None"] = relationship(
        "PatientProfile", back_populates="user", uselist=False
    )
    pairings_as_patient: Mapped[list["UserPairing"]] = relationship(
        "UserPairing", foreign_keys="UserPairing.patient_id", back_populates="patient"
    )
    pairings_as_caregiver: Mapped[list["UserPairing"]] = relationship(
        "UserPairing", foreign_keys="UserPairing.caregiver_id", back_populates="caregiver"
    )


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    birth_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str | None] = mapped_column(
        Enum("male", "female", name="biological_sex"), nullable=True
    )
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    activity_level: Mapped[str | None] = mapped_column(
        Enum("sedentary", "light", "moderate", "active", name="activity_level_enum"),
        nullable=True,
        default="sedentary",
    )
    profile_completeness_pct: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")


class UserPairing(Base):
    __tablename__ = "user_pairings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    caregiver_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("pending", "active", "revoked", name="pairing_status"),
        default="pending",
    )
    permissions: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    patient: Mapped["User"] = relationship(
        "User", foreign_keys=[patient_id], back_populates="pairings_as_patient"
    )
    caregiver: Mapped["User"] = relationship(
        "User", foreign_keys=[caregiver_id], back_populates="pairings_as_caregiver"
    )
