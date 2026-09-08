"""Outbox / inbox for at-least-once delivery with exactly-once business effect [Source: 03; ADR-005].

Both sit behind the ``rtcore.store.Store`` seam (ADR-010). The outbox is transactional: a producer writes the
event row in the same store transaction as its state change, and a relay hands pending rows to the bus and
marks them published, one row at a time, so a relay crash re-delivers only what was never marked. In dev/sim
the in-process subscribers are notified at publish time and the relay is exercised by tests [Open: R-05 bus].
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel
from rtcore.envelope import EventEnvelope
from rtcore.store import MemoryStore, Store

T = TypeVar("T")


class Outbox:
    def __init__(self, store: Store | None = None, *, table: str = "oms.outbox") -> None:
        self._store: Store = store or MemoryStore()
        self._table = table
        self._subscribers: list[Callable[[EventEnvelope], object]] = []

    @staticmethod
    def _encode(event: EventEnvelope, published: bool) -> str:
        return json.dumps({"published": published, "event": event.model_dump(mode="json")}, sort_keys=True)

    def _rows(self) -> list[tuple[EventEnvelope, bool]]:
        out = []
        for _key, raw in self._store.items(self._table):
            doc = json.loads(raw)
            out.append((EventEnvelope.model_validate(doc["event"]), bool(doc["published"])))
        return out

    def publish(self, event: EventEnvelope) -> None:
        """Write the event durably (inside the caller's transaction, if any), then notify in-process subscribers."""
        self._store.put(self._table, event.event_id, self._encode(event, False), correlation_id=event.correlation_id)
        for sub in self._subscribers:
            sub(event)

    def subscribe(self, fn: Callable[[EventEnvelope], object]) -> None:
        self._subscribers.append(fn)

    def events(self, name: str | None = None) -> tuple[EventEnvelope, ...]:
        return tuple(e for e, _ in self._rows() if name is None or e.event_name == name)

    def pending(self) -> tuple[EventEnvelope, ...]:
        """Events written but not yet handed to the bus."""
        return tuple(e for e, published in self._rows() if not published)

    def relay(self, fn: Callable[[EventEnvelope], object], *, limit: int | None = None) -> int:
        """Hand every pending event to ``fn`` in order and mark each published as soon as ``fn`` returns.

        Exactly once per event for a single relay: a crash inside ``fn`` leaves that event and all later ones
        pending; nothing already marked is delivered again. Returns the number delivered.
        """
        delivered = 0
        for event in self.pending():
            if limit is not None and delivered >= limit:
                break
            fn(event)
            self._store.put(self._table, event.event_id, self._encode(event, True), correlation_id=event.correlation_id)
            delivered += 1
        return delivered

    def replay(self, fn: Callable[[EventEnvelope], object]) -> int:
        """Re-deliver every event (simulates at-least-once redelivery). Returns count."""
        events = self.events()
        for e in events:
            fn(e)
        return len(events)


class Inbox:
    """Idempotent consumer: a key is processed once; later deliveries return the stored result.

    With a durable store the result is kept as JSON and decoded with ``model`` after a restart; results that are
    not pydantic models are served from the in-process cache only (and a durable inbox therefore requires ``model``).
    """

    def __init__(self, store: Store | None = None, *, table: str = "oms.inbox", model: type[BaseModel] | None = None) -> None:
        self._store: Store = store or MemoryStore()
        self._table = table
        self._model = model
        self._cache: dict[str, Any] = {}
        self.duplicates: int = 0

    def _encode(self, result: Any) -> str:
        if isinstance(result, BaseModel):
            return result.model_dump_json()
        return json.dumps(result, default=str)

    def _stored(self, key: str) -> Any:
        if key in self._cache:
            return self._cache[key]
        raw = self._store.get(self._table, key)
        if raw is None:
            raise KeyError(key)
        result = self._model.model_validate_json(raw) if self._model is not None else json.loads(raw)
        self._cache[key] = result
        return result

    def process_once(self, key: str, fn: Callable[[], T]) -> tuple[T, bool]:
        if self.seen(key):
            self.duplicates += 1
            return self._stored(key), False
        result = fn()
        self._cache[key] = result
        self._store.put(self._table, key, self._encode(result), correlation_id=key)
        return result, True

    def seen(self, key: str) -> bool:
        return key in self._cache or self._store.get(self._table, key) is not None
