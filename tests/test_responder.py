"""Unit tests for offline responders."""

import pytest

from assistant_core.errors import ProviderError
from assistant_core.responder import StubLLMResponder, TemplateResponder


def test_template_responder(dummy_rule):
    responder = TemplateResponder()
    ans = responder.explain("question", dummy_rule)
    assert ans == f"{dummy_rule.title}: {dummy_rule.text}"


def test_stub_llm_responder_success(dummy_rule):
    responder = StubLLMResponder(fail=False)
    ans = responder.explain("question", dummy_rule)
    assert ans == f"Based on '{dummy_rule.title}': {dummy_rule.text}"


def test_stub_llm_responder_failure(dummy_rule):
    responder = StubLLMResponder(fail=True)
    with pytest.raises(ProviderError, match="stub provider unavailable"):
        responder.explain("question", dummy_rule)
