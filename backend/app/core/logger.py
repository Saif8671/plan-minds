"""Structured JSON logging with request-id context variable support."""

import logging
import uuid
from contextvars import ContextVar

from pythonjsonlogger import jsonlogger

# Per-request ID propagated through the entire request context
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get("")  # type: ignore[attr-defined]
        return True


def setup_logging(level: str = "INFO") -> None:
    """Configure structured JSON logging for the application."""
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(_RequestIdFilter())

    root = logging.getLogger()
    root.setLevel(level)
    # Remove any pre-existing handlers (avoids duplicate logs when called again)
    root.handlers.clear()
    root.addHandler(handler)

    # Silence noisy third-party loggers
    for name in ("apscheduler", "httpx", "sqlalchemy.engine"):
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def new_request_id() -> str:
    """Generate a short request ID and set it in the context var."""
    rid = uuid.uuid4().hex[:12]
    request_id_var.set(rid)
    return rid
