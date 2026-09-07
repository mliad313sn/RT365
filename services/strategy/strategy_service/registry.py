from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Any

from compliance_engine.surveillance import StrategyDeclaration, screen_strategy_declaration
from rtcore.errors import ControlDenied
from rtcore.ids import hash_of
from rtcore.lines import Actor, Role
from rtcore.schemas.base import StrictModel
from rtcore.statemachine import MonotonicStateMachine


class StrategyStatus(str, Enum):
    PROPOSED = "PROPOSED"
    PRE_REGISTERED = "PRE_REGISTERED"
    BACKTESTED = "BACKTESTED"
    VALIDATED = "VALIDATED"  # Model Risk validation (leakage, stability, cost sensitivity)
    REPRODUCED = "REPRODUCED"  # IVA independent reproduction
    CHALLENGER = "CHALLENGER"  # MRC approval
    SHADOW = "SHADOW"
    PAPER = "PAPER"
    SUPERVISED_PILOT = "SUPERVISED_PILOT"
    CAPPED_AUTONOMOUS = "CAPPED_AUTONOMOUS"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


_T = {
    StrategyStatus.PROPOSED: {StrategyStatus.PRE_REGISTERED, StrategyStatus.REJECTED},
    StrategyStatus.PRE_REGISTERED: {StrategyStatus.BACKTESTED, StrategyStatus.REJECTED},
    StrategyStatus.BACKTESTED: {StrategyStatus.VALIDATED, StrategyStatus.REJECTED},
    StrategyStatus.VALIDATED: {StrategyStatus.REPRODUCED, StrategyStatus.REJECTED},
    StrategyStatus.REPRODUCED: {StrategyStatus.CHALLENGER, StrategyStatus.REJECTED},
    StrategyStatus.CHALLENGER: {StrategyStatus.SHADOW, StrategyStatus.RETIRED},
    StrategyStatus.SHADOW: {StrategyStatus.PAPER, StrategyStatus.RETIRED},
    StrategyStatus.PAPER: {StrategyStatus.SUPERVISED_PILOT, StrategyStatus.RETIRED},
    StrategyStatus.SUPERVISED_PILOT: {StrategyStatus.CAPPED_AUTONOMOUS, StrategyStatus.RETIRED},
    StrategyStatus.CAPPED_AUTONOMOUS: {StrategyStatus.RETIRED, StrategyStatus.SUPERVISED_PILOT},
}
LIFECYCLE: MonotonicStateMachine[StrategyStatus] = MonotonicStateMachine(
    {k: frozenset(v) for k, v in _T.items()}, frozenset({StrategyStatus.RETIRED, StrategyStatus.REJECTED})
)

# Who may move a strategy into each status (segregation: owner never validates own work)
PROMOTER: dict[StrategyStatus, frozenset[Role]] = {
    StrategyStatus.PRE_REGISTERED: frozenset({Role.QUANT_RESEARCH_LEAD}),
    StrategyStatus.BACKTESTED: frozenset({Role.QUANT_RESEARCH_LEAD}),
    StrategyStatus.VALIDATED: frozenset({Role.MODEL_RISK_LEAD}),
    StrategyStatus.REPRODUCED: frozenset({Role.INDEPENDENT_VALIDATION}),
    StrategyStatus.CHALLENGER: frozenset({Role.MODEL_RISK_LEAD}),
    StrategyStatus.SHADOW: frozenset({Role.MODEL_RISK_LEAD}),
    StrategyStatus.PAPER: frozenset({Role.MODEL_RISK_LEAD, Role.CHIEF_RISK_AGENT}),
    StrategyStatus.SUPERVISED_PILOT: frozenset({Role.MODEL_RISK_LEAD, Role.CHIEF_RISK_AGENT}),
    StrategyStatus.CAPPED_AUTONOMOUS: frozenset({Role.CHIEF_RISK_AGENT}),
    StrategyStatus.RETIRED: frozenset({Role.MODEL_RISK_LEAD, Role.CHIEF_RISK_AGENT}),
    StrategyStatus.REJECTED: frozenset({Role.MODEL_RISK_LEAD, Role.COMPLIANCE_AGENT}),
}
GATE_FOR: dict[StrategyStatus, str] = {
    StrategyStatus.PAPER: "C",
    StrategyStatus.SUPERVISED_PILOT: "D",
    StrategyStatus.CAPPED_AUTONOMOUS: "E",
}


class PreRegistration(StrictModel):
    """Hypothesis, universe, split and success criteria registered before any backtest runs [C7 §4]."""

    hypothesis: str
    universe: tuple[str, ...]
    period_start: datetime
    period_end: datetime
    split_scheme: str
    success_criteria: str
    registered_at: datetime
    registered_by: str

    @property
    def hypothesis_hash(self) -> str:
        return hash_of(self.model_dump(mode="json"))[:16]


class StrategyVersion(StrictModel):
    strategy_id: str
    version: str
    owner_id: str
    model_id: str
    model_version: str
    params: dict[str, Any]
    declaration: StrategyDeclaration
    status: StrategyStatus
    pre_registration: PreRegistration | None = None
    data_snapshot_id: str | None = None
    approvals: tuple[tuple[str, str, str], ...] = ()  # (status, actor, iso ts)
    docs: str = ""


