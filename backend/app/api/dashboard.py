from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from app.database import get_db
from app.models.request_log import RequestLog
from app.schemas.dashboard import DashboardMetrics, RequestLogEntry, AttackCategoryStats, RiskDistribution

router = APIRouter()


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
def get_metrics(db: Session = Depends(get_db)):
    total = db.query(func.count(RequestLog.id)).scalar() or 0

    action_counts = (
        db.query(RequestLog.final_action, func.count(RequestLog.id))
        .group_by(RequestLog.final_action)
        .all()
    )
    action_map = {row[0]: row[1] for row in action_counts}

    allowed = action_map.get("ALLOW", 0)
    blocked = action_map.get("BLOCK", 0)
    throttled = action_map.get("THROTTLE", 0)
    restricted = action_map.get("RESTRICT", 0)
    logged = action_map.get("LOG_ONLY", 0)

    cost_saved = db.query(func.sum(RequestLog.estimated_cost_saved_usd)).scalar() or 0.0
    ai_used = db.query(func.count(RequestLog.id)).filter(RequestLog.ai_classifier_used == True).scalar() or 0
    avg_risk = db.query(func.avg(RequestLog.risk_score)).scalar() or 0.0

    return DashboardMetrics(
        total_requests=total,
        allowed_requests=allowed,
        blocked_requests=blocked,
        throttled_requests=throttled,
        restricted_requests=restricted,
        logged_requests=logged,
        estimated_cost_saved_usd=round(float(cost_saved), 6),
        ai_classifier_usage_rate=round(ai_used / total, 3) if total > 0 else 0.0,
        average_risk_score=round(float(avg_risk), 1),
    )


@router.get("/dashboard/logs", response_model=List[RequestLogEntry])
def get_logs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    action: str = Query(default=None),
    db: Session = Depends(get_db)
):
    q = db.query(RequestLog).order_by(desc(RequestLog.created_at))
    if action:
        q = q.filter(RequestLog.final_action == action.upper())
    logs = q.offset(offset).limit(limit).all()
    return logs


@router.get("/dashboard/attack-categories", response_model=List[AttackCategoryStats])
def get_attack_categories(db: Session = Depends(get_db)):
    from app.models.layer_result import LayerResult
    results = (
        db.query(LayerResult.category, func.count(LayerResult.id))
        .filter(LayerResult.category.isnot(None))
        .group_by(LayerResult.category)
        .order_by(desc(func.count(LayerResult.id)))
        .limit(10)
        .all()
    )
    return [AttackCategoryStats(category=row[0], count=row[1]) for row in results]


@router.get("/dashboard/risk-distribution", response_model=List[RiskDistribution])
def get_risk_distribution(db: Session = Depends(get_db)):
    ranges = [
        ("0-20", 0, 20),
        ("21-40", 21, 40),
        ("41-60", 41, 60),
        ("61-80", 61, 80),
        ("81-100", 81, 100),
    ]
    result = []
    for label, low, high in ranges:
        count = db.query(func.count(RequestLog.id)).filter(
            RequestLog.risk_score >= low,
            RequestLog.risk_score <= high
        ).scalar() or 0
        result.append(RiskDistribution(range=label, count=count))
    return result
