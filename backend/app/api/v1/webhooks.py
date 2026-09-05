"""Endpoints para recepción y verificación de webhooks de WhatsApp Business Cloud API."""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query, Request, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.services.whatsapp_service import WhatsAppService
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
whatsapp_service = WhatsAppService()
chat_service = ChatService()


@router.get("/whatsapp")
async def verify_whatsapp_webhook(
    request: Request,
):
    """Valida el desafío (hub.challenge) de suscripción del webhook de Meta."""
    params = request.query_params
    mode = params.get("hub.mode", "")
    token = params.get("hub.verify_token", "")
    challenge = params.get("hub.challenge", "")

    verified_challenge = whatsapp_service.verify_webhook_token(
        mode=mode,
        token=token,
        challenge=challenge,
    )
    if verified_challenge is not None:
        return Response(content=verified_challenge, media_type="text/plain")

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verificación de token de WhatsApp fallida",
    )


@router.post("/whatsapp")
async def handle_whatsapp_message(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Procesa mensajes entrantes de WhatsApp y responde mediante el copiloto conversacional."""
    payload = await request.json()
    msg_info = whatsapp_service.parse_incoming_message(payload)

    if not msg_info:
        return {"status": "ignored"}

    sender_phone = msg_info.get("from_phone")
    text_content = msg_info.get("text", "")

    if not sender_phone or not text_content:
        return {"status": "empty_message"}

    # Attempt to locate existing patient by registered phone
    res = await db.execute(select(User).where(User.phone == sender_phone))
    user = res.scalar_one_or_none()

    if not user:
        # Fallback default or demo user
        res_default = await db.execute(select(User).limit(1))
        user = res_default.scalar_one_or_none()

    if user:
        session = await chat_service.get_or_create_session(
            db=db,
            user_id=user.id,
            channel="whatsapp",
        )
        ai_reply = await chat_service.process_user_message(
            db=db,
            session_id=session.id,
            user_message=text_content,
        )
        # Send reply back via WhatsApp Cloud API
        await whatsapp_service.send_message(
            to_phone=sender_phone,
            message_text=ai_reply,
        )

    return {"status": "processed"}