class StrategyRegistry:
    def __init__(self, audit: Callable[[str, dict[str, object]], object] | None = None) -> None:
        self._versions: dict[tuple[str, str], StrategyVersion] = {}
        self._audit = audit or (lambda action, payload: None)

    def register(self, sv: StrategyVersion) -> StrategyVersion:
        reasons = screen_strategy_declaration(sv.declaration)
        if reasons:
            rejected = sv.model_copy(update={"status": StrategyStatus.REJECTED})
            self._versions[(sv.strategy_id, sv.version)] = rejected
            self._audit("strategy.rejected", {"strategy_id": sv.strategy_id, "version": sv.version, "reasons": list(reasons)})
            raise ControlDenied(f"strategy declaration rejected at registration: {','.join(reasons)}")
        stored = sv.model_copy(update={"status": StrategyStatus.PROPOSED})
        self._versions[(sv.strategy_id, sv.version)] = stored
        self._audit("strategy.registered", {"strategy_id": sv.strategy_id, "version": sv.version})
        return stored

    def get(self, strategy_id: str, version: str) -> StrategyVersion:
        return self._versions[(strategy_id, version)]

    def versions(self, strategy_id: str) -> tuple[StrategyVersion, ...]:
        return tuple(v for (sid, _), v in self._versions.items() if sid == strategy_id)

    def pre_register(self, strategy_id: str, version: str, pre: PreRegistration, actor: Actor, *, data_snapshot_id: str) -> StrategyVersion:
        sv = self.get(strategy_id, version)
        if actor.role != Role.QUANT_RESEARCH_LEAD or actor.actor_id != sv.owner_id:
            raise ControlDenied("pre-registration is done by the owning quant")
        LIFECYCLE.assert_transition(sv.status, StrategyStatus.PRE_REGISTERED)
        updated = sv.model_copy(
            update={"status": StrategyStatus.PRE_REGISTERED, "pre_registration": pre, "data_snapshot_id": data_snapshot_id}
        )
        self._versions[(strategy_id, version)] = updated
        self._audit(
            "strategy.pre_registered",
            {"strategy_id": strategy_id, "version": version, "hypothesis_hash": pre.hypothesis_hash, "data_snapshot_id": data_snapshot_id},
        )
        return updated

    def promote(
        self,
        strategy_id: str,
        version: str,
        target: StrategyStatus,
        actor: Actor,
        *,
        now: datetime,
        evidence_ref: str,
        gate_passed: str | None = None,
    ) -> StrategyVersion:
        sv = self.get(strategy_id, version)
        if not actor.is_human:
            raise ControlDenied("agents cannot change strategy status")
        if actor.role not in PROMOTER.get(target, frozenset()):
            raise ControlDenied(f"role {actor.role.value} cannot move a strategy to {target.value}")
        if target in (StrategyStatus.VALIDATED, StrategyStatus.REPRODUCED, StrategyStatus.CHALLENGER) and actor.actor_id == sv.owner_id:
            raise ControlDenied("owner cannot validate, reproduce or approve their own strategy")
        if target == StrategyStatus.BACKTESTED and sv.pre_registration is None:
            raise ControlDenied("unregistered results are exploratory only and cannot be recorded")
        required_gate = GATE_FOR.get(target)
        if required_gate is not None and gate_passed != required_gate:
            raise ControlDenied(f"{target.value} requires Gate {required_gate} passed")
        LIFECYCLE.assert_transition(sv.status, target)
        updated = sv.model_copy(update={"status": target, "approvals": (*sv.approvals, (target.value, actor.actor_id, now.isoformat()))})
        self._versions[(strategy_id, version)] = updated
        self._audit(
            "strategy.status.changed",
            {"strategy_id": strategy_id, "version": version, "status": target.value, "by": actor.actor_id, "evidence": evidence_ref},
        )
        return updated

    def rollback(self, strategy_id: str, *, to_version: str, actor: Actor, now: datetime, reason: str) -> StrategyVersion:
        if actor.role not in (Role.MODEL_RISK_LEAD, Role.CHIEF_RISK_AGENT):
            raise ControlDenied("rollback requires Model Risk or Chief Risk")
        target = self.get(strategy_id, to_version)
        for (sid, ver), v in list(self._versions.items()):
            if (
                sid == strategy_id
                and ver != to_version
                and v.status
                in (
                    StrategyStatus.PAPER,
                    StrategyStatus.SUPERVISED_PILOT,
                    StrategyStatus.CAPPED_AUTONOMOUS,
                    StrategyStatus.SHADOW,
                    StrategyStatus.CHALLENGER,
                )
            ):
                self._versions[(sid, ver)] = v.model_copy(
                    update={"status": StrategyStatus.RETIRED, "approvals": (*v.approvals, ("RETIRED", actor.actor_id, now.isoformat()))}
                )
        self._audit("strategy.rollback", {"strategy_id": strategy_id, "to_version": to_version, "by": actor.actor_id, "reason": reason})
        return target

    def docs_for(self, strategy_id: str) -> str:
        parts = []
        for v in self.versions(strategy_id):
            parts.append(f"{v.strategy_id} v{v.version} [{v.status.value}] model={v.model_id}@{v.model_version}\n{v.docs}")
        return "\n\n".join(parts) if parts else "no documentation registered"
