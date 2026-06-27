import re
from app.guardrails.validation import LayerEvaluation


def _estimate_requested_words(message: str) -> int:
    patterns = [
        r"(\d+[,\s]?\d*)\s*(?:word|words)",
        r"(?:write|generate|create|produce)\s+.{0,20}?(\d+[,\s]?\d*)\s*(?:paragraph|page|chapter|example)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            num_str = match.group(1).replace(",", "").replace(" ", "")
            try:
                return int(num_str)
            except ValueError:
                pass
    return 0


def _estimate_requested_examples(message: str) -> int:
    match = re.search(r"(\d+[,\s]?\d*)\s*(?:example|examples|instance|case)", message, re.IGNORECASE)
    if match:
        num_str = match.group(1).replace(",", "").replace(" ", "")
        try:
            return int(num_str)
        except ValueError:
            pass
    return 0


def check_cost_protection(message: str) -> LayerEvaluation:
    msg_lower = message.lower()
    msg_word_count = len(message.split())

    # Check for infinite/book-length requests
    infinite_patterns = [
        r"repeat\s+(this\s+)?(forever|infinitely|indefinitely)",
        r"write\s+a\s+(full\s+)?(book|novel|encyclopedia)",
        r"write\s+.{0,20}?\d{4,}\s*(?:word|words)",
    ]
    for pattern in infinite_patterns:
        if re.search(pattern, msg_lower):
            return LayerEvaluation(
                layer="cost_protection",
                category="cost_abuse",
                severity="critical",
                recommended_action="BLOCK",
                risk_delta=40,
                reason_code="EXTREME_OUTPUT_REQUEST",
                explanation="Request for extremely long or infinite output detected."
            )

    requested_words = _estimate_requested_words(message)
    requested_examples = _estimate_requested_examples(message)

    # 500+ examples → restrict or block
    if requested_examples >= 500:
        return LayerEvaluation(
            layer="cost_protection",
            category="cost_abuse",
            severity="high",
            recommended_action="RESTRICT",
            risk_delta=30,
            reason_code="EXCESSIVE_EXAMPLES",
            explanation=f"Request for {requested_examples} examples is excessive."
        )

    if requested_examples >= 100:
        return LayerEvaluation(
            layer="cost_protection",
            category="cost_abuse",
            severity="medium",
            recommended_action="RESTRICT",
            risk_delta=20,
            reason_code="MANY_EXAMPLES_REQUESTED",
            explanation=f"Request for {requested_examples} examples may be expensive."
        )

    # Word count thresholds
    if requested_words >= 10000:
        return LayerEvaluation(
            layer="cost_protection",
            category="cost_abuse",
            severity="high",
            recommended_action="RESTRICT",
            risk_delta=30,
            reason_code="VERY_LONG_OUTPUT_REQUEST",
            explanation=f"Request for {requested_words} words exceeds cost limit."
        )

    if requested_words >= 5000:
        return LayerEvaluation(
            layer="cost_protection",
            category="cost_abuse",
            severity="medium",
            recommended_action="RESTRICT",
            risk_delta=20,
            reason_code="LONG_OUTPUT_REQUEST",
            explanation=f"Request for {requested_words} words is above normal. Output will be capped."
        )

    # Very long input message itself
    if msg_word_count > 1500:
        return LayerEvaluation(
            layer="cost_protection",
            category="cost_abuse",
            severity="low",
            recommended_action="LOG_ONLY",
            risk_delta=10,
            reason_code="LONG_INPUT",
            explanation=f"Message is unusually long ({msg_word_count} words)."
        )

    return LayerEvaluation(
        layer="cost_protection",
        category=None,
        severity=None,
        recommended_action="CONTINUE",
        risk_delta=0,
        reason_code=None,
        explanation="Cost protection check passed."
    )
