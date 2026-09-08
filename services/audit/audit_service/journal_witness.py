"""The audit chain acting as the witness for a control store's journal head [Source: 03, 06; NFR-AUD-01]
/ [Committee: D-061 (5) Option B, ADR-018 amendment 1, ADR-020] / [Open: O-54, O-128, O-133].

This is the whole of the coupling between the two halves of D-061 (5), and it is deliberately one-directional:

* it implements ``rtcore.journal_anchor.JournalWitness``, a three-method protocol declared in the **core library**;
* it writes through ``AuditStore.append`` — the append path that already existed, the only one there is — and it
  reads through ``by_action``. There is no update, no delete and no re-sequencing here, because none exists;
* it never sees a ``Store``, a file, a path or a digest algorithm. It does not know how a journal head is computed
  and cannot recompute one, so the audit service holds no copy of the control store's internals.

Every row it writes carries the correlation id of the control-plane transaction that caused it, so an auditor can
follow one id from a Kill Switch activation to the journal head it moved, to the audit head, to the external
anchor. Rows are platform-level, not customer data: tenant ``"-"`` (the convention ADR-020's own incident rows use).
"""

from __future__ import annotations

from typing import Any

from rtcore.journal_anchor import JOURNAL_ANCHORED, JOURNAL_INCIDENT, JOURNAL_RECOVERED, WitnessRow

from audit_service.store import AuditStore

#: The only actions this adapter will write or read. A caller asking for anything else is a defect, not a feature:
#: the control plane must not be able to append arbitrary audit rows through the anchoring path.
WITNESS_ACTIONS = frozenset({JOURNAL_ANCHORED, JOURNAL_INCIDENT, JOURNAL_RECOVERED})

#: Written on the audit row as the actor. The control store is the subject of the row; the audit service is the
#: recorder. Neither is a person and neither is an agent: no AI/MCP component can reach this path.
CONTROL_STORE_ACTOR = "control_store"


class UnknownWitnessAction(ValueError):
    """An action outside the journal-anchoring vocabulary was offered to the witness (fail closed)."""


class AuditJournalWitness:
    """Adapter: ``rtcore.journal_anchor.JournalWitness`` over an ``AuditStore``."""

    def __init__(self, audit: AuditStore, *, tenant: str = "-", actor: str = CONTROL_STORE_ACTOR) -> None:
        self._audit = audit
        self._tenant = tenant
        self._actor = actor

    def record(self, action: str, payload: dict[str, Any], *, correlation_id: str) -> None:
        if action not in WITNESS_ACTIONS:
            raise UnknownWitnessAction(f"'{action}' is not a journal-anchoring action (fail closed)")
        if not correlation_id:
            raise UnknownWitnessAction("a journal-anchoring row without a correlation_id is refused (fail closed)")
        self._audit.append(
            correlation_id=correlation_id,
            tenant=self._tenant,
            account=None,
            actor=self._actor,
            action=action,
            payload=payload,
        )

    def rows(self, action: str) -> tuple[WitnessRow, ...]:
        if action not in WITNESS_ACTIONS:
            raise UnknownWitnessAction(f"'{action}' is not a journal-anchoring action (fail closed)")
        return tuple(WitnessRow(correlation_id=e.correlation_id, payload=dict(e.payload)) for e in self._audit.by_action(action))

    def verified(self) -> tuple[bool, str]:
        """Whether the chain that carries the witnessed heads verifies against *its own* external anchor.

        This is what makes the two halves one control: a head is only witnessed if the witness is itself witnessed.
        """
        result = self._audit.verify()
        return result.ok, result.reason or result.detail
