"""Lab 07 tests for Quyền's UI logic, HTTP client, Streamlit AppTest, and KB/SQLite integration."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from assistant_api.db import make_engine as real_make_engine
from assistant_api.main import create_app
from assistant_core.config import Settings
from assistant_core.service import build_service
from ui.api_client import AssistantClient, ChatResult, api_url
from ui.logic import EXAMPLES, WELCOME, format_sources, status_note, validate_input

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = REPO_ROOT / "ui" / "app.py"
OK_PAYLOAD = {
    "answer": "Students may register a thesis when they have at least 120 credits and GPA 2.0.",
    "intent": "rule",
    "sources": [{"id": "H26#5.3", "title": "5.3 Thesis registration"}],
    "degraded": False,
    "escalate": False,
    "path": "llm",
    "confidence": 0.7,
    "request_id": "req-1",
}


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def test_ui_boundary_and_logic_independence():
    assert "streamlit" not in _imported_modules(REPO_ROOT / "ui" / "logic.py")
    for file_name in ("logic.py", "api_client.py", "app.py"):
        imports = _imported_modules(REPO_ROOT / "ui" / file_name)
        assert "assistant_core" not in imports
        assert "assistant_api" not in imports


def test_format_sources_empty_single_and_multiple():
    assert format_sources([]) == ""
    assert format_sources([{"id": "S26#3", "title": "3 Student card replacement"}]) == (
        "Sources: S26#3 — 3 Student card replacement"
    )
    multiple = [
        {"id": "H26#5.3", "title": "5.3 Thesis registration"},
        {"id": "H26#5.4", "title": "5.4 Late thesis registration"},
    ]
    assert format_sources(multiple) == (
        "Sources: H26#5.3 — 5.3 Thesis registration; H26#5.4 — 5.4 Late thesis registration"
    )


@pytest.mark.parametrize(
    ("escalate", "degraded", "expected"),
    [
        (True, False, "Training Office, room I.101"),
        (False, True, "AI helper was unavailable"),
        (True, True, "Training Office, room I.101"),
        (False, False, None),
    ],
)
def test_status_note_priority_and_states(escalate, degraded, expected):
    note = status_note(ChatResult(ok=True, escalate=escalate, degraded=degraded))
    if expected is None:
        assert note is None
    else:
        assert note is not None and expected in note


@pytest.mark.parametrize(
    ("text", "expected_error"),
    [
        ("", "Please type a question."),
        ("   \t\n  ", "Please type a question."),
        ("a", None),
        ("x" * 2000, None),
        ("  " + ("x" * 2000) + "  ", None),
        ("x" * 2001, "Your question is too long (max 2000 characters)."),
    ],
)
def test_validate_input_boundaries(text, expected_error):
    assert validate_input(text) == expected_error


def test_welcome_and_examples_state_ai_role():
    assert "AI" in WELCOME
    assert len(EXAMPLES) == 4


@pytest.mark.parametrize(
    ("raw_url", "expected"),
    [
        ("http://127.0.0.1:8000/", "http://127.0.0.1:8000"),
        (" https://assistant.fit.test/api/ ", "https://assistant.fit.test/api"),
    ],
)
def test_api_url_accepts_clean_http_urls(raw_url, expected):
    assert api_url(raw_url) == expected


@pytest.mark.parametrize(
    "bad_url",
    [
        "",
        "ftp://127.0.0.1:8000",
        "http://user:secret@127.0.0.1:8000",
        "http://127.0.0.1:8000?token=secret",
        "http://127.0.0.1:8000#frag",
        "http://[::1",
    ],
)
def test_api_url_rejects_unsafe_or_malformed_values(bad_url):
    with pytest.raises(ValueError):
        api_url(bad_url)


def test_api_url_reads_ui_env_without_backend_dotenv(monkeypatch):
    monkeypatch.setenv("ASSISTANT_API_URL", "http://localhost:8010/")
    assert api_url() == "http://localhost:8010"


@pytest.mark.parametrize("bad_timeout", [0, -1, float("nan"), float("inf")])
def test_client_rejects_non_positive_or_non_finite_timeout(bad_timeout):
    with pytest.raises(ValueError):
        AssistantClient(timeout_s=bad_timeout)


@pytest.mark.parametrize(
    ("status", "fragment"),
    [
        (422, "1–2000"),
        (429, "wait a minute"),
        (500, "error 500"),
        (503, "error 503"),
    ],
)
def test_client_ask_http_error_mapping(status, fragment):
    requests = []

    def handler(req):
        requests.append(req)
        return httpx.Response(status, text="internal secret stack")

    with AssistantClient(transport=httpx.MockTransport(handler)) as client:
        res = client.ask("  hello  ", "sess-1")
    assert not res.ok and fragment in res.error
    assert "internal secret stack" not in res.error
    assert len(requests) == 1
    assert json.loads(requests[0].content) == {"message": "hello", "session_id": "sess-1"}


@pytest.mark.parametrize("exc_type", [httpx.ConnectError, httpx.ReadTimeout])
def test_client_ask_network_failures_do_not_retry(exc_type):
    calls = 0

    def handler(req):
        nonlocal calls
        calls += 1
        raise exc_type("private detail", request=req)

    with AssistantClient(transport=httpx.MockTransport(handler)) as client:
        res = client.ask("question", "sess-1")
    assert not res.ok and "private detail" not in res.error
    assert calls == 1


@pytest.mark.parametrize(
    "raw_body",
    ["not json", "{}", json.dumps(OK_PAYLOAD | {"request_id": ""}), json.dumps(OK_PAYLOAD | {"confidence": 2.5})],
)
def test_client_ask_rejects_malformed_payloads(raw_body):
    with AssistantClient(transport=httpx.MockTransport(lambda req: httpx.Response(200, text=raw_body))) as client:
        res = client.ask("question", "sess-1")
    assert not res.ok and "unreadable reply" in res.error


@pytest.mark.parametrize("status", [404, 422, 429, 500, 200])
def test_client_send_feedback_requires_201_and_allows_retry(status):
    responses = iter([httpx.Response(status), httpx.Response(201, json={})])
    with AssistantClient(transport=httpx.MockTransport(lambda req: next(responses))) as client:
        assert not client.send_feedback("req-1", -1)
        assert client.last_feedback_error
        assert client.send_feedback("req-1", -1)
        assert client.last_feedback_error == ""


@pytest.mark.parametrize("bad_rating", [0, 2, True, "1"])
def test_client_send_feedback_rejects_invalid_ratings_locally(bad_rating):
    def fail_if_called(req):
        raise AssertionError("should not post invalid feedback")

    with AssistantClient(transport=httpx.MockTransport(fail_if_called)) as client:
        assert not client.send_feedback("req-1", bad_rating)
        assert client.last_feedback_error


def test_client_health_handles_unreachable_and_non_200():
    def down(req):
        raise httpx.ConnectError("down", request=req)

    with AssistantClient(transport=httpx.MockTransport(down)) as client:
        assert not client.healthy()
        assert "unreachable" in client.health_error

    with AssistantClient(transport=httpx.MockTransport(lambda req: httpx.Response(503))) as client:
        assert not client.healthy()
        assert "503" in client.health_error


def test_kb_answers_degraded_fallback_and_sqlite_persistence(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("assistant_api.main.make_engine", real_make_engine)
    db_file = tmp_path / "lab7_quyen.db"
    settings = Settings(
        data_dir=REPO_ROOT / "data",
        llm_provider="stub",
        database_url=f"sqlite:///{db_file}",
        api_admin_key="quyen-admin-key",
    )

    app1 = create_app(settings=settings)
    with TestClient(app1) as c1:
        assert c1.get("/health").status_code == 200

        thesis = c1.post("/v1/chat", json={"message": EXAMPLES[0], "session_id": "quyen-s1"}).json()
        assert "120" in thesis["answer"] and "2.0" in thesis["answer"]
        assert format_sources(thesis["sources"]) == "Sources: H26#5.3 — 5.3 Thesis registration"

        card = c1.post("/v1/chat", json={"message": EXAMPLES[3], "session_id": "quyen-s1"}).json()
        assert "I.102" in card["answer"] and "50,000" in card["answer"]
        assert format_sources(card["sources"]) == "Sources: S26#3 — 3 Student card replacement"

        tuition = c1.post("/v1/chat", json={"message": EXAMPLES[1], "session_id": "quyen-s1"}).json()
        assert "9,450,000" in tuition["answer"]
        assert format_sources(tuition["sources"]) == ""

        library = c1.post("/v1/chat", json={"message": EXAMPLES[2], "session_id": "quyen-s1"}).json()
        assert "B.201" in library["answer"]
        assert format_sources(library["sources"]) == ""

        unknown = c1.post(
            "/v1/chat", json={"message": "what is the capital of France", "session_id": "quyen-s1"}
        ).json()
        assert unknown["path"] == "abstain" and unknown["escalate"] is True and unknown["sources"] == []
        note = status_note(ChatResult(ok=True, escalate=unknown["escalate"], degraded=unknown["degraded"]))
        assert note is not None and "Training Office, room I.101" in note

        assert (
            c1.post(
                "/v1/feedback",
                json={"request_id": card["request_id"], "rating": -1, "comment": "quyen check"},
            ).status_code
            == 201
        )
        assert c1.post("/v1/feedback", json={"request_id": "missing-id", "rating": 1}).status_code == 404

    app2 = create_app(settings=settings)
    with TestClient(app2) as c2:
        saved = c2.get("/v1/feedback", headers={"X-API-Key": "quyen-admin-key"})
        assert saved.status_code == 200
        rows = saved.json()
        assert len(rows) == 1
        assert rows[0]["request_id"] == card["request_id"]
        assert rows[0]["rating"] == -1

    degraded_app = create_app(settings=settings, service=build_service(settings, fail_provider=True))
    with TestClient(degraded_app) as c_deg:
        deg = c_deg.post("/v1/chat", json={"message": EXAMPLES[0], "session_id": "quyen-deg"}).json()
        assert deg["degraded"] is True and deg["escalate"] is False
        assert format_sources(deg["sources"]) == "Sources: H26#5.3 — 5.3 Thesis registration"
        assert "AI helper was unavailable" in (
            status_note(ChatResult(ok=True, escalate=deg["escalate"], degraded=deg["degraded"])) or ""
        )


@pytest.fixture
def streamlit_app(monkeypatch):
    state = {
        "requests": [],
        "online": True,
        "feedback_status": 201,
        "next_chat": None,
    }

    def handler(request):
        if not state["online"]:
            raise httpx.ConnectError("offline", request=request)
        if request.url.path == "/health":
            return httpx.Response(200)
        body = json.loads(request.content)
        state["requests"].append((request.url.path, body))
        if request.url.path == "/v1/feedback":
            return httpx.Response(state["feedback_status"])
        idx = sum(path == "/v1/chat" for path, _ in state["requests"])
        payload = state["next_chat"] or (OK_PAYLOAD | {"request_id": f"req-{idx}"})
        return httpx.Response(200, json=payload)

    monkeypatch.setattr(
        "ui.api_client.AssistantClient",
        lambda: AssistantClient(transport=httpx.MockTransport(handler)),
    )
    app = AppTest.from_file(str(APP_PATH)).run()
    assert not app.exception
    return app, state


def test_app_sidebar_chat_shared_flow_and_validation(streamlit_app):
    app, state = streamlit_app
    session_id = app.session_state.session_id

    app.chat_input[0].set_value("   ").run()
    app.chat_input[0].set_value("x" * 2001).run()
    assert state["requests"] == []
    assert app.warning

    app.sidebar.button[0].click().run()
    assert len(state["requests"]) == 1
    assert state["requests"][0] == ("/v1/chat", {"message": EXAMPLES[0], "session_id": session_id})
    assert any("H26#5.3" in c.value for c in app.caption)

    app.chat_input[0].set_value("  I lost my student card  ").run()
    assert len(state["requests"]) == 2
    assert state["requests"][1] == ("/v1/chat", {"message": "I lost my student card", "session_id": session_id})
    assert app.session_state.session_id == session_id


def test_app_feedback_success_retry_and_no_duplicate_on_rerun(streamlit_app):
    app, state = streamlit_app
    app.sidebar.button[0].click().run()

    state["feedback_status"] = 404
    app.button(key="down-req-1").click().run()
    assert "req-1" not in app.session_state.rated
    assert app.error
    assert any(b.key == "down-req-1" for b in app.button)

    state["feedback_status"] = 201
    app.button(key="down-req-1").click().run()
    assert state["requests"][-1] == ("/v1/feedback", {"request_id": "req-1", "rating": -1, "comment": None})
    assert "req-1" in app.session_state.rated
    assert app.success and not app.error
    assert all(b.key not in ("up-req-1", "down-req-1") for b in app.button)

    app.run()
    assert len(state["requests"]) == 3


def test_app_thumbs_up_also_checks_201_before_locking(streamlit_app):
    app, state = streamlit_app
    app.sidebar.button[0].click().run()
    state["feedback_status"] = 500
    app.button(key="up-req-1").click().run()
    assert "req-1" not in app.session_state.rated
    assert any(b.key == "up-req-1" for b in app.button)

    state["feedback_status"] = 201
    app.button(key="up-req-1").click().run()
    assert state["requests"][-1] == ("/v1/feedback", {"request_id": "req-1", "rating": 1, "comment": None})
    assert "req-1" in app.session_state.rated


def test_app_offline_preserves_history_escalation_and_isolated_sessions(streamlit_app):
    app, state = streamlit_app
    state["next_chat"] = {
        "answer": "Please contact the Training Office (room I.101).",
        "intent": "unknown",
        "sources": [],
        "degraded": True,
        "escalate": True,
        "path": "abstain",
        "request_id": "req-esc",
    }
    app.chat_input[0].set_value("what is the capital of France").run()
    assert any("Training Office, room I.101" in info.value for info in app.info)

    saved_messages = list(app.session_state.messages)
    state["online"] = False
    app.run()
    assert app.error
    assert app.session_state.messages == saved_messages

    second = AppTest.from_file(str(APP_PATH)).run()
    assert second.session_state.session_id != app.session_state.session_id
    assert len(second.session_state.messages) == 1

    state["online"] = True
    app.sidebar.button(key="new_chat").click().run()
    assert app.session_state.session_id != second.session_state.session_id
    assert len(app.session_state.messages) == 1
