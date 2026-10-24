"""Unit tests for JSON logging and secret protection."""

import json
import logging

from assistant_core.logging_setup import JsonFormatter, setup_logging


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
