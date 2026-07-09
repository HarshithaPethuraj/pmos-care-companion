import re

RED_FLAG_PATTERNS = [
    r"\bsevere (pain|bleeding)\b",
    r"\bheavy bleeding\b",
    r"\bfainting\b",
    r"\bcan'?t stop bleeding\b",
]

ESCALATION_MESSAGE = (
    "What you're describing could need urgent medical attention. Please contact "
    "a doctor or visit the nearest emergency department now rather than waiting "
    "on this chat. I can help you find a nearby gynecologist if that's useful."
)


def check_red_flags(query: str) -> str | None:
    q = query.lower()
    if any(re.search(p, q) for p in RED_FLAG_PATTERNS):
        return ESCALATION_MESSAGE
    return None
