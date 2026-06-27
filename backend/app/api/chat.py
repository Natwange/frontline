from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.pipeline import process_request

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    result = process_request(
        session_id=body.session_id,
        message=body.message,
        ip=ip,
        db=db
    )
    return ChatResponse(**result)
