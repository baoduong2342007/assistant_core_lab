import httpx

from ui.api_client import AssistantClient, ChatResult
from ui.logic import format_sources, status_note, validate_input

OK = {
    "answer": "Room B.201",
    "intent": "office",
    "sources": [{"id": "S26#1", "title": "1 Library borrowing"}],
    "degraded": False,
    "escalate": False,
    "path": "deterministic",
    "request_id": "abc123",
}


def client_with(handler) -> AssistantClient:
    return AssistantClient("http://api.test", transport=httpx.MockTransport(handler))


def test_ask_ok():
    r = client_with(lambda req: httpx.Response(200, json=OK)).ask("where is the library", "s1")
    assert r.ok and r.answer == "Room B.201" and r.request_id == "abc123"


def test_ask_backend_down():
    def boom(req):
        raise httpx.ConnectError("refused", request=req)

    r = client_with(boom).ask("hi", "s1")
    assert not r.ok and "backend" in r.error


def test_ask_validation_and_server_errors():
    assert "type a question" in client_with(lambda req: httpx.Response(422)).ask("", "s").error
    assert "error 500" in client_with(lambda req: httpx.Response(500)).ask("x", "s").error


def test_feedback():
    assert client_with(lambda req: httpx.Response(201, json={})).send_feedback("abc123", 1)


def test_validate_input():
    assert validate_input("   ") == "Please type a question."
    assert validate_input("x" * 2001).startswith("Your question is too long")
    assert validate_input("hello") is None


def test_format_sources():
    assert format_sources([]) == ""
    assert format_sources(OK["sources"]) == "Sources: S26#1 — 1 Library borrowing"


def test_status_note():
    assert "Training Office" in status_note(ChatResult(ok=True, escalate=True))
    assert status_note(ChatResult(ok=True)) is None


def test_healthy_status_and_network_error():
    assert client_with(lambda req: httpx.Response(200, json={"status": "ok"})).healthy() is True
    assert client_with(lambda req: httpx.Response(500)).healthy() is False

    def boom(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=req)

    assert client_with(boom).healthy() is False


def test_ask_timeout_and_http_errors():
    def timeout(req: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=req)

    r_timeout = client_with(timeout).ask("hello", "s1")
    assert not r_timeout.ok and "too long" in r_timeout.error

    r_429 = client_with(lambda req: httpx.Response(429)).ask("hello", "s1")
    assert not r_429.ok and "Too many questions" in r_429.error

    r_422 = client_with(lambda req: httpx.Response(422)).ask("", "s1")
    assert not r_422.ok and "1–2000" in r_422.error

    r_500 = client_with(lambda req: httpx.Response(500)).ask("hello", "s1")
    assert not r_500.ok and "error 500" in r_500.error

    def conn_err(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=req)

    r_conn = client_with(conn_err).ask("hello", "s1")
    assert not r_conn.ok and "backend" in r_conn.error


def test_send_feedback_success_404_and_network_error():
    captured: list[bytes] = []

    def ok_handler(req: httpx.Request) -> httpx.Response:
        captured.append(req.content)
        return httpx.Response(201, json={"id": 1})

    assert client_with(ok_handler).send_feedback("req-1", -1, "unclear") is True
    assert b'"request_id":"req-1"' in captured[0] or b'"request_id": "req-1"' in captured[0]
    assert b"-1" in captured[0]

    assert client_with(lambda req: httpx.Response(404)).send_feedback("missing", 1) is False

    def boom(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=req)

    assert client_with(boom).send_feedback("req-1", -1) is False


def test_format_sources_empty_single_and_multiple():
    assert format_sources([]) == ""
    assert format_sources([{"id": "S26#1", "title": "1 Library borrowing"}]) == "Sources: S26#1 — 1 Library borrowing"
    multi = [
        {"id": "H26#5.3", "title": "5.3 Thesis registration"},
        {"id": "S26#3", "title": "3 Student card replacement"},
    ]
    assert format_sources(multi) == "Sources: H26#5.3 — 5.3 Thesis registration; S26#3 — 3 Student card replacement"


def test_status_note_prioritizes_escalate_over_degraded():
    esc = status_note(ChatResult(ok=True, escalate=True, degraded=False))
    assert esc is not None and "Training Office" in esc and "I.101" in esc

    deg = status_note(ChatResult(ok=True, escalate=False, degraded=True))
    assert deg is not None and "source document" in deg and "unavailable" in deg

    both = status_note(ChatResult(ok=True, escalate=True, degraded=True))
    assert both is not None and "Training Office" in both and "I.101" in both
    assert "unavailable" not in both

    assert status_note(ChatResult(ok=True, escalate=False, degraded=False)) is None


def test_validate_input_boundaries():
    assert validate_input("   \t\n ") == "Please type a question."
    assert validate_input("x" * 2000) is None
    assert validate_input("  " + ("x" * 2000) + "  ") is None
    assert validate_input("x" * 2001).startswith("Your question is too long")
    assert validate_input("Tuition for 18 credits") is None
