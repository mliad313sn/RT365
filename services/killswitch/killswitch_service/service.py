from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from rtcore.errors import ControlDenied
from rtcore.ids import hash_of, new_id
from rtcore.lines import KILL_SWITCH_ACTIVATORS, Actor, ActorKind
from rtcore.schemas.account import EmergencyPolicy, KillSwitchFlags
from rtcore.schemas.base import StrictModel
from rtcore.store import MemoryStore, Store


class KillSwitchLevel(str, Enum):
    PLATFORM = "PLATFORM"
    TENANT = "TENANT"
    ACCOUNT = "ACCOUNT"
    STRATEGY = "STRATEGY"
    ASSET = "ASSET"
    VENUE = "VENUE"


class Activation(StrictModel):
    activation_id: str
    level: KillSwitchLevel
    target_id: str
    reason: str
    actor_id: str
    actor_role: str
    activated_at: datetime
    evidence_hash: str
    emergency_policy_applied: str
    cancelled_orders: tuple[str, ...]
    revoked_identities: tuple[str, ...]
    active: bool = True
    hook_failures: tuple[str, ...] = ()  # a failed side effect never un-engages the switch (review OBJ-1)
    deactivation_first_by: str | None = None
    deactivation_first_line: str | None = None
    deactivated_at: datetime | None = None
    deactivation_reason: str | None = None
    # Time-to-halt measurement path (D-044, O-64): engage -> last cancel/revocation, wall clock of the process.
    engaged_at: datetime | None = None
    halt_elapsed_ms: int | None = None


@dataclass
class KillSwitchHooks:
    """Side effects executed on activation (P4). Each is injected so the service stays testable."""

    cancel_open_orders: Callable[[KillSwitchLevel, str], list[str]] = lambda level, target: []
    revoke_agent_identities: Callable[[KillSwitchLevel, str], list[str]] = lambda level, target: []
    emergency_policy_for: Callable[[KillSwitchLevel, str], tuple[EmergencyPolicy, str | None]] = lambda level, target: (
        EmergencyPolicy.CANCEL_ONLY,
        None,
    )
    apply_liquidation: Callable[[KillSwitchLevel, str, EmergencyPolicy, str], object] = lambda level, target, policy, ref: None
    evidence_snapshot: Callable[[KillSwitchLevel, str], dict[str, Any]] = lambda level, target: {}
    notify: Callable[[str, dict[str, Any]], object] = lambda subject, payload: None
    audit: Callable[[str, str, dict[str, Any]], object] = lambda action, correlation_id, payload: None
    alert: Callable[[str, dict[str, Any]], object] = lambda name, payload: None
    halt_account: Callable[[str, str], object] = lambda account_id, reason: None
    observe: Callable[[str, float], object] = lambda name, value: None  # metrics sink for time_to_halt_s (SLI catalogue)


