"""Responder protocol and offline implementations (Template & Stub)."""

from typing import Protocol

from assistant_core.errors import ProviderError
from assistant_core.models import Rule


class Responder(Protocol):
    """Protocol for rule explanation responders."""

    def explain(self, question: str, rule: Rule) -> str:
        """Generate an explanation response for a given question and rule."""
        ...


class TemplateResponder:
    """Deterministic offline responder using template formatting."""

    def explain(self, question: str, rule: Rule) -> str:
        return f"{rule.title}: {rule.text}"


class StubLLMResponder:
    """Offline stub responder that can simulate provider failure for testing."""

    def __init__(self, fail: bool = False):
        self.fail = fail

    def explain(self, question: str, rule: Rule) -> str:
        if self.fail:
            raise ProviderError("stub provider unavailable")
        return f"Based on '{rule.title}': {rule.text}"
