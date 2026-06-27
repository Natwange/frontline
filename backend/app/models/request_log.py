from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    ip_hash = Column(String(64), nullable=True)
    raw_message = Column(Text, nullable=True)
    redacted_message = Column(Text, nullable=True)
    message_hash = Column(String(64), nullable=True)
    message_length = Column(Integer, nullable=True)
    contains_pii = Column(Boolean, default=False)
    risk_score = Column(Integer, default=0)
    final_action = Column(String(50), nullable=False)
    reason_codes = Column(JSON, default=list)
    ai_classifier_used = Column(Boolean, default=False)
    ai_classifier_label = Column(String(100), nullable=True)
    ai_classifier_confidence = Column(Float, nullable=True)
    ai_classifier_explanation = Column(Text, nullable=True)
    input_tokens_estimated = Column(Integer, nullable=True)
    output_tokens_estimated = Column(Integer, nullable=True)
    estimated_cost_usd = Column(Float, nullable=True)
    actual_cost_usd = Column(Float, nullable=True)
    estimated_cost_saved_usd = Column(Float, nullable=True)
    ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