@dataclass
class KillSwitchService:
    hooks: KillSwitchHooks = field(default_factory=KillSwitchHooks)
    approved_liquidation_policies: tuple[str, ...] = ()  # [Open: O-08] registry of Trading-Risk-Committee-approved policies
    # Activations live behind the store seam (ADR-010): memory by default, SQLite with store_dir, so an engaged switch
    # at any level survives a restart and is the flag the risk engine and the gateway oracle consult (R-23, R-05).
    store: Store = field(default_factory=MemoryStore)
    table: str = "killswitch.activations"

    def _put(self, activation: Activation, correlation_id: str) -> Activation:
        self.store.put(self.table, activation.activation_id, activation.model_dump_json(), correlation_id=correlation_id)
        return activation

    def _all(self) -> tuple[Activation, ...]:
        return tuple(Activation.model_validate_json(raw) for _key, raw in self.store.items(self.table))

    # --- activation -------------------------------------------------------------------------
    def activate(
        self, level: KillSwitchLevel, target_id: str, *, reason: str, actor: Actor, now: datetime, correlation_id: str | None = None
    ) -> Activation:
        corr = correlation_id or new_id("ks")
        started = time.perf_counter()  # measurement only; never a decision input
        if actor.kind == ActorKind.AGENT:
            self.hooks.alert("killswitch.agent_attempt", {"actor": actor.actor_id, "level": level.value, "target": target_id})
            self.hooks.audit("killswitch.denied", corr, {"actor": actor.actor_id, "reason": "agents cannot operate the Kill Switch"})
            raise ControlDenied("AI agents cannot activate or deactivate the Kill Switch")
        if actor.role not in KILL_SWITCH_ACTIVATORS:
            self.hooks.audit("killswitch.denied", corr, {"actor": actor.actor_id, "role": actor.role.value})
            raise ControlDenied(f"role {actor.role.value} holds no emergency authority")
        # 1. Engage first (fail closed): the stored activation is the flag the risk engine consults; every side
        #    effect below is best-effort, recorded, alerted — a failing hook can never leave the switch disengaged.
        activation = Activation(
            activation_id=new_id("ksa"),
            level=level,
            target_id=target_id,
            reason=reason,
            actor_id=actor.actor_id,
            actor_role=actor.role.value,
            activated_at=now,
            evidence_hash="pending",
            emergency_policy_applied="pending",
            cancelled_orders=(),
            revoked_identities=(),
        )
        self._put(activation, corr)
        self.hooks.audit(
            "killswitch.engaged",
            corr,
            {"activation_id": activation.activation_id, "level": level.value, "target": target_id, "by": actor.actor_id, "reason": reason},
        )
        failures: list[str] = []

        def attempt(name: str, fn: Callable[[], Any], default: Any) -> Any:
            try:
                return fn()
            except Exception as exc:  # noqa: BLE001 - hook failures are evidence, not exits
                failures.append(f"{name}: {type(exc).__name__}: {exc}"[:200])
                self.hooks.alert(
                    "killswitch.hook_failed", {"activation_id": activation.activation_id, "hook": name, "error": type(exc).__name__}
                )
                return default

        # 2. cancel open orders
        cancelled = tuple(attempt("cancel_open_orders", lambda: self.hooks.cancel_open_orders(level, target_id), []))
        # 3. apply emergency policy (CANCEL_ONLY default; reduce/flatten only with an approved liquidation policy [Open: O-08])
        policy, liq_ref = attempt(
            "emergency_policy_for", lambda: self.hooks.emergency_policy_for(level, target_id), (EmergencyPolicy.CANCEL_ONLY, None)
        )
        applied = EmergencyPolicy.CANCEL_ONLY.value
        if policy != EmergencyPolicy.CANCEL_ONLY:
            if liq_ref and liq_ref in self.approved_liquidation_policies:
                attempt("apply_liquidation", lambda: self.hooks.apply_liquidation(level, target_id, policy, liq_ref), None)
                applied = f"{policy.value}:{liq_ref}"
            else:
                applied = f"CANCEL_ONLY (fallback: {policy.value} requested; liquidation policy {liq_ref!r} not approved)"
        # 4. revoke agent tool tokens
        revoked = tuple(attempt("revoke_agent_identities", lambda: self.hooks.revoke_agent_identities(level, target_id), []))
        # 5. preserve evidence snapshot
        snapshot = attempt("evidence_snapshot", lambda: self.hooks.evidence_snapshot(level, target_id), {})
        evidence = hash_of({"snapshot": snapshot, "cancelled": cancelled, "revoked": revoked, "at": now.isoformat()})
        halt_elapsed_ms = int((time.perf_counter() - started) * 1000)
        activation = activation.model_copy(
            update={
                "evidence_hash": evidence,
                "emergency_policy_applied": applied,
                "cancelled_orders": cancelled,
                "revoked_identities": revoked,
                "hook_failures": tuple(failures),
                "engaged_at": now,
                "halt_elapsed_ms": halt_elapsed_ms,
            }
        )
        attempt("observe", lambda: self.hooks.observe("killswitch.time_to_halt_s", halt_elapsed_ms / 1000.0), None)
        self._put(activation, corr)
        if level == KillSwitchLevel.ACCOUNT:
            attempt("halt_account", lambda: self.hooks.halt_account(target_id, reason), None)
        self.hooks.audit("killswitch.activated", corr, {**activation.model_dump(mode="json"), "evidence_snapshot": snapshot})
        # 6. notify
        attempt(
            "notify",
            lambda: self.hooks.notify(
                "killswitch.activated",
                {"level": level.value, "target": target_id, "reason": reason, "by": actor.actor_id, "hook_failures": failures},
            ),
            None,
        )
        return self.get(activation.activation_id)

    # --- deactivation (two-person, different lines) --------------------------------------------
    def deactivate(self, activation_id: str, *, actor: Actor, reason: str, now: datetime) -> Activation:
        act = self.get(activation_id)
        if not act.active:
            raise ControlDenied("activation already deactivated")
        if actor.kind != ActorKind.HUMAN:
            self.hooks.alert("killswitch.agent_attempt", {"actor": actor.actor_id, "action": "deactivate"})
            raise ControlDenied("only humans may deactivate the Kill Switch")
        if actor.role not in KILL_SWITCH_ACTIVATORS:
            raise ControlDenied(f"role {actor.role.value} holds no emergency authority")
        if act.deactivation_first_by is None:
            updated = act.model_copy(
                update={"deactivation_first_by": actor.actor_id, "deactivation_first_line": actor.line.value, "deactivation_reason": reason}
            )
            self._put(updated, activation_id)
            self.hooks.audit(
                "killswitch.deactivation.pending", activation_id, {"first": actor.actor_id, "line": actor.line.value, "reason": reason}
            )
            return updated
        if actor.actor_id == act.deactivation_first_by:
            raise ControlDenied("two-person rule: the same person cannot complete the deactivation")
        if actor.line.value == act.deactivation_first_line:
            raise ControlDenied("two-person rule: second person must sit in a different line of defense")
        updated = act.model_copy(
            update={"active": False, "deactivated_at": now, "deactivation_reason": f"{act.deactivation_reason} | {reason}"}
        )
        self._put(updated, activation_id)
        self.hooks.audit(
            "killswitch.deactivated",
            activation_id,
            {"first": act.deactivation_first_by, "second": actor.actor_id, "reason": updated.deactivation_reason},
        )
        self.hooks.notify("killswitch.deactivated", {"activation_id": activation_id, "by": [act.deactivation_first_by, actor.actor_id]})
        return updated

    # --- state queries ----------------------------------------------------------------------------
    def active(self) -> tuple[Activation, ...]:
        return tuple(a for a in self._all() if a.active)

    def get(self, activation_id: str) -> Activation:
        raw = self.store.get(self.table, activation_id)
        if raw is None:
            raise KeyError(activation_id)
        return Activation.model_validate_json(raw)

    def flags_for(self, *, tenant_id: str, account_id: str, asset_classes: tuple[str, ...] = ()) -> KillSwitchFlags:
        active = self.active()
        return KillSwitchFlags(
            platform=any(a.level == KillSwitchLevel.PLATFORM for a in active),
            tenant=any(a.level == KillSwitchLevel.TENANT and a.target_id == tenant_id for a in active),
            account=any(a.level == KillSwitchLevel.ACCOUNT and a.target_id == account_id for a in active),
            strategies=tuple(sorted({a.target_id for a in active if a.level == KillSwitchLevel.STRATEGY})),
            assets=tuple(sorted({a.target_id for a in active if a.level == KillSwitchLevel.ASSET})),
            venues=tuple(sorted({a.target_id for a in active if a.level == KillSwitchLevel.VENUE})),
        )

    def blocks(self, *, tenant_id: str, account_id: str, strategy_id: str, instrument_id: str, asset_class: str, venue: str) -> bool:
        f = self.flags_for(tenant_id=tenant_id, account_id=account_id)
        return (
            f.platform
            or f.tenant
            or f.account
            or strategy_id in f.strategies
            or instrument_id in f.assets
            or asset_class in f.assets
            or venue in f.venues
        )
