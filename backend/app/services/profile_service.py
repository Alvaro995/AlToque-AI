"""Servicio de gestión de perfil antropométrico y completitud progresiva."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import PatientProfile, User
from app.schemas.user import PatientProfileUpdate


class ProfileService:
    """Calculates anthropometrics and updates profile state."""

    @staticmethod
    def calculate_bmi(weight_kg: Optional[float], height_cm: Optional[float]) -> Optional[float]:
        """Compute Body Mass Index (kg/m^2)."""
        if not weight_kg or not height_cm or height_cm <= 0:
            return None
        height_m = height_cm / 100.0
        return round(weight_kg / (height_m * height_m), 1)

    @staticmethod
    def calculate_completeness(profile: PatientProfile) -> float:
        """Calculate profile completeness percentage."""
        fields = [
            profile.birth_date,
            profile.sex,
            profile.height_cm,
            profile.weight_kg,
            profile.activity_level,
        ]
        filled = sum(1 for f in fields if f is not None)
        return round((filled / len(fields)) * 100.0, 1)

    async def get_profile_by_user_id(
        self, db: AsyncSession, user_id: str
    ) -> Optional[PatientProfile]:
        """Fetch profile for user."""
        res = await db.execute(select(PatientProfile).where(PatientProfile.user_id == user_id))
        return res.scalar_one_or_none()

    async def update_profile(
        self, db: AsyncSession, user_id: str, update_data: PatientProfileUpdate
    ) -> PatientProfile:
        """Update anthropometrics and recalculate completeness."""
        profile = await self.get_profile_by_user_id(db, user_id)
        if not profile:
            profile = PatientProfile(user_id=user_id)
            db.add(profile)

        for key, val in update_data.model_dump(exclude_unset=True).items():
            setattr(profile, key, val)

        profile.profile_completeness_pct = self.calculate_completeness(profile)
        await db.commit()
        await db.refresh(profile)
        return profile
