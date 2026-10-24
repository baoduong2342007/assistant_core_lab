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


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured JSON logging to stderr without leaking secrets or full message texts."""
    logger = logging.getLogger("assistant_core")
    logger.setLevel(level.upper())

    # Avoid duplicate handlers if setup_logging is called repeatedly
    if not any(isinstance(h, logging.StreamHandler) and h.stream is sys.stderr for h in logger.handlers):
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    logger.propagate = False
    return logger
