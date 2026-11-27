"""UI logic without Streamlit, so it can be unit-tested."""

from __future__ import annotations

from ui.api_client import ChatResult

WELCOME = (
    "Hi! I am an AI study assistant for fees, offices and the student handbook. "
    "Try an example or ask a question below. Check important decisions with the Training Office."
)
EXAMPLES = [
    "Can I register my thesis with 118 credits?",
    "Tuition for 18 credits and 2 retake",
    "Where is the library?",
    "I lost my student card",
]

_CATEGORY_PREFIXES = {
    "H26#": "Student Handbook",
    "S26#": "Campus Services",
    "F26#": "Tuition & Fees",
}


def validate_input(text: str) -> str | None:
    """Return an error message for bad input, or None if it is fine."""
    t = text.strip()
    if not t:
        return "Please type a question."
    if len(t) > 2000:
        return "Your question is too long (max 2000 characters)."
    return None


def format_sources(sources: list[dict]) -> str:
    """Return formatted source citations or '' if none."""
    if not sources:
        return ""
    return "Sources: " + "; ".join(f"{s['id']} — {s['title']}" for s in sources)


def source_items(sources: list[dict]) -> list[dict[str, str]]:
    """Normalize source entries with category labels for structured UI display."""
    items: list[dict[str, str]] = []
    for source in sources:
        sid = str(source.get("id", "")).strip()
        title = str(source.get("title", "")).strip()
        category = "Official Document"
        for prefix, label in _CATEGORY_PREFIXES.items():
            if sid.startswith(prefix):
                category = label
                break
        items.append({"id": sid, "title": title, "category": category})
    return items


def status_note(result: ChatResult) -> str | None:
    """Return a short note shown under the answer for escalation or degraded mode."""
    if result.escalate:
        return "I could not find this in the official documents. A staff member can help: Training Office, room I.101."
    if result.degraded:
        return "Shown directly from the source document (the AI helper was unavailable)."
    return None
