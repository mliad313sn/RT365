from __future__ import annotations

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
    deactivation_first_by: str | None = None
    deactivation_first_line: str | None = None
    deactivated_at: datetime | None = None
    deactivation_reason: str | None = None


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


@dataclass
class KillSwitchService:
    hooks: KillSwitchHooks = field(default_factory=KillSwitchHooks)
    _activations: dict[str, Activation] = field(default_factory=dict)

    # --- activation -------------------------------------------------------------------------
    def activate(
        self, level: KillSwitchLevel, target_id: str, *, reason: str, actor: Actor, now: datetime, correlation_id: str | None = None
    ) -> Activation:
        corr = correlation_id or new_id("ks")
        if actor.kind == ActorKind.AGENT:
            self.hooks.alert("killswitch.agent_attempt", {"actor": actor.actor_id, "level": level.value, "target": target_id})
            self.hooks.audit("killswitch.denied", corr, {"actor": actor.actor_id, "reason": "agents cannot operate the Kill Switch"})
            raise ControlDenied("AI agents cannot activate or deactivate the Kill Switch")
        if actor.role not in KILL_SWITCH_ACTIVATORS:
            self.hooks.audit("killswitch.denied", corr, {"actor": actor.actor_id, "role": actor.role.value})
            raise ControlDenied(f"role {actor.role.value} holds no emergency authority")
        # 1. block new risk: the activation itself is the flag consulted by the risk engine.
        # 2. cancel open orders
        cancelled = tuple(self.hooks.cancel_open_orders(level, target_id))
        # 3. apply emergency policy (CANCEL_ONLY default; reduce/flatten only with approved liquidation policy [Open: O-08])
        policy, liq_ref = self.hooks.emergency_policy_for(level, target_id)
        applied = EmergencyPolicy.CANCEL_ONLY.value
        if policy != EmergencyPolicy.CANCEL_ONLY:
            if liq_ref:
                self.hooks.apply_liquidation(level, target_id, policy, liq_ref)
                applied = f"{policy.value}:{liq_ref}"
            else:
                applied = f"CANCEL_ONLY (fallback: {policy.value} requested without approved liquidation policy)"
        # 4. revoke agent tool tokens
        revoked = tuple(self.hooks.revoke_agent_identities(level, target_id))
        # 5. preserve evidence snapshot
        snapshot = self.hooks.evidence_snapshot(level, target_id)
        evidence = hash_of({"snapshot": snapshot, "cancelled": cancelled, "revoked": revoked, "at": now.isoformat()})
        activation = Activation(
            activation_id=new_id("ksa"),
            level=level,
            target_id=target_id,
            reason=reason,
            actor_id=actor.actor_id,
            actor_role=actor.role.value,
            activated_at=now,
            evidence_hash=evidence,
            emergency_policy_applied=applied,
            cancelled_orders=cancelled,
            revoked_identities=revoked,
        )
        self._activations[activation.activation_id] = activation
        if level == KillSwitchLevel.ACCOUNT:
            self.hooks.halt_account(target_id, reason)
        self.hooks.audit("killswitch.activated", corr, {**activation.model_dump(mode="json"), "evidence_snapshot": snapshot})
        # 6. notify
        self.hooks.notify("killswitch.activated", {"level": level.value, "target": target_id, "reason": reason, "by": actor.actor_id})
        return activation

    # --- deactivation (two-person, different lines) --------------------------------------------
    def deactivate(self, activation_id: str, *, actor: Actor, reason: str, now: datetime) -> Activation:
        act = self._activations[activation_id]
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
            self._activations[activation_id] = updated
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
        self._activations[activation_id] = updated
        self.hooks.audit(
            "killswitch.deactivated",
            activation_id,
            {"first": act.deactivation_first_by, "second": actor.actor_id, "reason": updated.deactivation_reason},
        )
        self.hooks.notify("killswitch.deactivated", {"activation_id": activation_id, "by": [act.deactivation_first_by, actor.actor_id]})
        return updated

    # --- state queries ----------------------------------------------------------------------------
    def active(self) -> tuple[Activation, ...]:
        return tuple(a for a in self._activations.values() if a.active)

    def get(self, activation_id: str) -> Activation:
        return self._activations[activation_id]

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
