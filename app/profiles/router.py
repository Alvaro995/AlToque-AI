from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.profiles.schemas import (
    ProfileCreate,
    ProfileResponse
)

from app.profiles.service import ProfileService


router = APIRouter(
    prefix="/api/v1/profiles",
    tags=["Profiles"]
)


# Crear perfil clínico
@router.post(
    "",
    response_model=ProfileResponse
)
def create_profile(
    payload: ProfileCreate,
    db: Session = Depends(get_db)
):

    return ProfileService.create_profile(
        db=db,
        payload=payload
    )


# Consultar perfil clínico por usuario
@router.get(
    "/{user_id}",
    response_model=ProfileResponse
)
def get_profile(
    user_id: int,
    db: Session = Depends(get_db)
):

    return ProfileService.get_profile(
        db=db,
        user_id=user_id
    )