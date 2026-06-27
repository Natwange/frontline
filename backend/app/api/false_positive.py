from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.false_positive_report import FalsePositiveReport
from app.schemas.false_positive import FalsePositiveCreate, FalsePositiveResponse

router = APIRouter()


@router.post("/false-positive-reports", response_model=FalsePositiveResponse)
def create_report(body: FalsePositiveCreate, db: Session = Depends(get_db)):
    report = FalsePositiveReport(
        request_log_id=body.request_log_id,
        reason=body.reason,
        status="open"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
