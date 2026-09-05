from sqlalchemy.orm import Session

from app.users.models import User
from app.users.schemas import UserCreate
from app.users.repository import UserRepository



class UserService:


    @staticmethod
    def create_user(
        db: Session,
        payload: UserCreate
    ):

        user = User(

            name=payload.name,
            email=payload.email,
            age=payload.age

        )


        return UserRepository.create(
            db,
            user
        )



    @staticmethod
    def get_users(
        db: Session
    ):

        return UserRepository.get_all(db)