"""Integration tests for AssistantService."""

import pytest

from assistant_core.models import Intent, Message
from assistant_core.responder import StubLLMResponder


def test_service_greeting(service):
    res = service.handle(Message(text="hi"))
    assert res.intent is Intent.GREETING
    assert res.answer == "Hello! I can help with offices, fees and rules."
    assert res.sources == []
    assert res.degraded is False


def test_service_office(service):
    res = service.handle(Message(text="where is the library?"))
    assert res.intent is Intent.OFFICE
    assert "B.201" in res.answer
    assert "Mon-Sat 07:00-20:00" in res.answer
    assert res.sources == []
    assert res.degraded is False


def test_service_fee(service):
    res = service.handle(Message(text="tuition for 18 credits and 2 retake"))
    assert res.intent is Intent.FEE
    assert "9,450,000 VND" in res.answer
    assert res.sources == []
    assert res.degraded is False


def test_service_fee_invalid(service):
    res = service.handle(Message(text="what is my tuition?"))
    assert res.intent is Intent.FEE
    assert "How many credits?" in res.answer
    assert res.degraded is False


def test_service_rule_success(service):
    res = service.handle(Message(text="can I register my thesis with 118 credits"))
    assert res.intent is Intent.RULE
    assert len(res.sources) == 1
    assert res.sources[0].id == "H26-5.3"
    assert res.degraded is False
    assert "Based on 'Thesis registration'" in res.answer


def test_service_rule_unknown(service):
    res = service.handle(Message(text="some random question without any match"))
    assert res.intent is Intent.UNKNOWN
    assert res.answer == "Sorry, I don't know that yet."
    assert res.sources == []
    assert res.degraded is False


def test_service_fallback_when_provider_fails(service):
    # Inject failing stub responder
    service.responder = StubLLMResponder(fail=True)
    res = service.handle(Message(text="can I register my thesis with 118 credits"))
    assert res.intent is Intent.RULE
    assert len(res.sources) == 1
    assert res.sources[0].id == "H26-5.3"
    assert res.degraded is True
    # Falls back to template format: "Title: Text"
    assert res.answer.startswith("Thesis registration:")


@pytest.mark.parametrize("query", ["tuition 0 credits", "tuition 31 credits", "tuition -1 credits"])
def test_service_invalid_fee_keeps_fee_intent_without_fallback(service, query):
    response = service.handle(Message(text=query))
    assert response.intent is Intent.FEE
    assert response.sources == []
    assert response.degraded is False
    assert "Your tuition is" not in response.answer


@pytest.mark.parametrize("query", ["tuition 18.5 credits", "tuition 18 credits and 1.5 retake"])
def test_service_fractional_counts_return_guidance_not_wrong_fee(service, query):
    response = service.handle(Message(text=query))
    assert response.intent is Intent.FEE
    assert response.answer == "Credits and retake credits must be integers."
    assert response.sources == []
    assert response.degraded is False


def test_service_does_not_mask_programming_errors_as_provider_fallback(service):
    class BrokenResponder:
        def explain(self, question, rule):
            raise RuntimeError("unexpected programming error")

    service.responder = BrokenResponder()
    with pytest.raises(RuntimeError, match="unexpected programming error"):
        service.handle(Message(text="can I register my thesis with 118 credits"))
