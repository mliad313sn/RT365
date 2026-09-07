"""Structured JSON logging with redaction at emission (NFR-PRV-01) and correlation ID on every line."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import Any

from rtobs.correlation import current_correlation_id

_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "<email>"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]+"), "bearer <token>"),
    (re.compile(r"vault://[^\s\"']+"), "vault://<ref>"),
    (re.compile(r"\b\d{12,19}\b"), "<number>"),
    (re.compile(r"(?i)(\"?(?:secret|password|api_key|token)\"?\s*[:=]\s*)\"?[^\s\",}]+\"?"), r"\1<redacted>"),
)


def redact(text: str) -> str:
    for pattern, repl in _PATTERNS:
        text = pattern.sub(repl, text)
    return text


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": redact(record.getMessage()),
            "correlation_id": getattr(record, "correlation_id", None) or current_correlation_id(),
        }
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update({k: redact(str(v)) for k, v in extra.items()})
        return json.dumps(payload, sort_keys=True)


class _Adapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: Any) -> tuple[str, Any]:
        extra = kwargs.pop("extra", None) or {}
        kwargs["extra"] = {"extra_fields": extra}
        return msg, kwargs


def get_logger(name: str) -> logging.LoggerAdapter:
    logger = logging.getLogger(name)
    if not any(isinstance(h.formatter, JsonFormatter) for h in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return _Adapter(logger, {})
