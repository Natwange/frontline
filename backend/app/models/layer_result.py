from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class LayerResult(Base):
    __tablename__ = "layer_results"

    id = Column(Integer, primary_key=True, index=True)
    request_log_id = Column(Integer, ForeignKey("request_logs.id"), nullable=False, index=True)
    layer_name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    severity = Column(String(50), nullable=True)
    recommended_action = Column(String(50), nullable=False)
    risk_delta = Column(Integer, default=0)
    reason_code = Column(String(100), nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
