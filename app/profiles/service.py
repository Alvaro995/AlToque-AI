from sqlalchemy.orm import Session

from app.profiles.models import ClinicalProfile
from app.profiles.schemas import ProfileCreate
from app.profiles.repository import ProfileRepository


class ProfileService:


    @staticmethod
    def create_profile(
        db: Session,
        payload: ProfileCreate
    ):

        profile = ClinicalProfile(

            user_id=payload.user_id,
            weight=payload.weight,
            height=payload.height,
            glucose=payload.glucose,
            hba1c=payload.hba1c

        )


        return ProfileRepository.create(
            db,
            profile
        )


    @staticmethod
    def get_profile(
        db: Session,
        user_id: int
    ):

        return ProfileRepository.get_by_user(
            db,
            user_id
        )