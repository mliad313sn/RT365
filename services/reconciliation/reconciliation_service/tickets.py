"""Break tickets: account moves to Supervised (or Kill Switch for S1); resolution needs two-person confirmation [P6]."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from enum import Enum

from rtcore.errors import ControlDenied
from rtcore.lines import Actor, Role
from rtcore.schemas.base import StrictModel

from reconciliation_service.reconcile import Break, BreakSeverity


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    PENDING_SECOND = "PENDING_SECOND"
    RESOLVED = "RESOLVED"


class BreakTicket(StrictModel):
    ticket_id: str
    brk: Break
    status: TicketStatus
    opened_at: datetime
    first_resolver: str | None = None
    first_resolver_line: str | None = None
    second_resolver: str | None = None
    resolution: str | None = None
    resolved_at: datetime | None = None


RESOLVERS = frozenset({Role.OPERATIONS_ANALYST, Role.TRADING_DOMAIN_LEAD, Role.RISK_OFFICER, Role.CHIEF_RISK_AGENT, Role.SRE_LEAD})


class BreakTicketService:
    def __init__(
        self,
        *,
        on_break: Callable[[Break], object],
        audit: Callable[[str, str, dict[str, object]], object] | None = None,
    ) -> None:
        self._tickets: dict[str, BreakTicket] = {}
        self._on_break = on_break  # moves account to Supervised / Kill Switch per severity
        self._audit = audit or (lambda action, correlation_id, payload: None)

    def open(self, brk: Break, *, now: datetime) -> BreakTicket:
        # One ticket per (account, type, instrument) while it is open: recurring cycles must not spawn duplicates
        for t in self._tickets.values():
            if (
                t.status != TicketStatus.RESOLVED
                and t.brk.account_id == brk.account_id
                and t.brk.break_type == brk.break_type
                and t.brk.instrument_id == brk.instrument_id
            ):
                return t
        ticket = BreakTicket(ticket_id=f"tkt_{brk.break_id}", brk=brk, status=TicketStatus.OPEN, opened_at=now)
        self._tickets[ticket.ticket_id] = ticket
        self._on_break(brk)
        self._audit(
            "reconciliation.break.v1", brk.correlation_ids[0] if brk.correlation_ids else brk.break_id, ticket.model_dump(mode="json")
        )
        return ticket

    def resolve(self, ticket_id: str, actor: Actor, *, resolution: str, now: datetime) -> BreakTicket:
        t = self._tickets[ticket_id]
        if not actor.is_human or actor.role not in RESOLVERS:
            raise ControlDenied("break resolution requires an authorised human")
        if t.status == TicketStatus.RESOLVED:
            raise ControlDenied("ticket already resolved")
        if t.first_resolver is None:
            t = t.model_copy(
                update={
                    "status": TicketStatus.PENDING_SECOND,
                    "first_resolver": actor.actor_id,
                    "first_resolver_line": actor.line.value,
                    "resolution": resolution,
                }
            )
        else:
            if actor.actor_id == t.first_resolver:
                raise ControlDenied("two-person confirmation: second resolver must differ")
            if actor.line.value == t.first_resolver_line:
                raise ControlDenied("two-person confirmation: second resolver must sit in a different line of defense")
            t = t.model_copy(
                update={
                    "status": TicketStatus.RESOLVED,
                    "second_resolver": actor.actor_id,
                    "resolved_at": now,
                    "resolution": f"{t.resolution} | {resolution}",
                }
            )
        self._tickets[ticket_id] = t
        self._audit("reconciliation.ticket.updated", t.brk.break_id, t.model_dump(mode="json"))
        return t

    def open_tickets(self, account_id: str | None = None) -> tuple[BreakTicket, ...]:
        return tuple(
            t
            for t in self._tickets.values()
            if t.status != TicketStatus.RESOLVED and (account_id is None or t.brk.account_id == account_id)
        )

    def severity_of(self, brk: Break) -> BreakSeverity:
        return brk.severity
