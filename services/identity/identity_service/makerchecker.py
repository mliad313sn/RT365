"""Generic maker-checker primitive with cooling period [Source: 02, 05; E01].

Used for limit changes, mode promotion, tool registration. Agents can neither make nor check.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from rtcore.errors import ControlDenied
from rtcore.ids import new_id
from rtcore.lines import Actor
from rtcore.schemas.base import StrictModel


class ChangeStatus(str, Enum):
    PENDING = "PENDING"
    CHECKED = "CHECKED"
    EFFECTIVE = "EFFECTIVE"
    REJECTED = "REJECTED"


class PendingChange(StrictModel):
    change_id: str
    kind: str
    payload: dict[str, Any]
    maker_id: str
    maker_line: str
    status: ChangeStatus
    proposed_at: datetime
    checker_id: str | None = None
    checked_at: datetime | None = None
    effective_at: datetime | None = None
    reason: str | None = None


class MakerChecker:
    def __init__(
        self,
        *,
        cooling_period: timedelta,
        require_different_line: bool = False,
        audit_hook: Callable[[str, dict[str, object]], object] | None = None,
    ) -> None:
        self._cooling = cooling_period
        self._different_line = require_different_line
        self._changes: dict[str, PendingChange] = {}
        self._audit = audit_hook or (lambda action, payload: None)

    def propose(self, kind: str, payload: dict[str, Any], maker: Actor, *, now: datetime) -> PendingChange:
        if not maker.is_human:
            raise ControlDenied("only humans may propose controlled changes; agents/MCP have no write path")
        change = PendingChange(
            change_id=new_id("chg"),
            kind=kind,
            payload=payload,
            maker_id=maker.actor_id,
            maker_line=maker.line.value,
            status=ChangeStatus.PENDING,
            proposed_at=now,
        )
        self._changes[change.change_id] = change
        self._audit(f"{kind}.proposed", change.model_dump(mode="json"))
        return change

    def check(self, change_id: str, checker: Actor, *, now: datetime, reason: str = "") -> PendingChange:
        change = self._changes[change_id]
        if change.status != ChangeStatus.PENDING:
            raise ControlDenied(f"change {change_id} is {change.status.value}")
        if not checker.is_human:
            raise ControlDenied("checker must be human")
        if checker.actor_id == change.maker_id:
            raise ControlDenied("maker-checker: checker must differ from maker")
        if self._different_line and checker.line.value == change.maker_line:
            raise ControlDenied("checker must sit in a different line of defense")
        effective = now + self._cooling
        updated = change.model_copy(
            update={
                "status": ChangeStatus.CHECKED,
                "checker_id": checker.actor_id,
                "checked_at": now,
                "effective_at": effective,
                "reason": reason,
            }
        )
        self._changes[change_id] = updated
        self._audit(f"{change.kind}.checked", updated.model_dump(mode="json"))
        return updated

    def reject(self, change_id: str, checker: Actor, *, now: datetime, reason: str) -> PendingChange:
        change = self._changes[change_id]
        updated = change.model_copy(
            update={"status": ChangeStatus.REJECTED, "checker_id": checker.actor_id, "checked_at": now, "reason": reason}
        )
        self._changes[change_id] = updated
        self._audit(f"{change.kind}.rejected", updated.model_dump(mode="json"))
        return updated

    def effective(self, change_id: str, *, now: datetime) -> PendingChange | None:
        """Returns the change once checked and past its cooling period; None otherwise."""
        change = self._changes[change_id]
        if change.status == ChangeStatus.CHECKED and change.effective_at is not None and change.effective_at <= now:
            updated = change.model_copy(update={"status": ChangeStatus.EFFECTIVE})
            self._changes[change_id] = updated
            self._audit(f"{change.kind}.effective", updated.model_dump(mode="json"))
            return updated
        if change.status == ChangeStatus.EFFECTIVE:
            return change
        return None

    def get(self, change_id: str) -> PendingChange:
        return self._changes[change_id]

    def pending_ids(self) -> tuple[str, ...]:
        return tuple(cid for cid, c in self._changes.items() if c.status in (ChangeStatus.CHECKED, ChangeStatus.EFFECTIVE))
