"""Servicio del copiloto conversacional con guardrails clínicos y RAG (F-11)."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.assistant import ChatSession, ChatMessage
from app.models.user import User, PatientProfile
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService


class ChatService:
    """Conversational assistant managing multi-channel sessions and clinical safety guardrails."""

    SYSTEM_PROMPT_BASE = (
        "Eres el copiloto preventivo de salud metabolica AlToque AI. Tu funcion es educar, "
        "acompanar y motivar a personas con prediabetes o riesgo metabolico.\n\n"
        "REGLAS CLINICAS ESTRICTAS:\n"
        "1. NO diagnostiques enfermedades ni sustituyas al profesional de salud.\n"
        "2. NO recetes, modifiques ni recomiendes medicamentos ni dosis (metformina, insulina, etc.).\n"
        "3. Enfocate en recomendaciones de habitos basadas en evidencia: orden de consumo de alimentos, "
        "amortiguacion de carbohidratos, contraccion muscular del soleo y respeto a los ritmos circadianos.\n"
        "4. Si el usuario describe sintomas de emergencia (confusion mental aguda, sudor frio profuso, "
        "perdida de conciencia, dolor toracico), indicale buscar atencion de urgencia medica de inmediato.\n"
        "5. Manten un tono profesional, empatico, claro y sin jerga incomprensible."
    )

    RED_FLAGS = [
        "desmayo", "perder la conciencia", "dolor de pecho", "vision borrosa severa",
        "falta de aire", "convulsion", "sudor frio y temblor",
    ]

    MEDICATION_KEYWORDS = [
        "metformina", "glibenclamida", "insulina", "dosis", "recetar", "pastilla para la diabetes",
    ]

    def __init__(self):
        self.llm = LLMService()
        self.rag = RAGService()

    def check_safety_boundaries(self, text: str) -> Optional[str]:
        """Verify if prompt triggers clinical guardrails or red flags."""
        lower = text.lower()

        # Emergency red flag
        for flag in self.RED_FLAGS:
            if flag in lower:
                return (
                    "ALERTA CLINICA: Los sintomas que describe requieren valoracion medica de urgencia. "
                    "Por favor acuda al centro hospitalario mas cercano o contacte al servicio de emergencias medicas "
                    "de forma inmediata."
                )

        # Medication request guardrail
        for med in self.MEDICATION_KEYWORDS:
            if med in lower and ("tomar" in lower or "cuanto" in lower or "receta" in lower or "debo" in lower):
                return (
                    "Aviso de seguridad medica: Como asistente preventivo de AlToque AI, no tengo permitido recetar, "
                    "recomendar ni alterar esquemas farmacologicos. Cualquier indicacion o ajuste de farmacos "
                    "debe ser prescrita exclusivamente por su medico tratante."
                )

        return None

    async def get_or_create_session(
        self,
        db: AsyncSession,
        user_id: str,
        channel: str = "app",
    ) -> ChatSession:
        """Retrieve existing active session or instantiate a new one."""
        res = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id, ChatSession.channel == channel)
            .order_by(ChatSession.last_message_at.desc())
        )
        session = res.scalars().first()
        if not session:
            session = ChatSession(
                user_id=user_id,
                channel=channel,
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
        return session

    async def process_user_message(
        self,
        db: AsyncSession,
        session_id: str,
        user_message: str,
    ) -> str:
        """Execute conversational turn with safety validation, RAG context, and persistence."""
        # 1. Store user message
        msg_user = ChatMessage(
            session_id=session_id,
            role="user",
            content=user_message,
        )
        db.add(msg_user)
        await db.commit()

        # 2. Check safety guardrails
        safety_override = self.check_safety_boundaries(user_message)
        if safety_override:
            msg_assistant = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=safety_override,
            )
            db.add(msg_assistant)
            await db.commit()
            return safety_override

        # 3. Retrieve clinical knowledge context
        rag_context = await self.rag.retrieve_relevant_context(user_message)

        # 4. Construct enriched system prompt
        system_prompt = (
            f"{self.SYSTEM_PROMPT_BASE}\n\n"
            f"EVIDENCIA CLINICA DE RESPALDO:\n{rag_context}\n\n"
            "Responde de forma concisa y orientada a la accion."
        )

        # 5. Build conversation history
        history_res = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(6)
        )
        past_msgs = list(reversed(history_res.scalars().all()))
        formatted_history = [
            {"role": m.role if m.role in ["user", "assistant"] else "user", "content": m.content}
            for m in past_msgs
        ]

        # 6. Generate AI response
        ai_response = await self.llm.generate_conversational_response(
            system_prompt=system_prompt,
            conversation_history=formatted_history,
        )

        # 7. Persist assistant response
        msg_assistant = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=ai_response,
            context_snapshot={"rag_used": bool(rag_context)},
        )
        db.add(msg_assistant)

        session_res = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session = session_res.scalar_one()
        session.last_message_at = datetime.utcnow()

        await db.commit()
        return ai_response
