import hashlib
import time
from typing import Optional
from app.guardrails.validation import LayerEvaluation
from app.redis_client import get_redis


def _hash_ip(ip: Optional[str]) -> str:
    if not ip:
        return "unknown"
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def check_rate_limit(session_id: str, ip: Optional[str] = None) -> LayerEvaluation:
    redis = get_redis()

    if redis is None:
        return LayerEvaluation(
            layer="rate_limit",
            category=None,
            severity=None,
            recommended_action="CONTINUE",
            risk_delta=0,
            reason_code=None,
            explanation="Rate limiting skipped (Redis unavailable)."
        )

    ip_hash = _hash_ip(ip)
    session_key_60s = f"rate:session:{session_id}:60s"
    session_key_10s = f"burst:session:{session_id}:10s"
    ip_key_60s = f"rate:ip:{ip_hash}:60s"

    pipe = redis.pipeline()
    pipe.incr(session_key_60s)
    pipe.expire(session_key_60s, 60)
    pipe.incr(session_key_10s)
    pipe.expire(session_key_10s, 10)
    pipe.incr(ip_key_60s)
    pipe.expire(ip_key_60s, 60)
    results = pipe.execute()

    session_count_60s = results[0]
    burst_count_10s = results[2]
    ip_count_60s = results[4]

    # Check temporary block
    blocked_key = f"blocked:session:{session_id}"
    if redis.exists(blocked_key):
        ttl = redis.ttl(blocked_key)
        return LayerEvaluation(
            layer="rate_limit",
            category="bot_rate_abuse",
            severity="critical",
            recommended_action="BLOCK",
            risk_delta=50,
            reason_code="TEMPORARILY_BLOCKED",
            explanation=f"Session is temporarily blocked. Try again in {ttl} seconds."
        )

    # Burst detection: 6+ in 10 seconds
    if burst_count_10s >= 6:
        return LayerEvaluation(
            layer="rate_limit",
            category="bot_rate_abuse",
            severity="high",
            recommended_action="THROTTLE",
            risk_delta=35,
            reason_code="BURST_DETECTED",
            explanation=f"Burst rate detected: {burst_count_10s} requests in 10 seconds."
        )

    # 31+ per minute → temporary block
    if session_count_60s >= 31:
        redis.setex(f"blocked:session:{session_id}", 300, "1")
        return LayerEvaluation(
            layer="rate_limit",
            category="bot_rate_abuse",
            severity="critical",
            recommended_action="BLOCK",
            risk_delta=50,
            reason_code="HIGH_REQUEST_RATE",
            explanation=f"Session sent {session_count_60s} requests in 60 seconds. Temporarily blocked."
        )

    # 21–30 per minute → throttle
    if session_count_60s >= 21:
        return LayerEvaluation(
            layer="rate_limit",
            category="bot_rate_abuse",
            severity="medium",
            recommended_action="THROTTLE",
            risk_delta=35,
            reason_code="HIGH_REQUEST_RATE",
            explanation=f"Session sent {session_count_60s} requests in 60 seconds."
        )

    # 11–20 per minute → log
    if session_count_60s >= 11:
        return LayerEvaluation(
            layer="rate_limit",
            category="elevated_rate",
            severity="low",
            recommended_action="LOG_ONLY",
            risk_delta=10,
            reason_code="ELEVATED_REQUEST_RATE",
            explanation=f"Session sent {session_count_60s} requests in 60 seconds."
        )

    return LayerEvaluation(
        layer="rate_limit",
        category=None,
        severity=None,
        recommended_action="CONTINUE",
        risk_delta=0,
        reason_code=None,
        explanation="Rate limit check passed."
    )
