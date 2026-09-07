"""Outbox / inbox for at-least-once delivery with exactly-once business effect [Source: 03; ADR-005]."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from rtcore.envelope import EventEnvelope

T = TypeVar("T")


class Outbox:
    def __init__(self) -> None:
        self._events: list[EventEnvelope] = []
        self._subscribers: list[Callable[[EventEnvelope], object]] = []

    def publish(self, event: EventEnvelope) -> None:
        self._events.append(event)
        for sub in self._subscribers:
            sub(event)

    def subscribe(self, fn: Callable[[EventEnvelope], object]) -> None:
        self._subscribers.append(fn)

    def events(self, name: str | None = None) -> tuple[EventEnvelope, ...]:
        return tuple(e for e in self._events if name is None or e.event_name == name)

    def replay(self, fn: Callable[[EventEnvelope], object]) -> int:
        """Re-deliver every event (simulates at-least-once redelivery). Returns count."""
        for e in list(self._events):
            fn(e)
        return len(self._events)


class Inbox:
    """Idempotent consumer: a key is processed once; later deliveries return the stored result."""

    def __init__(self) -> None:
        self._seen: dict[str, Any] = {}
        self.duplicates: int = 0

    def process_once(self, key: str, fn: Callable[[], T]) -> tuple[T, bool]:
        if key in self._seen:
            self.duplicates += 1
            return self._seen[key], False
        result = fn()
        self._seen[key] = result
        return result, True

    def seen(self, key: str) -> bool:
        return key in self._seen
