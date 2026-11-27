"""Pure presentation rules shared by the chat UI and its tests."""

from __future__ import annotations

import re

from ui.api_client import ChatResult

WELCOME = (
    "Hi! I am an AI study assistant for fees, offices and the student handbook. "
    "For best results, ask in English. Try an example or type a question below. "
    "Check important decisions with the Training Office."
)
CHAT_PLACEHOLDER = "Ask in English about fees, offices or the handbook (avoid Vietnamese/shorthand)…"
EXAMPLES = [
    "Can I register my thesis with 118 credits?",
    "Tuition for 18 credits and 2 retake",
    "Where is the library?",
    "I lost my student card",
]

_SHORTHAND_OR_VIETNAMESE = re.compile(
    r"\b(?:kh|ko|dk|tui|dc|khong|lam|mat|khoa|luan|hoc|phi|thu|vien|bao|nhieu|dau|studnet)\b",
    re.IGNORECASE,
)

_SUGGESTION_RULES: list[tuple[tuple[str, ...], str]] = [
    (
        ("thesis", "credit", "credits", "khóa luận", "khoa luan", "luận văn", "đăng kí", "dang ki", "tín chỉ"),
        "Can I register my thesis with 118 credits?",
    ),
    (
        ("card", "studnet", "thẻ", "mất", "làm lại", "student id"),
        "I lost my student card",
    ),
    (
        ("tuition", "fee", "retake", "học phí", "hoc phi", "học lại"),
        "Tuition for 18 credits and 2 retake",
    ),
    (
        ("library", "thư viện", "thu vien"),
        "Where is the library?",
    ),
]


def validate_input(text: str) -> str | None:
    text = text.strip()
    if not text:
        return "Please type a question."
    if len(text) > 2000:
        return "Your question is too long (max 2000 characters)."
    return None


def format_sources(sources: list[dict]) -> str:
    if not sources:
        return ""
    return "Sources: " + "; ".join(f"{source['id']} — {source['title']}" for source in sources)


def has_mixed_or_shorthand(text: str) -> bool:
    """Detect non-ASCII Vietnamese characters or common Vietnamese/shorthand tokens."""
    if any(ord(ch) > 127 for ch in text):
        return True
    return bool(_SHORTHAND_OR_VIETNAMESE.search(text))


def suggest_english_queries(text: str) -> list[str]:
    """Return matching full-English example questions for mixed or shorthand input."""
    lowered = text.lower()
    suggestions: list[str] = []
    for keywords, example in _SUGGESTION_RULES:
        if any(kw in lowered for kw in keywords) and example not in suggestions:
            suggestions.append(example)
    return suggestions


def status_note(result: ChatResult) -> str | None:
    if result.escalate:
        return (
            "I could not find this in the official documents. " "A staff member can help: Training Office, room I.101."
        )
    if result.degraded:
        return "Shown directly from the source document (the AI helper was unavailable)."
    return None


def escalation_note(question: str, result: ChatResult) -> str | None:
    """Provide actionable English-rephrase guidance when a mixed/shorthand query escalates."""
    if result.escalate and has_mixed_or_shorthand(question):
        return (
            "Tip: Only full English keywords are indexed (mixed Vietnamese, abbreviations like 'kh', "
            "or typos may not match). Try a full English phrasing below, or contact Training Office, room I.101."
        )
    return status_note(result)
