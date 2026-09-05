"""Endpoints del asistente conversacional y copiloto clínico (F-11)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.assistant import ChatSession, ChatMessage
from app.schemas.assistant import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionResponse,
    ChatResponse,
    ChatChannel,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Asistente"])
chat_service = ChatService()


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_or_get_session(
    channel: ChatChannel = ChatChannel.app,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Crea u obtiene una sesión de conversación activa."""
    session = await chat_service.get_or_create_session(
        db=db,
        user_id=current_user.id,
        channel=channel.value,
    )
    return session


@router.post("/messages", response_model=ChatResponse)
async def send_message(
    msg_in: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Procesa un mensaje del usuario aplicando guardrails clínicos y RAG."""
    if msg_in.session_id:
        session_res = await db.execute(
            select(ChatSession).where(
                ChatSession.id == msg_in.session_id,
                ChatSession.user_id == current_user.id,
            )
        )
        session = session_res.scalar_one_or_none()
        if not session:
            session = await chat_service.get_or_create_session(db=db, user_id=current_user.id)
    else:
        session = await chat_service.get_or_create_session(db=db, user_id=current_user.id)

    reply_content = await chat_service.process_user_message(
        db=db,
        session_id=session.id,
        user_message=msg_in.content,
    )

    # Obtener el último mensaje del asistente registrado
    res = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id, ChatMessage.role == "assistant")
        .order_by(ChatMessage.created_at.desc())
    )
    last_assistant_msg = res.scalars().first()

    return {
        "session_id": session.id,
        "message": last_assistant_msg,
    }


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def list_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista el historial cronológico de mensajes de una sesión."""
    session_res = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    if not session_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada")

    res = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return list(res.scalars().all())
