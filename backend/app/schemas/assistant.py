"""Modelos para sesiones y mensajes del asistente conversacional."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ChatChannel(str, Enum):
    app = "app"
    whatsapp = "whatsapp"


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"
    tool = "tool"


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    session_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    tool_calls: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    channel: str
    started_at: datetime
    last_message_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    message: ChatMessageResponse
    session_id: str
