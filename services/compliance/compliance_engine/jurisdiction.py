"""Dual-key market enablement [Source: 07; C6 §1; P5].

A cell is live only when (a) a signed legal record exists and (b) the technical flag is
activated by a *different* person. Either alone is insufficient. Disabling is single-person.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from rtcore.errors import ControlDenied
from rtcore.lines import Actor, Role
from rtcore.schemas.compliance import CustomerType, JurisdictionCell


class JurisdictionRegistry:
    def __init__(self, audit_hook: Callable[[str, dict[str, object]], object] | None = None) -> None:
        self._cells: dict[tuple[str, str, str, str, str, str], JurisdictionCell] = {}
        self._audit = audit_hook or (lambda action, payload: None)

    def cells(self) -> tuple[JurisdictionCell, ...]:
        return tuple(self._cells.values())

    def propose(
        self, *, country: str, customer_type: CustomerType, broker: str, venue: str, asset_class: str, feature: str
    ) -> JurisdictionCell:
        cell = JurisdictionCell(
            country=country, customer_type=customer_type, broker=broker, venue=venue, asset_class=asset_class, feature=feature
        )
        self._cells[cell.key] = cell
        self._audit("jurisdiction.cell.proposed", cell.model_dump(mode="json"))
        return cell

    def record_legal(self, cell: JurisdictionCell, *, legal_record_ref: str, actor: Actor) -> JurisdictionCell:
        if actor.role not in (Role.LEGAL_AGENT, Role.COMPLIANCE_AGENT) or not actor.is_human:
            raise ControlDenied("legal record requires a human Legal or Compliance Agent")
        updated = cell.model_copy(update={"legal_record_ref": legal_record_ref, "legal_signed_by": actor.actor_id})
        self._cells[cell.key] = updated
        self._audit("jurisdiction.legal.recorded", updated.model_dump(mode="json"))
        return updated

    def activate_flag(self, cell: JurisdictionCell, *, actor: Actor, now: datetime) -> JurisdictionCell:
        current = self._cells[cell.key]
        if not actor.is_human:
            raise ControlDenied("technical flag activation requires a human actor")
        if actor.role not in (Role.COMPLIANCE_AGENT, Role.LEGAL_AGENT, Role.COMPLIANCE_ANALYST):
            raise ControlDenied("technical flag activation requires a Compliance or Legal role")
        if not current.legal_record_ref or not current.legal_signed_by:
            raise ControlDenied("technical flag cannot be activated without a signed legal record")
        if actor.actor_id == current.legal_signed_by:
            raise ControlDenied("dual key: flag activator must differ from the legal signer")
        updated = current.model_copy(update={"technical_flag": True, "flag_activated_by": actor.actor_id, "activated_at": now})
        self._cells[cell.key] = updated
        self._audit("jurisdiction.flag.changed", updated.model_dump(mode="json"))
        return updated

    def disable_flag(self, cell: JurisdictionCell, *, actor: Actor, reason: str) -> JurisdictionCell:
        """Single person may disable (ROLLBACK_PLAN); enabling needs dual key."""
        current = self._cells[cell.key]
        updated = current.model_copy(update={"technical_flag": False, "flag_activated_by": None, "activated_at": None})
        self._cells[cell.key] = updated
        self._audit("jurisdiction.flag.changed", {**updated.model_dump(mode="json"), "disabled_by": actor.actor_id, "reason": reason})
        return updated

    def is_live(self, cell: JurisdictionCell) -> bool:
        current = self._cells.get(cell.key)
        return bool(current and current.dual_key_satisfied())
