"""Record retention with legal hold [Source: 06, 07; C5 §3; Open: O-09].

Deletion requests are *suppressed*, never destroyed, while a hold applies; the decision is logged.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from enum import Enum

from rtcore.errors import ControlDenied
from rtcore.lines import Actor, Role
from rtcore.schemas.base import StrictModel


class RetentionSchedule(StrictModel):
    record_class: str  # e.g. trading_record, identity, session_log
    jurisdiction: str
    retain_for: timedelta
    source_ref: str  # COMPLIANCE_MATRIX row / legal record


class LegalHold(StrictModel):
    hold_id: str
    scope: str  # tenant/account/customer id
    reason: str
    placed_by: str
    placed_at: datetime


class DeletionOutcome(str, Enum):
    DELETED = "DELETED"
    SUPPRESSED_LEGAL_HOLD = "SUPPRESSED_LEGAL_HOLD"
    SUPPRESSED_RETENTION = "SUPPRESSED_RETENTION"
    SUPPRESSED_NO_SCHEDULE = "SUPPRESSED_NO_SCHEDULE"  # fail closed: no schedule means we do not know the duty (review F-18)


class RetentionService:
    def __init__(self, audit_hook: Callable[[str, dict[str, object]], object] | None = None) -> None:
        self._schedules: dict[tuple[str, str], RetentionSchedule] = {}
        self._holds: dict[str, LegalHold] = {}
        self._audit = audit_hook or (lambda action, payload: None)

    def add_schedule(self, schedule: RetentionSchedule) -> None:
        self._schedules[(schedule.record_class, schedule.jurisdiction)] = schedule

    def place_hold(self, hold: LegalHold) -> None:
        self._holds[hold.hold_id] = hold
        self._audit("retention.hold.placed", hold.model_dump(mode="json"))

    def release_hold(self, hold_id: str, actor: Actor) -> None:
        if not actor.is_human or actor.role not in (Role.LEGAL_AGENT, Role.COMPLIANCE_AGENT):
            raise ControlDenied("only a human Legal or Compliance Agent may release a legal hold")
        hold = self._holds.pop(hold_id)
        self._audit("retention.hold.released", {**hold.model_dump(mode="json"), "released_by": actor.actor_id})

    def holds_for(self, *scopes: str) -> tuple[LegalHold, ...]:
        """A hold on any enclosing scope (tenant, account, customer) covers the record (Security review F-18)."""
        return tuple(h for h in self._holds.values() if h.scope in scopes)

    def request_deletion(
        self,
        *,
        record_class: str,
        jurisdiction: str,
        scopes: tuple[str, ...],
        record_created_at: datetime,
        now: datetime,
        requested_by: str,
    ) -> DeletionOutcome:
        if self.holds_for(*scopes):
            outcome = DeletionOutcome.SUPPRESSED_LEGAL_HOLD
        else:
            schedule = self._schedules.get((record_class, jurisdiction))
            if schedule is None:
                outcome = DeletionOutcome.SUPPRESSED_NO_SCHEDULE
            elif record_created_at + schedule.retain_for > now:
                outcome = DeletionOutcome.SUPPRESSED_RETENTION
            else:
                outcome = DeletionOutcome.DELETED
        self._audit(
            "retention.deletion.decided",
            {
                "record_class": record_class,
                "jurisdiction": jurisdiction,
                "scopes": list(scopes),
                "requested_by": requested_by,
                "outcome": outcome.value,
            },
        )
        return outcome
