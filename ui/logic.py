"""UI presentation and validation logic without Streamlit dependencies."""

from __future__ import annotations

from ui.api_client import ChatResult

WELCOME = (
    "Hi! I am an AI study assistant for fees, offices, and the student handbook. "
    "Try: “Can I register my thesis with 118 credits?” "
    "Check important decisions with the Training Office."
)
EXAMPLES = [
    "Can I register my thesis with 118 credits?",
    "Tuition for 18 credits and 2 retake",
    "Where is the library?",
    "I lost my student card",
]


def validate_input(text: str) -> str | None:
    """Return an error message for invalid user input, or None when valid."""
    t = text.strip()
    if not t:
        return "Please type a question."
    if len(t) > 2000:
        return "Your question is too long (max 2000 characters)."
    return None


def format_sources(sources: list[dict]) -> str:
    """Format document citations as 'Sources: <id> — <title>; ...', or '' when empty."""
    if not sources:
        return ""
    return "Sources: " + "; ".join(f"{s['id']} — {s['title']}" for s in sources)


def status_note(result: ChatResult) -> str | None:
    """Return an explanation banner under an answer, prioritizing escalation over degraded fallback."""
    if result.escalate:
        return (
            "I could not find this in the official documents. " "A staff member can help: Training Office, room I.101."
        )
    if result.degraded:
        return "Shown directly from the source document (the AI helper was unavailable)."
    return None
