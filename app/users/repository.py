from sqlalchemy.orm import Session

from app.users.models import User


class UserRepository:


    @staticmethod
    def create(
        db: Session,
        user: User
    ):

        db.add(user)
        db.commit()
        db.refresh(user)

        return user



    @staticmethod
    def get_all(
        db: Session
    ):

        return db.query(User).all()