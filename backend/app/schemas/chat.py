from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=10000)

    @validator("message")
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatResponse(BaseModel):
    decision: str
    risk_score: int
    reason_codes: List[str]
    response: Optional[str] = None
    explanation: Optional[str] = None
    request_log_id: Optional[int] = None
