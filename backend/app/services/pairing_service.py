"""Servicio de vinculación paciente-cuidador y permisos granulares (F-09)."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.user import UserPairing, User
from app.schemas.user import PairingCreate


class PairingService:
    """Orchestrates secure patient-caregiver linkages and permission checks."""

    DEFAULT_PERMISSIONS = {
        "view_meals": True,
        "view_glucose": True,
        "view_reports": True,
        "receive_nudges": True,
    }

    async def create_pairing(
        self,
        db: AsyncSession,
        patient_id: str,
        caregiver_email: str,
        permissions: Optional[Dict[str, bool]] = None,
    ) -> UserPairing:
        """Initiate or activate pairing with a designated caregiver."""
        res = await db.execute(select(User).where(User.email == caregiver_email))
        caregiver = res.scalar_one_or_none()
        if not caregiver:
            raise ValueError(f"No existe usuario registrado con el correo: {caregiver_email}")

        # Check if pairing already exists
        existing_res = await db.execute(
            select(UserPairing).where(
                and_(
                    UserPairing.patient_id == patient_id,
                    UserPairing.caregiver_id == caregiver.id,
                )
            )
        )
        pairing = existing_res.scalar_one_or_none()
        perms = permissions or self.DEFAULT_PERMISSIONS

        if pairing:
            pairing.status = "active"
            pairing.permissions = perms
        else:
            pairing = UserPairing(
                patient_id=patient_id,
                caregiver_id=caregiver.id,
                status="active",
                permissions=perms,
            )
            db.add(pairing)

        await db.commit()
        await db.refresh(pairing)
        return pairing

    async def list_patient_caregivers(
        self, db: AsyncSession, patient_id: str
    ) -> List[UserPairing]:
        """List all active or pending pairings for a patient."""
        res = await db.execute(
            select(UserPairing).where(UserPairing.patient_id == patient_id)
        )
        return list(res.scalars().all())

    async def revoke_pairing(
        self, db: AsyncSession, patient_id: str, pairing_id: str
    ) -> bool:
        """Revoke caregiver access immediately."""
        res = await db.execute(
            select(UserPairing).where(
                and_(
                    UserPairing.id == pairing_id,
                    UserPairing.patient_id == patient_id,
                )
            )
        )
        pairing = res.scalar_one_or_none()
        if not pairing:
            return False
        pairing.status = "revoked"
        await db.commit()
        return True
