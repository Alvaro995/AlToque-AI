from sqlalchemy.orm import Session

from app.profiles.models import ClinicalProfile


class ProfileRepository:


    @staticmethod
    def create(
        db: Session,
        profile: ClinicalProfile
    ):

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile


    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int
    ):

        return (
            db.query(ClinicalProfile)
            .filter(
                ClinicalProfile.user_id == user_id
            )
            .order_by(
                ClinicalProfile.created_at.desc()
            )
            .first()
        )