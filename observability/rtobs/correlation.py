from __future__ import annotations

import contextvars
from collections.abc import Iterator
from contextlib import contextmanager

_cid: contextvars.ContextVar[str | None] = contextvars.ContextVar("rt_correlation_id", default=None)


def current_correlation_id() -> str | None:
    return _cid.get()


@contextmanager
def correlation(correlation_id: str) -> Iterator[None]:
    token = _cid.set(correlation_id)
    try:
        yield
    finally:
        _cid.reset(token)
