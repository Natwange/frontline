from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class FalsePositiveReport(Base):
    __tablename__ = "false_positive_reports"

    id = Column(Integer, primary_key=True, index=True)
    request_log_id = Column(Integer, ForeignKey("request_logs.id"), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    status = Column(String(50), default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
