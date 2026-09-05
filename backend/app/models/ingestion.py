"""Modelos para documentos cargados, parámetros clínicos y bloques de horario."""

import uuid
from datetime import datetime, date, time
from sqlalchemy import (
    String, Text, Float, Boolean, Integer, Date, Time,
    Enum, ForeignKey, DateTime, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doc_type: Mapped[str] = mapped_column(
        Enum("clinical", "schedule", name="document_type"), nullable=False
    )
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "processing", "processed", "failed", name="document_status"),
        default="pending",
    )
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    clinical_records: Mapped[list["ClinicalRecord"]] = relationship(
        "ClinicalRecord", back_populates="document"
    )
    schedule_blocks: Mapped[list["ScheduleBlock"]] = relationship(
        "ScheduleBlock", back_populates="document"
    )


class ClinicalRecord(Base):
    __tablename__ = "clinical_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lab_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(
        Enum("ocr", "manual", name="record_source"), default="ocr"
    )
    raw_extraction: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    validated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    document: Mapped["UploadedDocument"] = relationship(
        "UploadedDocument", back_populates="clinical_records"
    )
    parameters: Mapped[list["ClinicalParameter"]] = relationship(
        "ClinicalParameter", back_populates="record", cascade="all, delete-orphan"
    )


class ClinicalParameter(Base):
    __tablename__ = "clinical_parameters"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    record_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clinical_records.id", ondelete="CASCADE"), nullable=False
    )
    parameter_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    ref_range_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    ref_range_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    flag: Mapped[str | None] = mapped_column(
        Enum("normal", "high", "low", "critical", name="parameter_flag"), nullable=True
    )

    # Relationships
    record: Mapped["ClinicalRecord"] = relationship(
        "ClinicalRecord", back_populates="parameters"
    )


class ScheduleBlock(Base):
    __tablename__ = "schedule_blocks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("uploaded_documents.id", ondelete="SET NULL"), nullable=True
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    block_type: Mapped[str] = mapped_column(
        Enum("work", "sleep", "fixed", "commute", name="block_type_enum"), nullable=False
    )
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    document: Mapped["UploadedDocument | None"] = relationship(
        "UploadedDocument", back_populates="schedule_blocks"
    )
