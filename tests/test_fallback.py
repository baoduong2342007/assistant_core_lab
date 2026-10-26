"""Exercise actual service fallback through shared responder fixtures."""

import pytest

from assistant_core.models import Intent, Message
from assistant_core.responder import Responder


@pytest.mark.parametrize("failing", [False, True])
def test_service_responder_contract(service, stub_responder_success, stub_responder_fail, template_responder, failing):
    responder = stub_responder_fail if failing else stub_responder_success
    assert isinstance(responder, Responder)
    assert isinstance(template_responder, Responder)
    service.responder = responder
    service.fallback = template_responder
    rule = service.handbook.get_by_id("H26-5.3")
    response = service.handle(Message(text="can I register my thesis with 118 credits"))
    assert response.intent is Intent.RULE
    assert response.degraded is failing
    assert [(s.id, s.title) for s in response.sources] == [(rule.id, rule.title)]
    expected = template_responder if failing else stub_responder_success
    assert response.answer == expected.explain("question", rule)
