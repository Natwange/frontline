from pydantic import BaseModel, Field
from typing import Optional, List


class SimulatorRequest(BaseModel):
    scenario: str = Field(..., description="Scenario type")
    request_count: int = Field(default=10, ge=1, le=100)
    session_id: Optional[str] = None


class SimulatorResult(BaseModel):
    scenario: str
    total_sent: int
    results: List[dict]
    summary: dict
