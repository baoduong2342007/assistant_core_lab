"""Tests for Bảo's Lab 07 H1 fix: English-rephrase guidance and quick suggestions on mixed/shorthand queries."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
from streamlit.testing.v1 import AppTest

from ui.api_client import AssistantClient, ChatResult
from ui.logic import CHAT_PLACEHOLDER, escalation_note, has_mixed_or_shorthand, suggest_english_queries

APP = Path(__file__).resolve().parents[1] / "ui/app.py"


def test_mixed_or_shorthand_detection_and_suggestions():
    assert has_mixed_or_shorthand("118 credits có đăng kí làm khóa luận được kh") is True
    assert has_mixed_or_shorthand("tui mất studnet card thì làm lại ở đâu") is True
    assert has_mixed_or_shorthand("Can I register my thesis with 118 credits?") is False

    assert suggest_english_queries("118 credits có đăng kí làm khóa luận được kh") == [
        "Can I register my thesis with 118 credits?"
    ]
    assert suggest_english_queries("tui mất studnet card thì làm lại ở đâu") == ["I lost my student card"]
    assert suggest_english_queries("what is the capital of France") == []


def test_escalation_note_for_mixed_query():
    mixed_escalate = ChatResult(ok=True, escalate=True)
    note = escalation_note("118 credits có đăng kí làm khóa luận được kh", mixed_escalate)
    assert note is not None
    assert "full English keywords" in note
    assert "Training Office, room I.101" in note

    plain_escalate = escalation_note("what is the capital of France", mixed_escalate)
    assert plain_escalate is not None and "I could not find this" in plain_escalate


def test_h1_mixed_query_shows_suggestion_and_recovers(monkeypatch):
    requests: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(200)
        body = json.loads(request.content)
        requests.append(body)
        if "khóa luận" in body["message"]:
            return httpx.Response(
                200,
                json={
                    "answer": (
                        "I'm not confident I can answer that from the official documents. "
                        "Please contact the Training Office (room I.101) or ask your academic advisor."
                    ),
                    "intent": "unknown",
                    "sources": [],
                    "degraded": False,
                    "escalate": True,
                    "path": "abstain",
                    "request_id": "req-mixed",
                },
            )
        return httpx.Response(
            200,
            json={
                "answer": "According to 5.3 Thesis registration: at least 120 credits and GPA 2.0.",
                "intent": "rule",
                "sources": [{"id": "H26#5.3", "title": "5.3 Thesis registration"}],
                "degraded": False,
                "escalate": False,
                "path": "rag",
                "request_id": "req-en",
            },
        )

    monkeypatch.setattr(
        "ui.api_client.AssistantClient",
        lambda: AssistantClient(transport=httpx.MockTransport(handler)),
    )
    app = AppTest.from_file(str(APP)).run()
    assert app.chat_input[0].placeholder == CHAT_PLACEHOLDER

    app.chat_input[0].set_value("118 credits có đăng kí làm khóa luận được kh").run()
    assert any("full English keywords" in box.value for box in app.info)
    suggest_btn = app.button(key="suggest-req-mixed-0")
    assert "Can I register my thesis with 118 credits?" in suggest_btn.label

    suggest_btn.click().run()
    assert requests[-1]["message"] == "Can I register my thesis with 118 credits?"
    assert any("H26#5.3" in c.value for c in app.caption)
    assert not app.exception
