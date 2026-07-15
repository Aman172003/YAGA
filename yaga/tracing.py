from __future__ import annotations

import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator

from yaga.logging import get_logger, log_event

logger = get_logger(__name__)
_trace_id: ContextVar[str | None] = ContextVar("yaga.trace_id", default=None)


def get_trace_id() -> str | None:
    return _trace_id.get()


def generate_trace_id() -> str:
    return uuid.uuid4().hex


@contextmanager
def trace_scope(trace_id: str | None = None) -> Iterator[str]:
    previous = _trace_id.get()
    current_trace_id = trace_id or previous or generate_trace_id()
    token = _trace_id.set(current_trace_id)
    try:
        yield current_trace_id
    finally:
        _trace_id.reset(token)


def trace_event(event: str, **context: Any) -> None:
    payload = {"trace_id": get_trace_id(), **context}
    log_event(logger, event, **payload)
