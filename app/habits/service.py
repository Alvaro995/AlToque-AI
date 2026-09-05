from datetime import datetime

from sqlalchemy.orm import Session

from app.habits.models import HabitEvent
from app.habits.repository import HabitRepository
from app.habits.schemas import HabitEventCreate


class HabitService:

    @staticmethod
    def register_habit(
        db: Session,
        payload: HabitEventCreate
    ) -> HabitEvent:

        event = HabitEvent(
            user_id=payload.user_id,
            habit_type=payload.habit_type,
            value=payload.value,
            unit=payload.unit,
            source=payload.source,
            event_at=payload.event_at or datetime.utcnow()
        )

        return HabitRepository.create(
            db=db,
            habit=event
        )


    @staticmethod
    def get_user_habits(
        db: Session,
        user_id: str
    ) -> list[HabitEvent]:

        return HabitRepository.get_by_user(
            db=db,
            user_id=user_id
        )