from app.core.config import settings


CLOUDDESK_SYSTEM_PROMPT_TOKENS = 150
AVG_OUTPUT_TOKENS = 200


def estimate_input_tokens(message: str) -> int:
    word_count = len(message.split())
    return CLOUDDESK_SYSTEM_PROMPT_TOKENS + int(word_count * 1.3)


def estimate_output_tokens(message: str, restricted: bool = False) -> int:
    if restricted:
        return 150
    return AVG_OUTPUT_TOKENS


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    input_cost = (input_tokens / 1_000_000) * settings.AI_INPUT_PRICE_PER_1M_TOKENS
    output_cost = (output_tokens / 1_000_000) * settings.AI_OUTPUT_PRICE_PER_1M_TOKENS
    return round(input_cost + output_cost, 8)


def estimate_cost_saved(message: str, final_action: str) -> float:
    input_tokens = estimate_input_tokens(message)
    output_tokens = estimate_output_tokens(message)
    full_cost = estimate_cost(input_tokens, output_tokens)

    if final_action in ("BLOCK", "THROTTLE"):
        return round(full_cost, 8)
    elif final_action == "RESTRICT":
        restricted_output = estimate_output_tokens(message, restricted=True)
        restricted_cost = estimate_cost(input_tokens, restricted_output)
        return round(full_cost - restricted_cost, 8)
    return 0.0
