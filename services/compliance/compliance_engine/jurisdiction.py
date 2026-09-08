"""Dual-key market enablement [Source: 07; C6 §1; P5].

A cell is live only when (a) a signed legal record exists and (b) the technical flag is
activated by a *different* person. Either alone is insufficient. Disabling is single-person.
The legal record is a typed, hashed reference (LegalRecordRef); a free string is refused
(council P-2, O-71). Every audit row about a cell carries the cell's deterministic correlation_id.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from pydantic import ValidationError
from rtcore.errors import ControlDenied
from rtcore.lines import Actor, Role
from rtcore.schemas.compliance import CustomerType, JurisdictionCell, LegalRecordRef
from rtcore.world import is_user_assigned, is_valid_country


class JurisdictionRegistry:
    def __init__(self, audit_hook: Callable[[str, dict[str, object]], object] | None = None) -> None:
        self._cells: dict[tuple[str, str, str, str, str, str], JurisdictionCell] = {}
        self._audit = audit_hook or (lambda action, payload: None)

    def cells(self) -> tuple[JurisdictionCell, ...]:
        return tuple(self._cells.values())

    def _emit(self, action: str, cell: JurisdictionCell, **extra: object) -> None:
        self._audit(action, {**cell.model_dump(mode="json"), "correlation_id": cell.correlation_id, **extra})

    def _stored(self, cell: JurisdictionCell) -> JurisdictionCell:
        current = self._cells.get(cell.key)
        if current is None:
            raise ControlDenied(f"cell {cell.correlation_id} was never proposed; nothing to record against (fail closed)")
        return current

    def propose(
        self,
        *,
        country: str,
        customer_type: CustomerType,
        broker: str,
        venue: str,
        asset_class: str,
        feature: str,
        required_disclosure_version: str | None = None,
    ) -> JurisdictionCell:
        # Global compatibility (D-050): any ISO 3166-1 country on any continent is proposable; a user-assigned code is
        # a simulated cell; anything else is refused. Proposing never enables (dual key below).
        if is_valid_country(country):
            simulated = False
        elif is_user_assigned(country):
            simulated = True
        else:
            raise ControlDenied(f"{country!r} is not an ISO 3166-1 alpha-2 country code nor a user-assigned (simulated) code")
        cell = JurisdictionCell(
            country=country,
            customer_type=customer_type,
            broker=broker,
            venue=venue,
            asset_class=asset_class,
            feature=feature,
            simulated=simulated,
            required_disclosure_version=required_disclosure_version,
        )
        self._cells[cell.key] = cell
        self._emit("jurisdiction.cell.proposed", cell)
        return cell

    def record_legal(self, cell: JurisdictionCell, *, legal_record_ref: LegalRecordRef, actor: Actor) -> JurisdictionCell:
        # Dual key spans two functions: Legal signs the record, Compliance activates the flag (goals/07, goals/08;
        # council finding F-1 2026-09-08). Two Compliance hands, an agent or the Product Owner never satisfy it.
        if actor.role != Role.LEGAL_AGENT or not actor.is_human:
            raise ControlDenied("legal record requires a human Legal Agent")
        # The record is a typed reference (id, signing entity, date, document hash); a string or a dict is refused (P-2, O-71).
        if not isinstance(legal_record_ref, LegalRecordRef):
            raise ControlDenied("legal record must be a typed LegalRecordRef (record id, signing entity, date, document hash)")
        current = self._stored(cell)
        if legal_record_ref.simulated != current.simulated:
            raise ControlDenied(
                "legal record label mismatch: a SIM- record is valid only on a simulated cell, and a simulated cell carries only SIM- records"
            )
        try:
            updated = JurisdictionCell.model_validate(
                {**current.model_dump(), "legal_record_ref": legal_record_ref, "legal_signed_by": actor.actor_id}
            )
        except ValidationError as exc:
            raise ControlDenied(f"legal record refused: {exc.errors()[0].get('msg', 'invalid')}") from exc
        self._cells[cell.key] = updated
        self._emit("jurisdiction.legal.recorded", updated)
        return updated

    def activate_flag(self, cell: JurisdictionCell, *, actor: Actor, now: datetime) -> JurisdictionCell:
        current = self._stored(cell)
        if not actor.is_human:
            raise ControlDenied("technical flag activation requires a human actor")
        if actor.role not in (Role.COMPLIANCE_AGENT, Role.COMPLIANCE_ANALYST):
            raise ControlDenied("technical flag activation requires a human Compliance role (the legal record is Legal's hand)")
        if current.legal_record_ref is None or not current.legal_signed_by:
            raise ControlDenied("technical flag cannot be activated without a signed legal record")
        if actor.actor_id == current.legal_signed_by:
            raise ControlDenied("dual key: flag activator must differ from the legal signer")
        updated = current.model_copy(update={"technical_flag": True, "flag_activated_by": actor.actor_id, "activated_at": now})
        self._cells[cell.key] = updated
        self._emit("jurisdiction.flag.changed", updated)
        return updated

    def disable_flag(self, cell: JurisdictionCell, *, actor: Actor, reason: str) -> JurisdictionCell:
        """Single *human* Compliance/Legal person may disable (ROLLBACK_PLAN); enabling needs dual key; agents never."""
        if not actor.is_human or actor.role not in (Role.COMPLIANCE_AGENT, Role.LEGAL_AGENT, Role.COMPLIANCE_ANALYST):
            raise ControlDenied("flag disable requires a human Compliance or Legal role")
        current = self._stored(cell)
        updated = current.model_copy(update={"technical_flag": False, "flag_activated_by": None, "activated_at": None})
        self._cells[cell.key] = updated
        self._emit("jurisdiction.flag.changed", updated, disabled_by=actor.actor_id, reason=reason)
        return updated

    def is_live(self, cell: JurisdictionCell) -> bool:
        current = self._cells.get(cell.key)
        return bool(current and current.dual_key_satisfied())
