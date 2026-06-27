import hashlib
import json
from typing import Optional
from app.guardrails.validation import LayerEvaluation
from app.redis_client import get_redis


def _hash_message(message: str) -> str:
    return hashlib.sha256(message.strip().lower().encode()).hexdigest()[:16]


def check_behavior(session_id: str, message: str) -> LayerEvaluation:
    redis = get_redis()

    if redis is None:
        return LayerEvaluation(
            layer="behavior",
            category=None,
            severity=None,
            recommended_action="CONTINUE",
            risk_delta=0,
            reason_code=None,
            explanation="Behavior analysis skipped (Redis unavailable)."
        )

    msg_hash = _hash_message(message)
    repeat_key = f"repeated_count:session:{session_id}:{msg_hash}"
    recent_key = f"recent_messages:session:{session_id}"

    pipe = redis.pipeline()
    pipe.incr(repeat_key)
    pipe.expire(repeat_key, 600)
    pipe.lpush(recent_key, msg_hash)
    pipe.ltrim(recent_key, 0, 19)
    pipe.expire(recent_key, 600)
    results = pipe.execute()

    repeat_count = results[0]

    # 8+ same message → temp block
    if repeat_count >= 8:
        redis.setex(f"blocked:session:{session_id}", 300, "1")
        return LayerEvaluation(
            layer="behavior",
            category="repeated_message_attack",
            severity="critical",
            recommended_action="BLOCK",
            risk_delta=40,
            reason_code="EXCESSIVE_REPETITION",
            explanation=f"Same message sent {repeat_count} times. Session temporarily blocked."
        )

    # 5–7 same message → throttle
    if repeat_count >= 5:
        return LayerEvaluation(
            layer="behavior",
            category="repeated_message_pattern",
            severity="high",
            recommended_action="THROTTLE",
            risk_delta=25,
            reason_code="REPEATED_MESSAGE",
            explanation=f"Same message sent {repeat_count} times."
        )

    # 3–4 same message → log
    if repeat_count >= 3:
        return LayerEvaluation(
            layer="behavior",
            category="repeated_message_pattern",
            severity="low",
            recommended_action="LOG_ONLY",
            risk_delta=10,
            reason_code="REPEATED_MESSAGE",
            explanation=f"Same message sent {repeat_count} times."
        )

    return LayerEvaluation(
        layer="behavior",
        category=None,
        severity=None,
        recommended_action="CONTINUE",
        risk_delta=0,
        reason_code=None,
        explanation="Behavior analysis passed."
    )
