from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.core.database import get_db

from app.users.schemas import (
    UserCreate,
    UserResponse
)

from app.users.service import UserService



router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)



@router.post(
    "",
    response_model=UserResponse
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):

    return UserService.create_user(
        db,
        payload
    )



@router.get(
    "",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):

    return UserService.get_users(db)