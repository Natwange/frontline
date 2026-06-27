import re
import hashlib


EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.IGNORECASE)
API_KEY_PATTERN = re.compile(r"\b(sk|pk|api|token|key)[-_]?[a-zA-Z0-9]{16,}\b", re.IGNORECASE)
TOKEN_PATTERN = re.compile(r"\b(Bearer\s+|Token\s+)[a-zA-Z0-9._\-]{10,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
SECRET_PATTERN = re.compile(r"\b(password|passwd|pwd|secret|credential|token|access_token)\s*[:=]\s*\S+", re.IGNORECASE)


def redact_message(message: str) -> tuple:
    redacted = message
    contains_pii = False

    if EMAIL_PATTERN.search(redacted):
        redacted = EMAIL_PATTERN.sub("[EMAIL]", redacted)
        contains_pii = True

    if API_KEY_PATTERN.search(redacted):
        redacted = API_KEY_PATTERN.sub("[SECRET]", redacted)
        contains_pii = True

    if TOKEN_PATTERN.search(redacted):
        redacted = TOKEN_PATTERN.sub("[TOKEN]", redacted)
        contains_pii = True

    if PHONE_PATTERN.search(redacted):
        redacted = PHONE_PATTERN.sub("[PHONE]", redacted)
        contains_pii = True

    if SECRET_PATTERN.search(redacted):
        redacted = SECRET_PATTERN.sub(lambda m: m.group().split(m.group().split()[-1])[0] + "[REDACTED]", redacted)
        contains_pii = True

    return redacted, contains_pii


def hash_message(message: str) -> str:
    return hashlib.sha256(message.strip().lower().encode()).hexdigest()


def hash_ip(ip: str) -> str:
    if not ip:
        return "unknown"
    return hashlib.sha256(ip.encode()).hexdigest()[:16]
