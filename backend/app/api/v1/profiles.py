"""Endpoints de perfil antropométrico e indicadores de estilo de vida del paciente."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, PatientProfile
from app.schemas.user import PatientProfileResponse, PatientProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["Perfiles"])
profile_service = ProfileService()


@router.get("/me", response_model=PatientProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene el perfil antropométrico y de estilo de vida del paciente."""
    profile = await profile_service.get_profile_by_user_id(db, current_user.id)
    if not profile:
        profile = PatientProfile(user_id=current_user.id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


@router.put("/me", response_model=PatientProfileResponse)
async def update_my_profile(
    profile_in: PatientProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza medidas antropométricas y recalcula completitud de perfil."""
    profile = await profile_service.update_profile(
        db=db,
        user_id=current_user.id,
        update_data=profile_in,
    )
    return profile
