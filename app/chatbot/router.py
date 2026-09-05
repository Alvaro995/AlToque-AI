from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.chatbot.schemas import (
    ChatRequest,
    ChatResponse
)

from app.chatbot.service import ChatbotService



router = APIRouter(

    prefix="/api/v1/chat",

    tags=["Chatbot"]

)



@router.post(
    "",
    response_model=ChatResponse
)
def chat(
    data: ChatRequest,
    db: Session = Depends(get_db)
):

    return ChatbotService.generate_response(
        db=db,
        user_id=data.user_id,
        message=data.message
    )