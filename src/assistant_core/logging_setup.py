"""Structured JSON logging configuration."""

import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    """Format log records into structured single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        data = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ("intent", "latency_ms", "session", "degraded"):
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


class _JsonStderrHandler(logging.StreamHandler):
    """Mark the handler owned by this package, preserving embedding-app handlers."""


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured JSON logging to stderr without leaking secrets or full message texts."""
    logger = logging.getLogger("assistant_core")
    logger.setLevel(level.strip().upper())

    # A test runner or embedding application can replace stderr between calls.
    handlers = [handler for handler in logger.handlers if isinstance(handler, _JsonStderrHandler)]
    current = next((handler for handler in handlers if handler.stream is sys.stderr), None)
    for handler in handlers:
        if handler is not current:
            logger.removeHandler(handler)
            handler.close()
    if current is None:
        handler = _JsonStderrHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    logger.propagate = False
    return logger
