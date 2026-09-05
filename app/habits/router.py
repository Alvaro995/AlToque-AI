from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.habits.schemas import (
    HabitEventCreate,
    HabitEventResponse
)
from app.habits.service import HabitService


router = APIRouter(
    prefix="/api/v1/habits",
    tags=["Habits"]
)


@router.post(
    "",
    response_model=HabitEventResponse
)
def create_habit(
    payload: HabitEventCreate,
    db: Session = Depends(get_db)
):
    return HabitService.register_habit(
        db=db,
        payload=payload
    )


@router.get(
    "/{user_id}",
    response_model=list[HabitEventResponse]
)
def get_habits(
    user_id: str,
    db: Session = Depends(get_db)
):
    return HabitService.get_user_habits(
        db=db,
        user_id=user_id
    )