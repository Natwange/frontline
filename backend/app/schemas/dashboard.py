from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class DashboardMetrics(BaseModel):
    total_requests: int
    allowed_requests: int
    blocked_requests: int
    throttled_requests: int
    restricted_requests: int
    logged_requests: int
    estimated_cost_saved_usd: float
    ai_classifier_usage_rate: float
    average_risk_score: float


class RequestLogEntry(BaseModel):
    id: int
    session_id: str
    redacted_message: Optional[str]
    risk_score: int
    final_action: str
    reason_codes: Optional[List[str]]
    ai_classifier_used: bool
    ai_classifier_label: Optional[str]
    estimated_cost_saved_usd: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class AttackCategoryStats(BaseModel):
    category: str
    count: int


class RiskDistribution(BaseModel):
    range: str
    count: int
