"""Pure presentation rules shared by the chat UI and its tests."""

from __future__ import annotations

from ui.api_client import ChatResult

WELCOME = (
    "Hi! I am an AI study assistant for fees, offices and the student handbook. "
    "For best results, ask in English. Try an example or type a question below. "
    "Check important decisions with the Training Office."
)
EXAMPLES = [
    "Can I register my thesis with 118 credits?",
    "Tuition for 18 credits and 2 retake",
    "Where is the library?",
    "I lost my student card",
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


def status_note(result: ChatResult) -> str | None:
    if result.escalate:
        return (
            "I could not find this in the official documents. " "A staff member can help: Training Office, room I.101."
        )
    if result.degraded:
        return "Shown directly from the source document (the AI helper was unavailable)."
    return None
