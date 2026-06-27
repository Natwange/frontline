from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FalsePositiveCreate(BaseModel):
    request_log_id: int
    reason: str = Field(..., min_length=1, max_length=2000)


class FalsePositiveResponse(BaseModel):
    id: int
    request_log_id: int
    reason: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
