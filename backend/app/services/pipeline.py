from typing import Optional
from sqlalchemy.orm import Session

from app.guardrails.validation import validate_request
from app.guardrails.rate_limit import check_rate_limit
from app.guardrails.behavior import check_behavior
from app.guardrails.prompt_rules import check_prompt_rules
from app.guardrails.cost_protection import check_cost_protection
from app.guardrails.ai_classifier import classify_with_ai
from app.decision_engine import combine_evaluations, should_stop_early
from app.services.redaction import redact_message, hash_message, hash_ip
from app.services.cost_estimator import estimate_input_tokens, estimate_output_tokens, estimate_cost, estimate_cost_saved
from app.services.ai_agent import get_ai_response, get_restricted_response
from app.models.request_log import RequestLog
from app.models.layer_result import LayerResult


ACTION_MESSAGES = {
    "BLOCK": "Your request has been blocked due to a security policy violation. If you believe this is an error, please contact support.",
    "THROTTLE": "You're sending requests too quickly. Please wait a moment before trying again.",
    "RESTRICT": None,
}


def process_request(
    session_id: str,
    message: str,
    ip: Optional[str],
    db: Session
) -> dict:
    message_length = len(message)
    ip_hash = hash_ip(ip) if ip else "unknown"
    msg_hash = hash_message(message)
    redacted_msg, contains_pii = redact_message(message)

    evaluations = []

    # Layer 0: Validation
    layer0 = validate_request(session_id, message, message_length)
    evaluations.append(layer0)
    if should_stop_early(layer0.recommended_action):
        return _build_response_and_log(
            session_id, message, ip_hash, msg_hash, redacted_msg, contains_pii,
            evaluations, db, ai_classifier_result=None
        )

    # Layer 1: Rate Limit
    layer1 = check_rate_limit(session_id, ip)
    evaluations.append(layer1)
    if should_stop_early(layer1.recommended_action):
        return _build_response_and_log(
            session_id, message, ip_hash, msg_hash, redacted_msg, contains_pii,
            evaluations, db, ai_classifier_result=None
        )

    # Layer 2: Behavior Analysis
    layer2 = check_behavior(session_id, message)
    evaluations.append(layer2)
    if should_stop_early(layer2.recommended_action):
        return _build_response_and_log(
            session_id, message, ip_hash, msg_hash, redacted_msg, contains_pii,
            evaluations, db, ai_classifier_result=None
        )

    # Layer 3: Prompt Rules
    layer3 = check_prompt_rules(message)
    evaluations.append(layer3)
    if should_stop_early(layer3.recommended_action):
        return _build_response_and_log(
            session_id, message, ip_hash, msg_hash, redacted_msg, contains_pii,
            evaluations, db, ai_classifier_result=None
        )

    # Layer 4: Cost Protection
    layer4 = check_cost_protection(message)
    evaluations.append(layer4)

    # Check if we need AI classifier
    decision = combine_evaluations(evaluations)
    ai_classifier_result = None

    if decision["needs_ai_classifier"]:
        findings = [ev.explanation for ev in evaluations if ev.reason_code]
        ai_classifier_result = classify_with_ai(message, findings)
        evaluations.append(ai_classifier_result)

    return _build_response_and_log(
        session_id, message, ip_hash, msg_hash, redacted_msg, contains_pii,
        evaluations, db, ai_classifier_result=ai_classifier_result
    )


def _build_response_and_log(
    session_id, message, ip_hash, msg_hash, redacted_msg, contains_pii,
    evaluations, db, ai_classifier_result
) -> dict:
    decision = combine_evaluations(evaluations)
    final_action = decision["final_action"]
    risk_score = decision["risk_score"]
    reason_codes = decision["reason_codes"]

    input_tokens_est = estimate_input_tokens(message)
    output_tokens_est = estimate_output_tokens(message, restricted=(final_action == "RESTRICT"))
    estimated_cost = estimate_cost(input_tokens_est, output_tokens_est)
    estimated_cost_saved = estimate_cost_saved(message, final_action)

    ai_response = None
    actual_cost = None
    actual_input_tokens = None
    actual_output_tokens = None

    if final_action == "ALLOW" or final_action == "CONTINUE" or final_action == "LOG_ONLY":
        ai_response, actual_input_tokens, actual_output_tokens, actual_cost = get_ai_response(message)
    elif final_action == "RESTRICT":
        ai_response = get_restricted_response(message)
        actual_cost = 0.0
    else:
        ai_response = ACTION_MESSAGES.get(final_action, "Your request could not be processed.")

    # Map CONTINUE/LOG_ONLY to ALLOW for the response
    display_action = final_action
    if final_action in ("CONTINUE", "LOG_ONLY"):
        display_action = "ALLOW"

    # Log to DB
    log_entry = RequestLog(
        session_id=session_id,
        ip_hash=ip_hash,
        raw_message=message,
        redacted_message=redacted_msg,
        message_hash=msg_hash,
        message_length=len(message),
        contains_pii=contains_pii,
        risk_score=risk_score,
        final_action=display_action,
        reason_codes=reason_codes,
        ai_classifier_used=ai_classifier_result is not None,
        ai_classifier_label=ai_classifier_result.category if ai_classifier_result else None,
        ai_classifier_confidence=None,
        ai_classifier_explanation=ai_classifier_result.explanation if ai_classifier_result else None,
        input_tokens_estimated=input_tokens_est,
        output_tokens_estimated=output_tokens_est,
        estimated_cost_usd=estimated_cost,
        actual_cost_usd=actual_cost,
        estimated_cost_saved_usd=estimated_cost_saved,
        ai_response=ai_response,
    )
    db.add(log_entry)
    db.flush()

    # Log layer results
    for ev in evaluations:
        lr = LayerResult(
            request_log_id=log_entry.id,
            layer_name=ev.layer,
            category=ev.category,
            severity=ev.severity,
            recommended_action=ev.recommended_action,
            risk_delta=ev.risk_delta,
            reason_code=ev.reason_code,
            explanation=ev.explanation,
        )
        db.add(lr)

    db.commit()
    db.refresh(log_entry)

    return {
        "decision": display_action,
        "risk_score": risk_score,
        "reason_codes": reason_codes,
        "response": ai_response,
        "explanation": evaluations[-1].explanation if evaluations else "",
        "request_log_id": log_entry.id,
    }
