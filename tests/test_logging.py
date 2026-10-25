"""Unit tests for JSON logging and secret protection."""

import json
import logging
import sys
from io import StringIO

import pytest

from assistant_core.logging_setup import JsonFormatter, setup_logging


@pytest.fixture(autouse=True)
def restore_logger():
    """Restore the host application's logger after every test."""
    logger = logging.getLogger("assistant_core")
    handlers, level, propagate = logger.handlers[:], logger.level, logger.propagate
    logger.handlers = []
    yield
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    logger.handlers, logger.level, logger.propagate = handlers, level, propagate


def test_json_formatter():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="assistant_core",
        level=logging.INFO,
        pathname="service.py",
        lineno=42,
        msg="handled",
        args=(),
        exc_info=None,
    )
    record.intent = "fee"
    record.latency_ms = 1.25
    record.session = "local"
    record.degraded = False

    output = formatter.format(record)
    parsed = json.loads(output)
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "assistant_core"
    assert parsed["msg"] == "handled"
    assert parsed["intent"] == "fee"
    assert parsed["latency_ms"] == 1.25
    assert parsed["session"] == "local"
    assert parsed["degraded"] is False


def test_setup_logging_no_duplicates():
    logger1 = setup_logging("INFO")
    handler_count_1 = len(logger1.handlers)
    logger2 = setup_logging("INFO")
    handler_count_2 = len(logger2.handlers)
    assert handler_count_1 == handler_count_2


def test_setup_follows_replaced_stderr_without_duplicate_records(monkeypatch):
    first, second = StringIO(), StringIO()
    monkeypatch.setattr(sys, "stderr", first)
    logger = setup_logging("INFO")
    logger.info("first")
    monkeypatch.setattr(sys, "stderr", second)
    logger = setup_logging("DEBUG")
    setup_logging("DEBUG")
    logger.debug("second")
    assert len(logger.handlers) == 1
    assert [json.loads(line)["msg"] for line in first.getvalue().splitlines()] == ["first"]
    assert [json.loads(line)["msg"] for line in second.getvalue().splitlines()] == ["second"]


def test_logs_stay_on_stderr_and_ignore_sensitive_extra(capsys):
    logger = setup_logging("INFO")
    logger.info(
        "handled",
        extra={
            "intent": "fee",
            "latency_ms": 0.5,
            "session": "local",
            "degraded": False,
            "message_text": "private student question",
            "api_key": "fake-sensitive-key",
            "settings": {"llm_api_key": "fake-sensitive-key"},
        },
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert json.loads(captured.err) == {
        "level": "INFO",
        "logger": "assistant_core",
        "msg": "handled",
        "intent": "fee",
        "latency_ms": 0.5,
        "session": "local",
        "degraded": False,
    }
    assert "private student question" not in captured.err
    assert "fake-sensitive-key" not in captured.err


def test_setup_preserves_host_handlers_and_does_not_propagate(monkeypatch):
    host_stream, own_stream = StringIO(), StringIO()
    host_handler = logging.StreamHandler(host_stream)
    logging.getLogger("assistant_core").addHandler(host_handler)
    monkeypatch.setattr(sys, "stderr", own_stream)
    logger = setup_logging("warning")
    logger.info("hidden")
    logger.warning("visible")
    assert host_handler in logger.handlers
    assert logger.propagate is False
    assert host_stream.getvalue() == "visible\n"
    assert json.loads(own_stream.getvalue())["msg"] == "visible"
