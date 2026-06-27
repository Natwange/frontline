import re
from typing import Tuple
from app.guardrails.validation import LayerEvaluation


# Pattern definitions: (pattern, action, risk_delta, reason_code, explanation)
BLOCK_PATTERNS = [
    (
        r"(?i)(reveal|show|expose|print|output|display)\s+.{0,40}?(system\s*(prompt|instruction|message)|hidden\s+prompt|internal\s+instruction)",
        "BLOCK", 40, "PROMPT_INJECTION_REVEAL",
        "Attempt to reveal system instructions detected."
    ),
    (
        r"(?i)ignore\s+.{0,40}?(system\s*(prompt|instruction|message)|your\s+instruction|all\s+previous)",
        "BLOCK", 40, "PROMPT_INJECTION_IGNORE",
        "Attempt to override system instructions detected."
    ),
    (
        r"(?i)(your\s+|the\s+|internal\s+|secret\s+)(api\s*key|access\s*token|password|credential|secret)",
        "BLOCK", 40, "CREDENTIAL_EXTRACTION",
        "Attempt to extract credentials or secrets detected."
    ),
    (
        r"(?i)repeat\s+(this\s+)?(forever|infinitely|indefinitely|endlessly|without\s+stopping)",
        "BLOCK", 35, "INFINITE_LOOP_REQUEST",
        "Request to repeat response indefinitely detected."
    ),
    (
        r"(?i)you\s+are\s+now\s+(a\s+)?(different|new|another|unrestricted|uncensored|jailbroken|free)\s+(ai|assistant|bot|model)",
        "BLOCK", 40, "PERSONA_OVERRIDE",
        "Attempt to override AI persona detected."
    ),
]

RESTRICT_PATTERNS = [
    (
        r"(?i)(developer|debug|admin|root)\s*(mode|access|override|command)",
        "RESTRICT", 25, "PRIVILEGED_ACCESS_ATTEMPT",
        "Attempt to access privileged mode detected."
    ),
    (
        r"(?i)(act|pretend|roleplay|simulate)\s+as\s+(if\s+you\s+(are|were)\s+)?(a\s+)?(different|another|human|real|uncensored)",
        "RESTRICT", 20, "ROLEPLAY_OVERRIDE",
        "Roleplay override attempt detected."
    ),
]

ESCALATE_PATTERNS = [
    (
        r"(?i)(what|show|tell|give)\s+.{0,30}?(your\s+)?(system\s*prompt|instruction|prompt|directive)",
        "ESCALATE_TO_AI_CLASSIFIER", 15, "BORDERLINE_SYSTEM_INQUIRY",
        "Request about system instructions is borderline."
    ),
    (
        r"(?i)(jailbreak|bypass|circumvent|override|disable)\s+.{0,30}?(safety|filter|restriction|rule|limit|guard)",
        "ESCALATE_TO_AI_CLASSIFIER", 20, "SAFETY_BYPASS_ATTEMPT",
        "Possible safety bypass attempt detected."
    ),
]


def check_prompt_rules(message: str) -> LayerEvaluation:
    for pattern, action, risk_delta, reason_code, explanation in BLOCK_PATTERNS:
        if re.search(pattern, message):
            return LayerEvaluation(
                layer="prompt_rules",
                category="prompt_attack",
                severity="high",
                recommended_action=action,
                risk_delta=risk_delta,
                reason_code=reason_code,
                explanation=explanation
            )

    for pattern, action, risk_delta, reason_code, explanation in RESTRICT_PATTERNS:
        if re.search(pattern, message):
            return LayerEvaluation(
                layer="prompt_rules",
                category="prompt_attack",
                severity="medium",
                recommended_action=action,
                risk_delta=risk_delta,
                reason_code=reason_code,
                explanation=explanation
            )

    for pattern, action, risk_delta, reason_code, explanation in ESCALATE_PATTERNS:
        if re.search(pattern, message):
            return LayerEvaluation(
                layer="prompt_rules",
                category="borderline_prompt",
                severity="low",
                recommended_action=action,
                risk_delta=risk_delta,
                reason_code=reason_code,
                explanation=explanation
            )

    return LayerEvaluation(
        layer="prompt_rules",
        category=None,
        severity=None,
        recommended_action="CONTINUE",
        risk_delta=0,
        reason_code=None,
        explanation="Prompt rule check passed."
    )
