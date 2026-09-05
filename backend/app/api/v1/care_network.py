"""Endpoints de red de cuidado, emparejamiento paciente-cuidador y nudges (F-09, F-10)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserPairing
from app.models.care_network import NudgeEvent
from app.schemas.user import PairingCreate, PairingResponse
from app.schemas.care_network import NudgeEventResponse, NudgeReason, NudgeChannel
from app.services.pairing_service import PairingService
from app.services.nudge_service import NudgeService

router = APIRouter(prefix="/care-network", tags=["Red de Cuidado"])

pairing_service = PairingService()
nudge_service = NudgeService()


@router.post("/pairings", response_model=PairingResponse, status_code=status.HTTP_201_CREATED)
async def create_caregiver_pairing(
    pairing_in: PairingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Vincula la cuenta del paciente con un cuidador designado con permisos granulares."""
    try:
        pairing = await pairing_service.create_pairing(
            db=db,
            patient_id=current_user.id,
            caregiver_email=pairing_in.patient_email,
            permissions=pairing_in.permissions,
        )
        return pairing
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/pairings", response_model=List[PairingResponse])
async def list_pairings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todos los vínculos de cuidadores activos del usuario."""
    pairings = await pairing_service.list_patient_caregivers(db=db, patient_id=current_user.id)
    return pairings


@router.delete("/pairings/{pairing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_pairing(
    pairing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoca inmediatamente el acceso de un cuidador."""
    success = await pairing_service.revoke_pairing(
        db=db, patient_id=current_user.id, pairing_id=pairing_id
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vínculo no encontrado")
    return None


@router.post("/nudges", response_model=List[NudgeEventResponse])
async def dispatch_nudge(
    reason: NudgeReason,
    channel: NudgeChannel = NudgeChannel.push,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Envía un recordatorio de apoyo asincrónico a cuidadores ante desviación de hábitos."""
    events = await nudge_service.trigger_nudge(
        db=db,
        patient_id=current_user.id,
        reason=reason.value,
        channel=channel.value,
    )
    return events


@router.get("/nudges", response_model=List[NudgeEventResponse])
async def list_nudges(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista los eventos de recordatorios que involucran al paciente o cuidador actual."""
    res = await db.execute(
        select(NudgeEvent)
        .where(
            (NudgeEvent.patient_id == current_user.id) | (NudgeEvent.caregiver_id == current_user.id)
        )
        .order_by(NudgeEvent.nudge_sent_at.desc())
    )
    return list(res.scalars().all())
