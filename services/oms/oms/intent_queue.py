"""Control-plane intake queue: the only path from Analytics to Control [Source: 00, 04; ADR-001].

Strict schema validation; unknown fields rejected; intent immutable after validation (P1).
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from datetime import datetime
from typing import Any

from pydantic import ValidationError
from rtcore.envelope import make_event
from rtcore.errors import SchemaViolation
from rtcore.ids import new_id
from rtcore.planes import GUARD, Plane, PlaneGuard
from rtcore.schemas.intent import TradeIntent, ValidatedIntent

from oms.lifecycle import IntentState, IntentTracker
from oms.outbox import Outbox


class IntentQueue:
    def __init__(
        self,
        tracker: IntentTracker,
        outbox: Outbox,
        *,
        max_depth: int = 10_000,
        on_reject: Callable[[str, dict[str, Any]], object] | None = None,
        instrument_valid: Callable[[str, str, datetime], bool] | None = None,
        guard: PlaneGuard = GUARD,
    ) -> None:
        self._q: deque[ValidatedIntent] = deque()
        self._guard = guard
        self._instrument_valid = instrument_valid or (lambda instrument_id, venue, ts: True)
        self._tracker = tracker
        self._outbox = outbox
        self._max_depth = max_depth
        self._on_reject = on_reject or (lambda correlation_id, payload: None)
        self._seen_hashes: set[str] = set()

    def submit(
        self, raw: dict[str, Any] | TradeIntent, *, tenant_id: str, submitted_by: str, now: datetime, correlation_id: str | None = None
    ) -> ValidatedIntent:
        self._guard.check_caller(Plane.CONTROL, "intent_queue")
        corr = correlation_id or new_id("corr")
        intent_id = str(raw.get("intent_id", "unknown")) if isinstance(raw, dict) else str(raw.intent_id)
        if self._tracker.exists(intent_id):
            # Replayed intent_id (review F-01): the first submission stands; the replay is refused, not reset.
            self._on_reject(corr, {"intent_id": intent_id, "reason": "DUPLICATE_INTENT_ID"})
            raise SchemaViolation(f"intent {intent_id} was already submitted")
        self._tracker.create(intent_id, corr, tenant_id=tenant_id, now=now)
        try:
            intent = raw if isinstance(raw, TradeIntent) else TradeIntent.model_validate(raw)
        except ValidationError as exc:
            self._tracker.transition(
                intent_id, IntentState.REJECTED, now=now, detail={"reason": "SCHEMA", "errors": exc.errors(include_url=False)[:5]}
            )
            self._on_reject(corr, {"intent_id": intent_id, "reason": "SCHEMA_VIOLATION"})
            raise SchemaViolation(str(exc)) from exc
        if intent.expiry <= now:
            self._tracker.transition(intent_id, IntentState.EXPIRED, now=now)
            raise SchemaViolation("intent already expired")
        if intent.market_ts > now:
            self._tracker.transition(intent_id, IntentState.REJECTED, now=now, detail={"reason": "STALE_OR_FUTURE_TS"})
            raise SchemaViolation("intent market_ts is in the future")
        if not self._instrument_valid(intent.instrument_id, intent.venue, intent.market_ts):
            # Hallucinated or delisted symbol is rejected here, before any engine sees it [C3 control test].
            self._tracker.transition(
                intent_id, IntentState.REJECTED, now=now, detail={"reason": "INVALID_SYMBOL", "instrument_id": intent.instrument_id}
            )
            self._on_reject(corr, {"intent_id": intent_id, "reason": "INVALID_SYMBOL"})
            raise SchemaViolation(f"invalid symbol {intent.instrument_id}@{intent.venue} at {intent.market_ts.isoformat()}")
        if len(self._q) >= self._max_depth:
            self._tracker.transition(intent_id, IntentState.REJECTED, now=now, detail={"reason": "BACKPRESSURE"})
            raise SchemaViolation("intent queue at capacity; analytics shed first [Committee C2 §6]")
        vi = ValidatedIntent.seal(intent, correlation_id=corr, tenant_id=tenant_id, submitted_by=submitted_by, validated_at=now)
        if vi.intent_hash in self._seen_hashes:
            self._tracker.transition(intent_id, IntentState.REJECTED, now=now, detail={"reason": "DUPLICATE_INTENT_HASH"})
            raise SchemaViolation("identical intent already submitted (replay)")
        self._seen_hashes.add(vi.intent_hash)
        self._tracker.transition(intent_id, IntentState.SCHEMA_VALIDATED, now=now, detail={"intent_hash": vi.intent_hash})
        self._q.append(vi)
        self._outbox.publish(
            make_event(
                "intent.submitted.v1",
                correlation_id=corr,
                tenant=tenant_id,
                account=intent.account_id,
                producer="oms.intent_queue",
                payload=vi,
                market_ts=intent.market_ts,
                emitted_ts=now,
            )
        )
        return vi

    def pop(self) -> ValidatedIntent | None:
        return self._q.popleft() if self._q else None

    def take(self, intent_id: str, tenant_id: str) -> ValidatedIntent | None:
        """Remove and return one queued intent of ``tenant_id``; other tenants' intents are neither drained nor revealed."""
        for ix, vi in enumerate(self._q):
            if str(vi.intent.intent_id) == intent_id:
                if vi.tenant_id != tenant_id:
                    return None
                del self._q[ix]
                return vi
        return None

    def __len__(self) -> int:
        return len(self._q)
