"""Responder protocol and offline implementations (Template & Stub)."""

from typing import Protocol, runtime_checkable

from assistant_core.errors import ProviderError
from assistant_core.models import Rule


@runtime_checkable
class Responder(Protocol):
    """Protocol for rule explanation responders."""

    def explain(self, question: str, rule: Rule) -> str:
        """Generate an explanation response for a given question and rule."""
        ...


class TemplateResponder:
    """Deterministic offline responder using template formatting."""

    def explain(self, question: str, rule: Rule) -> str:
        """Format an explanation using the rule title and text."""
        return f"{rule.title}: {rule.text}"


class StubLLMResponder:
    """Offline stub responder that simulates LLM response or controlled failure."""

    def __init__(self, fail: bool = False):
        self.fail = fail

    def explain(self, question: str, rule: Rule) -> str:
        """Return a stub explanation or raise ProviderError if fail flag is enabled."""
        if self.fail:
            raise ProviderError("stub provider unavailable")
        return f"Based on '{rule.title}': {rule.text}"
