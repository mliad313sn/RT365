"""Trade-intent lifecycle P1 [Source: 00 pipeline; Committee state machine]. Monotonic; every transition audited."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from enum import Enum

from rtcore.errors import TransitionError
from rtcore.schemas.base import StrictModel
from rtcore.statemachine import MonotonicStateMachine


class IntentState(str, Enum):
    CREATED = "CREATED"
    SCHEMA_VALIDATED = "SCHEMA_VALIDATED"
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    RISK_DECIDED = "RISK_DECIDED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    AUTHORISED = "AUTHORISED"
    DECLINED = "DECLINED"
    REJECTED = "REJECTED"
    HALTED = "HALTED"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    BROKER_REJECTED = "BROKER_REJECTED"
    RECONCILED = "RECONCILED"
    ARCHIVED = "ARCHIVED"
    EXPIRED = "EXPIRED"


_T = {
    IntentState.CREATED: {IntentState.SCHEMA_VALIDATED, IntentState.REJECTED, IntentState.EXPIRED},
    IntentState.SCHEMA_VALIDATED: {IntentState.ELIGIBLE, IntentState.INELIGIBLE, IntentState.HALTED, IntentState.EXPIRED},
    IntentState.ELIGIBLE: {IntentState.RISK_DECIDED, IntentState.HALTED, IntentState.EXPIRED},
    IntentState.RISK_DECIDED: {
        IntentState.AUTHORISED,
        IntentState.PENDING_APPROVAL,
        IntentState.REJECTED,
        IntentState.HALTED,
        IntentState.EXPIRED,
    },
    IntentState.PENDING_APPROVAL: {
        IntentState.AUTHORISED,
        IntentState.DECLINED,
        IntentState.REJECTED,
        IntentState.EXPIRED,
        IntentState.HALTED,
    },
    IntentState.AUTHORISED: {IntentState.SUBMITTED, IntentState.EXPIRED, IntentState.HALTED},
    IntentState.SUBMITTED: {IntentState.ACKNOWLEDGED, IntentState.BROKER_REJECTED, IntentState.CANCELLED, IntentState.EXPIRED},
    IntentState.ACKNOWLEDGED: {IntentState.PARTIALLY_FILLED, IntentState.FILLED, IntentState.CANCELLED, IntentState.BROKER_REJECTED},
    IntentState.PARTIALLY_FILLED: {IntentState.PARTIALLY_FILLED, IntentState.FILLED, IntentState.CANCELLED},
    IntentState.FILLED: {IntentState.RECONCILED},
    IntentState.CANCELLED: {IntentState.RECONCILED},
    IntentState.BROKER_REJECTED: {IntentState.RECONCILED},
    IntentState.RECONCILED: {IntentState.ARCHIVED},
}
TERMINAL = frozenset(
    {IntentState.INELIGIBLE, IntentState.REJECTED, IntentState.HALTED, IntentState.DECLINED, IntentState.EXPIRED, IntentState.ARCHIVED}
)

INTENT_MACHINE: MonotonicStateMachine[IntentState] = MonotonicStateMachine({k: frozenset(v) for k, v in _T.items()}, TERMINAL)


class IntentStatus(StrictModel):
    intent_id: str
    correlation_id: str
    tenant_id: str  # the tenant the intent was sealed under: every read of the status is filtered by it (NFR-TEN-01)
    state: IntentState
    history: tuple[tuple[str, str], ...]
    updated_at: datetime


class IntentTracker:
    def __init__(self, audit_hook: Callable[[str, str, dict[str, object]], object] | None = None) -> None:
        self._status: dict[str, IntentStatus] = {}
        self._audit = audit_hook or (lambda action, correlation_id, payload: None)

    def exists(self, intent_id: str) -> bool:
        return intent_id in self._status

    def create(self, intent_id: str, correlation_id: str, *, tenant_id: str, now: datetime) -> IntentStatus:
        if intent_id in self._status:
            raise TransitionError(f"intent {intent_id} already tracked; states are monotonic and never reset")
        st = IntentStatus(
            intent_id=intent_id,
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            state=IntentState.CREATED,
            history=((IntentState.CREATED.value, now.isoformat()),),
            updated_at=now,
        )
        self._status[intent_id] = st
        self._audit("intent.state", correlation_id, {"intent_id": intent_id, "tenant_id": tenant_id, "state": st.state.value})
        return st

    def transition(self, intent_id: str, nxt: IntentState, *, now: datetime, detail: dict[str, object] | None = None) -> IntentStatus:
        cur = self._status[intent_id]
        INTENT_MACHINE.assert_transition(cur.state, nxt)
        st = cur.model_copy(update={"state": nxt, "history": (*cur.history, (nxt.value, now.isoformat())), "updated_at": now})
        self._status[intent_id] = st
        self._audit(
            "intent.state", cur.correlation_id, {"intent_id": intent_id, "tenant_id": cur.tenant_id, "state": nxt.value, **(detail or {})}
        )
        return st

    def get(self, intent_id: str) -> IntentStatus:
        return self._status[intent_id]

    def get_in_tenant(self, intent_id: str, tenant_id: str) -> IntentStatus | None:
        """Tenant-scoped read: ``None`` for an unknown intent and for another tenant's (no existence leak)."""
        st = self._status.get(intent_id)
        if st is None or st.tenant_id != tenant_id:
            return None
        return st

    def all(self) -> tuple[IntentStatus, ...]:
        return tuple(self._status.values())
