"""UI logic without Streamlit, so it can be unit-tested."""

from __future__ import annotations

from ui.api_client import ChatResult

WELCOME = (
    "Hi! I can answer questions in English about fees, offices and the student handbook. "
    "Try: “Can I register my thesis with 118 credits?”"
)
EXAMPLES = [
    "Can I register my thesis with 118 credits?",
    "Tuition for 18 credits and 2 retakes",
    "Where is the library?",
    "I lost my student card",
]


def validate_input(text: str) -> str | None:
    """Return an error message for bad input, or None if it is fine."""
    t = text.strip()
    if not t:
        return "Please type a question."
    if len(t) > 2000:
        return "Your question is too long (max 2000 characters)."
    return None


def format_sources(sources: list[dict]) -> str:
    """'Sources: H26#5.3 — 5.3 Thesis registration' or '' if none."""
    if not sources:
        return ""
    return "Sources: " + "; ".join(f"{s['id']} — {s['title']}" for s in sources)


def status_note(result: ChatResult) -> str | None:
    """A short note shown under the answer, explaining special situations."""
    if result.escalate:
        return "I could not find this in the official documents. A staff member can help: Training Office, room I.101."
    if result.degraded:
        return "Shown directly from the source document (the AI helper was unavailable)."
    return None


def looks_non_english(text: str) -> bool:
    """Return True when the input contains non-ASCII characters (e.g., Vietnamese)."""
    return any(ord(ch) > 127 for ch in text)


def build_status_note(result: ChatResult, question: str = "") -> str | None:
    """Build the UI note without repeating escalation already present in the answer."""
    english_hint = "Official documents are currently indexed in English only — try rephrasing your question in English."
    if result.escalate and "Training Office" in result.answer:
        return f"Note: {english_hint}" if looks_non_english(question) else None
    note = status_note(result)
    if result.escalate and note and looks_non_english(question):
        return f"{note} Note: {english_hint}"
    return note
