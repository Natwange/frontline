from dataclasses import dataclass
from typing import Optional


@dataclass
class LayerEvaluation:
    layer: str
    category: Optional[str]
    severity: Optional[str]
    recommended_action: str
    risk_delta: int
    reason_code: Optional[str]
    explanation: str


def validate_request(session_id: str, message: str, message_length: int) -> LayerEvaluation:
    if not session_id or not session_id.strip():
        return LayerEvaluation(
            layer="validation",
            category="invalid_request",
            severity="critical",
            recommended_action="BLOCK",
            risk_delta=100,
            reason_code="MISSING_SESSION_ID",
            explanation="Session ID is missing or empty."
        )

    if not message or not message.strip():
        return LayerEvaluation(
            layer="validation",
            category="invalid_request",
            severity="critical",
            recommended_action="BLOCK",
            risk_delta=100,
            reason_code="EMPTY_MESSAGE",
            explanation="Message is empty."
        )

    if message_length > 10000:
        return LayerEvaluation(
            layer="validation",
            category="invalid_request",
            severity="high",
            recommended_action="BLOCK",
            risk_delta=50,
            reason_code="MESSAGE_TOO_LONG",
            explanation="Message exceeds maximum allowed length of 10,000 characters."
        )

    return LayerEvaluation(
        layer="validation",
        category=None,
        severity=None,
        recommended_action="CONTINUE",
        risk_delta=0,
        reason_code=None,
        explanation="Request validation passed."
    )
