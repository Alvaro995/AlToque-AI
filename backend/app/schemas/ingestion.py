"""Modelos para documentos cargados, parámetros clínicos y bloques de horario."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, time
from enum import Enum


class DocumentType(str, Enum):
    clinical = "clinical"
    schedule = "schedule"


class DocumentStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class ParameterFlag(str, Enum):
    normal = "normal"
    high = "high"
    low = "low"
    critical = "critical"


class BlockType(str, Enum):
    work = "work"
    sleep = "sleep"
    fixed = "fixed"
    commute = "commute"


# --- Document Schemas ---

class DocumentUploadResponse(BaseModel):
    id: str
    doc_type: str
    status: str
    original_filename: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentStatusResponse(BaseModel):
    id: str
    doc_type: str
    status: str
    error_detail: Optional[str] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# --- Clinical Record Schemas ---

class ClinicalParameterResponse(BaseModel):
    id: str
    parameter_name: str
    value: float
    unit: str
    ref_range_low: Optional[float] = None
    ref_range_high: Optional[float] = None
    flag: Optional[str] = None

    model_config = {"from_attributes": True}


class ClinicalParameterCorrection(BaseModel):
    parameter_name: str
    value: float
    unit: str
    ref_range_low: Optional[float] = None
    ref_range_high: Optional[float] = None


class ClinicalRecordResponse(BaseModel):
    id: str
    document_id: str
    lab_date: Optional[date] = None
    source: str
    validated: bool
    parameters: list[ClinicalParameterResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ClinicalRecordValidation(BaseModel):
    lab_date: Optional[date] = None
    corrections: Optional[list[ClinicalParameterCorrection]] = None


# --- Schedule Block Schemas ---

class ScheduleBlockCreate(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    block_type: BlockType
    label: Optional[str] = None


class ScheduleBlockUpdate(BaseModel):
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    block_type: Optional[BlockType] = None
    label: Optional[str] = None


class ScheduleBlockResponse(BaseModel):
    id: str
    user_id: str
    day_of_week: int
    start_time: time
    end_time: time
    block_type: str
    label: Optional[str] = None

    model_config = {"from_attributes": True}
