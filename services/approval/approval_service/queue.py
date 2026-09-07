from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from enum import Enum

from rtcore.errors import ControlDenied
from rtcore.ids import new_id
from rtcore.lines import APPROVERS, Actor
from rtcore.schemas.base import StrictModel
from rtcore.schemas.decision import DecisionRecord, Outcome
from rtcore.schemas.intent import ValidatedIntent


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"


class ApprovalItem(StrictModel):
    approval_id: str
    validated_intent: ValidatedIntent
    decision: DecisionRecord
    maker_id: str  # who submitted the intent (agent or user); can never be the checker
    strategy_owner_id: str | None
    status: ApprovalStatus
    enqueued_at: datetime
    decided_by: str | None = None
    decided_at: datetime | None = None
    reason: str | None = None


class ApprovalRecord(StrictModel):
    approval_id: str
    intent_id: str
    decision_id: str
    approver_id: str
    approver_role: str
    maker_id: str
    approved_at: datetime
    reason: str


class ApprovalQueue:
    def __init__(self, audit_hook: Callable[[str, str, dict[str, object]], object] | None = None) -> None:
        self._items: dict[str, ApprovalItem] = {}
        self._audit = audit_hook or (lambda action, correlation_id, payload: None)

    def enqueue(
        self, vi: ValidatedIntent, decision: DecisionRecord, *, now: datetime, strategy_owner_id: str | None = None
    ) -> ApprovalItem:
        if decision.outcome != Outcome.REQUIRES_HUMAN_APPROVAL:
            raise ControlDenied("only REQUIRES_HUMAN_APPROVAL decisions enter the approval queue")
        if decision.intent_hash != vi.intent_hash:
            raise ControlDenied("decision does not match intent")
        item = ApprovalItem(
            approval_id=new_id("apr"),
            validated_intent=vi,
            decision=decision,
            maker_id=vi.submitted_by,
            strategy_owner_id=strategy_owner_id,
            status=ApprovalStatus.PENDING,
            enqueued_at=now,
        )
        self._items[item.approval_id] = item
        self._audit("approval.enqueued", vi.correlation_id, {"approval_id": item.approval_id, "intent_id": decision.intent_id})
        return item

    def pending(self, account_id: str | None = None) -> tuple[ApprovalItem, ...]:
        return tuple(
            i
            for i in self._items.values()
            if i.status == ApprovalStatus.PENDING and (account_id is None or i.validated_intent.intent.account_id == account_id)
        )

    def get(self, approval_id: str) -> ApprovalItem:
        return self._items[approval_id]

    def _check_actor(self, item: ApprovalItem, actor: Actor) -> None:
        if not actor.is_human:
            raise ControlDenied("approval requires a human approver; agents cannot approve")
        if actor.role not in APPROVERS:
            raise ControlDenied(f"role {actor.role.value} may not approve orders")
        if actor.actor_id == item.maker_id or (item.strategy_owner_id and actor.actor_id == item.strategy_owner_id):
            raise ControlDenied("maker-checker: approver must differ from the maker/strategy owner")
        if actor.tenant_id and actor.tenant_id != item.validated_intent.tenant_id:
            raise ControlDenied("approver belongs to a different tenant")

    def approve(self, approval_id: str, actor: Actor, *, reason: str, now: datetime) -> ApprovalRecord:
        item = self._items[approval_id]
        if item.status != ApprovalStatus.PENDING:
            raise ControlDenied(f"approval {approval_id} is {item.status.value}")
        if item.validated_intent.intent.expiry <= now:
            self._items[approval_id] = item.model_copy(update={"status": ApprovalStatus.EXPIRED, "decided_at": now})
            raise ControlDenied("intent expired before approval")
        self._check_actor(item, actor)
        self._items[approval_id] = item.model_copy(
            update={"status": ApprovalStatus.APPROVED, "decided_by": actor.actor_id, "decided_at": now, "reason": reason}
        )
        record = ApprovalRecord(
            approval_id=approval_id,
            intent_id=item.decision.intent_id,
            decision_id=item.decision.decision_id,
            approver_id=actor.actor_id,
            approver_role=actor.role.value,
            maker_id=item.maker_id,
            approved_at=now,
            reason=reason,
        )
        self._audit("approval.recorded", item.validated_intent.correlation_id, record.model_dump(mode="json"))
        return record

    def decline(self, approval_id: str, actor: Actor, *, reason: str, now: datetime) -> ApprovalItem:
        item = self._items[approval_id]
        if item.status != ApprovalStatus.PENDING:
            raise ControlDenied(f"approval {approval_id} is {item.status.value}")
        self._check_actor(item, actor)
        updated = item.model_copy(
            update={"status": ApprovalStatus.DECLINED, "decided_by": actor.actor_id, "decided_at": now, "reason": reason}
        )
        self._items[approval_id] = updated
        self._audit(
            "approval.declined", item.validated_intent.correlation_id, {"approval_id": approval_id, "by": actor.actor_id, "reason": reason}
        )
        return updated
