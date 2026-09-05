"""Modelos relacionales para identidad, perfil antropométrico y red de cuidado."""

from pydantic import BaseModel, Field
try:
    import email_validator
    from pydantic import EmailStr
except (ImportError, Exception):
    EmailStr = str

from typing import Optional
from datetime import datetime, date
from enum import Enum


class UserRole(str, Enum):
    patient = "patient"
    caregiver = "caregiver"
    doctor = "doctor"


class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"


class BiologicalSex(str, Enum):
    male = "male"
    female = "female"


# --- Auth Schemas ---

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    phone: Optional[str] = None
    role: UserRole = UserRole.patient


UserCreate = UserRegister


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


# --- User Schemas ---

class UserResponse(BaseModel):
    id: str
    email: str
    phone: Optional[str] = None
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Patient Profile Schemas ---

class PatientProfileCreate(BaseModel):
    birth_date: Optional[date] = None
    sex: Optional[BiologicalSex] = None
    height_cm: Optional[float] = Field(None, ge=50, le=250)
    weight_kg: Optional[float] = Field(None, ge=20, le=300)
    activity_level: Optional[ActivityLevel] = None


class PatientProfileUpdate(BaseModel):
    birth_date: Optional[date] = None
    sex: Optional[BiologicalSex] = None
    height_cm: Optional[float] = Field(None, ge=50, le=250)
    weight_kg: Optional[float] = Field(None, ge=20, le=300)
    activity_level: Optional[ActivityLevel] = None


class PatientProfileResponse(BaseModel):
    id: str
    user_id: str
    birth_date: Optional[date] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    profile_completeness_pct: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileCompletenessResponse(BaseModel):
    completeness_pct: float
    missing_fields: list[str]


# --- Pairing Schemas ---

class PairingStatus(str, Enum):
    pending = "pending"
    active = "active"
    revoked = "revoked"


class PairingCreate(BaseModel):
    patient_email: EmailStr
    permissions: Optional[dict] = Field(
        default_factory=lambda: {
            "view_food_logs": True,
            "view_clinical": False,
            "view_exercise": True,
            "send_nudge": True,
            "view_reports": False,
        }
    )


class PairingUpdate(BaseModel):
    status: Optional[PairingStatus] = None
    permissions: Optional[dict] = None


class PairingResponse(BaseModel):
    id: str
    patient_id: str
    caregiver_id: str
    status: str
    permissions: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}
