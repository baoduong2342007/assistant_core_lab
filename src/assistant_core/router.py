"""Intent routing logic for incoming user messages."""

import re

from assistant_core.models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})


def is_tuition_deadline(text: str) -> bool:
    return bool(
        re.search(r"\btuition\b", text, re.IGNORECASE)
        and re.search(r"\b(?:due|deadlines?)\b|\bwhen\b[^?.!]*\bpay\b", text, re.IGNORECASE)
    )


def route(text: str, office_names: set[str], *, policy_search: bool = False) -> Intent:
    """Determine the intent of a user message.

    Evaluation precedence:
    1. Greetings
    2. Policy questions with tool or office keywords, when RAG is enabled
    3. Fee / tuition inquiries
    4. Office directory inquiries
    5. Academic handbook rule inquiries
    """
    t = text.lower().strip().rstrip("?!.")
    if t in GREETINGS:
        return Intent.GREETING
    if policy_search:
        if is_tuition_deadline(t):
            return Intent.RULE
        if "student card" in t and re.search(r"\b(?:fees?|cost|replacement)\b", t):
            return Intent.RULE
        if "library" in t and re.search(r"\b(?:borrow\w*|renew\w*|keep)\b", t):
            return Intent.RULE
    if "fee" in t or "tuition" in t:
        return Intent.FEE
    if any(name in t for name in office_names):
        return Intent.OFFICE
    return Intent.RULE
