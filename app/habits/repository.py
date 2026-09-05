from sqlalchemy import select
from sqlalchemy.orm import Session

from app.habits.models import HabitEvent


class HabitRepository:

    @staticmethod
    def create(
        db: Session,
        habit: HabitEvent
    ) -> HabitEvent:

        db.add(habit)
        db.commit()
        db.refresh(habit)

        return habit


    @staticmethod
    def get_by_user(
        db: Session,
        user_id: str
    ) -> list[HabitEvent]:

        statement = (
            select(HabitEvent)
            .where(HabitEvent.user_id == user_id)
            .order_by(HabitEvent.event_at.desc())
        )

        return list(
            db.scalars(statement).all()
        )