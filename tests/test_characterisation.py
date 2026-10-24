"""Characterisation tests locking in original monolith behaviors."""

from assistant_core.models import Intent, Message


def test_characterisation_greeting(service):
    res = service.handle(Message(text="hi"))
    assert res.answer == "Hello! I can help with offices, fees and rules."
    assert res.intent is Intent.GREETING


def test_characterisation_tuition(service):
    res = service.handle(Message(text="tuition for 18 credits and 2 retake"))
    assert "9,450,000 VND" in res.answer
    assert res.intent is Intent.FEE


def test_characterisation_office_library(service):
    res = service.handle(Message(text="where is the library"))
    assert res.intent is Intent.OFFICE
    assert "Library: room B.201, open Mon-Sat 07:00-20:00." in res.answer


def test_characterisation_thesis_rule(service):
    res = service.handle(Message(text="can I register my thesis with 118 credits"))
    assert res.intent is Intent.RULE
    assert len(res.sources) == 1
    assert res.sources[0].id == "H26-5.3"
    assert "Thesis registration" in res.sources[0].title
