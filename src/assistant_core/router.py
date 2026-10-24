"""Intent routing logic for incoming user messages."""

from assistant_core.models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})


def route(text: str, office_names: set[str]) -> Intent:
    """Determine the intent of a user message.

    Evaluation precedence:
    1. Greetings
    2. Fee / tuition inquiries
    3. Office directory inquiries
    4. Academic handbook rule inquiries
    """
    t = text.lower().strip().rstrip("?!.")
    if t in GREETINGS:
        return Intent.GREETING
    if "fee" in t or "tuition" in t:
        return Intent.FEE
    if any(name in t for name in office_names):
        return Intent.OFFICE
    return Intent.RULE
