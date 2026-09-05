"""Servicio de recordatorios asincrónicos no punitivos para la red de cuidado (F-10)."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.care_network import NudgeEvent
from app.models.user import UserPairing, User


class NudgeService:
    """Dispatches empathic, actionable nudges to family caregivers upon metabolic deviations."""

    NUDGE_TEMPLATES = {
        "missed_meal": (
            "Notificacion de acompanamiento: Hemos detectado que {patient_name} no ha registrado "
            "su comida dentro de la ventana metabolica habitual. Un breve saludo o recordatorio cariñoso "
            "puede facilitarle mantener su regularidad."
        ),
        "missed_exercise": (
            "Pausa activa sugerida: {patient_name} tiene pendiente su estimulo de movimiento postprandial. "
            "Invitarle a una breve caminata de 10 minutos juntos fortalecera su salud metabólica."
        ),
        "missed_medication": (
            "Recordatorio preventivo: Es momento oportuno para verificar que {patient_name} haya "
            "tomado sus suplementos o indicacion medica del dia."
        ),
    }

    async def trigger_nudge(
        self,
        db: AsyncSession,
        patient_id: str,
        reason: str,
        missed_time: Optional[datetime] = None,
        channel: str = "push",
    ) -> List[NudgeEvent]:
        """Evaluate active caregivers and dispatch non-invasive nudge events."""
        pairings_res = await db.execute(
            select(UserPairing).where(
                and_(
                    UserPairing.patient_id == patient_id,
                    UserPairing.status == "active",
                )
            )
        )
        active_pairings = list(pairings_res.scalars().all())

        patient_res = await db.execute(select(User).where(User.id == patient_id))
        patient = patient_res.scalar_one_or_none()
        patient_name = patient.full_name if patient else "el paciente"

        created_events: List[NudgeEvent] = []
        event_time = missed_time or datetime.utcnow()

        for pairing in active_pairings:
            perms = pairing.permissions or {}
            if not perms.get("receive_nudges", True):
                continue

            nudge = NudgeEvent(
                patient_id=patient_id,
                caregiver_id=pairing.caregiver_id,
                trigger_reason=reason,
                missed_block_time=event_time,
                channel=channel,
                caregiver_responded=False,
            )
            db.add(nudge)
            created_events.append(nudge)

        await db.commit()
        return created_events

    def format_nudge_text(self, patient_name: str, reason: str) -> str:
        """Format non-alarmist caregiver nudge text."""
        template = self.NUDGE_TEMPLATES.get(
            reason,
            "Recordatorio de seguimiento preventivo para {patient_name}."
        )
        return template.format(patient_name=patient_name)
