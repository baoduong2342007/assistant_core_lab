"""Unit tests for domain models."""

import pytest
from pydantic import ValidationError

from assistant_core.models import Intent, Message, Response, Rule, Source


def test_intent_values():
    assert Intent.GREETING == "greeting"
    assert Intent.FEE == "fee"
    assert Intent.OFFICE == "office"
    assert Intent.RULE == "rule"
    assert Intent.UNKNOWN == "unknown"


def test_message_valid():
    msg = Message(text="hello")
    assert msg.text == "hello"
    assert msg.session_id == "local"


def test_message_whitespace_only():
    with pytest.raises(ValidationError):
        Message(text="   ")


def test_message_empty():
    with pytest.raises(ValidationError):
        Message(text="")


def test_message_max_length():
    msg = Message(text="a" * 2000)
    assert len(msg.text) == 2000
    with pytest.raises(ValidationError):
        Message(text="a" * 2001)


def test_response_sources_default_factory_independence():
    r1 = Response(answer="ans 1", intent=Intent.GREETING)
    r2 = Response(answer="ans 2", intent=Intent.GREETING)
    assert r1.sources is not r2.sources
    r1.sources.append(Source(id="S1", title="Source 1"))
    assert len(r2.sources) == 0


def test_rule_model():
    rule = Rule(id="H26-1.1", title="Title", text="Rule text")
    assert rule.id == "H26-1.1"
    assert rule.title == "Title"
    assert rule.text == "Rule text"
