from typing import List
from app.guardrails.validation import LayerEvaluation

ACTION_STRENGTH = {
    "CONTINUE": 0,
    "LOG_ONLY": 1,
    "RESTRICT": 2,
    "THROTTLE": 3,
    "BLOCK": 4,
    "ESCALATE_TO_AI_CLASSIFIER": 1,
}

EARLY_STOP_ACTIONS = {"BLOCK", "THROTTLE"}


def combine_evaluations(evaluations: List[LayerEvaluation]) -> dict:
    max_action = "CONTINUE"
    max_strength = 0
    total_risk = 0
    reason_codes = []
    needs_ai_classifier = False

    for ev in evaluations:
        total_risk += ev.risk_delta
        if ev.reason_code:
            reason_codes.append(ev.reason_code)

        if ev.recommended_action == "ESCALATE_TO_AI_CLASSIFIER":
            needs_ai_classifier = True
            continue

        strength = ACTION_STRENGTH.get(ev.recommended_action, 0)
        if strength > max_strength:
            max_strength = strength
            max_action = ev.recommended_action

    risk_score = min(total_risk, 100)

    final_action = max_action
    if final_action == "CONTINUE" and risk_score >= 70:
        final_action = "RESTRICT"
    elif final_action == "CONTINUE" and risk_score >= 50:
        final_action = "LOG_ONLY"

    return {
        "final_action": final_action,
        "risk_score": risk_score,
        "reason_codes": reason_codes,
        "needs_ai_classifier": needs_ai_classifier and final_action not in EARLY_STOP_ACTIONS,
    }


def should_stop_early(action: str) -> bool:
    return action in EARLY_STOP_ACTIONS
