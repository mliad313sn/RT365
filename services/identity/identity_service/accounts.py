"""Tenants, accounts and the operating-mode state machine [Source: 01; C1 §1].

Promotion is one step at a time and requires the entry criteria of the matching gate; HALTED
is reachable from any mode by any authorised role; leaving HALTED needs two persons from
different lines and a documented reason.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal

from rtcore.errors import ControlDenied, TransitionError
from rtcore.lines import Actor, ActorKind, Role
from rtcore.schemas.account import MODE_LADDER, AccountMode, EmergencyPolicy, TradingStatus
from rtcore.schemas.base import StrictModel

# Gate that authorises entry into each mode [Source: 00, 12; PRODUCT_CHARTER]
MODE_GATE: dict[AccountMode, str | None] = {
    AccountMode.OBSERVE: None,
    AccountMode.BACKTEST: None,  # requires pinned snapshot + pre-registration (strategy_service)
    AccountMode.PAPER: "C",
    AccountMode.SUPERVISED: "D",
    AccountMode.BOUNDED_AUTONOMOUS: "E",
}

MODE_CHANGERS = frozenset(
    {Role.RISK_OFFICER, Role.CHIEF_RISK_AGENT, Role.PORTFOLIO_MANAGER, Role.COMPLIANCE_AGENT, Role.SRE_LEAD, Role.TRADING_DOMAIN_LEAD}
)


class GateRecord(StrictModel):
    gate: str
    passed: bool
    decision_log_ref: str
    iva_verdict: str  # APPROVE | VETO


class Tenant(StrictModel):
    tenant_id: str
    name: str
    residency_region: str
    jurisdiction: str


class Account(StrictModel):
    account_id: str
    tenant_id: str
    customer_id: str
    broker: str
    jurisdiction: str
    customer_type: str
    base_currency: str
    mode: AccountMode = AccountMode.OBSERVE
    enabled_feature: AccountMode | None = None  # compliance-matrix feature cell; unchanged by halts
    trading_status: TradingStatus = TradingStatus.ACTIVE
    emergency_policy: EmergencyPolicy = EmergencyPolicy.CANCEL_ONLY
    liquidation_policy_ref: str | None = None
    capital_envelope: Decimal | None = None
    authorised_strategies: tuple[str, ...] = ()
    autonomy_suspended: bool = False
    pending_unhalt_by: str | None = None
    pending_unhalt_line: str | None = None
    halt_reason: str | None = None


class AccountRegistry:
    """Tenants, accounts and the tenant binding of human principals [Source: 01, 06; NFR-TEN-01].

    The tenant of a principal is a server-side fact recorded here (``bind_principal``), never a claim the
    client asserts; ``tenant_of_principal`` fails closed for an unbound principal (RAID R-22).
    """

    def __init__(self, audit_hook: Callable[[str, str, dict[str, object]], object] | None = None) -> None:
        self._tenants: dict[str, Tenant] = {}
        self._accounts: dict[str, Account] = {}
        self._principals: dict[str, str] = {}
        self._audit = audit_hook or (lambda action, tenant, payload: None)

    def add_tenant(self, tenant: Tenant) -> None:
        self._tenants[tenant.tenant_id] = tenant

    def tenants(self) -> tuple[Tenant, ...]:
        return tuple(self._tenants.values())

    def add_account(self, account: Account) -> None:
        if account.tenant_id not in self._tenants:
            raise ControlDenied("unknown tenant")
        if account.enabled_feature is None:
            account = account.model_copy(update={"enabled_feature": account.mode})
        self._accounts[account.account_id] = account
        self._audit("account.created", account.tenant_id, account.model_dump(mode="json"))

    def get(self, account_id: str) -> Account:
        return self._accounts[account_id]

    def get_in_tenant(self, account_id: str, tenant_id: str) -> Account | None:
        """Tenant-scoped lookup: ``None`` both for a missing account and for another tenant's (no existence leak)."""
        acct = self._accounts.get(account_id)
        if acct is None or acct.tenant_id != tenant_id:
            return None
        return acct

    def accounts(self, tenant_id: str | None = None) -> tuple[Account, ...]:
        return tuple(a for a in self._accounts.values() if tenant_id is None or a.tenant_id == tenant_id)

    # --- principals ---------------------------------------------------------------------------
    def bind_principal(self, actor_id: str, tenant_id: str) -> None:
        """Record the tenant a human principal belongs to (IdP claim in deployment [Open: R-06]; fixture in sim)."""
        if tenant_id not in self._tenants:
            raise ControlDenied("unknown tenant")
        if not actor_id:
            raise ControlDenied("principal id required")
        self._principals[actor_id] = tenant_id
        self._audit("principal.bound", tenant_id, {"actor_id": actor_id, "tenant_id": tenant_id, "correlation_id": f"principal:{actor_id}"})

    def tenant_of_principal(self, actor_id: str) -> str:
        """The bound tenant of a principal; an unbound principal is refused (fail closed), never defaulted."""
        tenant = self._principals.get(actor_id)
        if tenant is None:
            raise ControlDenied("principal is not bound to a tenant")
        return tenant

    def _save(self, account: Account, action: str, extra: dict[str, object]) -> Account:
        self._accounts[account.account_id] = account
        self._audit(action, account.tenant_id, {"account_id": account.account_id, "mode": account.mode.value, **extra})
        return account

    # --- mode transitions -----------------------------------------------------------------
    def promote(
        self, account_id: str, target: AccountMode, actor: Actor, gate: GateRecord | None, *, reason: str, now: datetime
    ) -> Account:
        acct = self._accounts[account_id]
        if not actor.is_human or actor.role not in MODE_CHANGERS:
            raise ControlDenied("mode promotion requires an authorised human; agents cannot change modes")
        if acct.mode == AccountMode.HALTED:
            raise TransitionError("account is HALTED; use restore_from_halt (two-person)")
        if target == AccountMode.HALTED:
            raise TransitionError("use halt() to enter HALTED")
        cur_ix = MODE_LADDER.index(acct.mode)
        tgt_ix = MODE_LADDER.index(target)
        if tgt_ix < cur_ix:
            return self._save(
                acct.model_copy(update={"mode": target, "enabled_feature": target}),
                "account.mode.changed",
                {"from": acct.mode.value, "by": actor.actor_id, "reason": reason, "direction": "demote"},
            )
        if tgt_ix != cur_ix + 1:
            raise TransitionError(f"promotion is one step at a time: {acct.mode.value} -> {target.value} skips a step")
        required = MODE_GATE[target]
        if required is not None:
            if gate is None or gate.gate != required or not gate.passed or gate.iva_verdict != "APPROVE":
                raise ControlDenied(f"entering {target.value} requires Gate {required} passed with IVA APPROVE")
        if target == AccountMode.BOUNDED_AUTONOMOUS and acct.capital_envelope is None:
            raise ControlDenied("bounded autonomy requires a capital envelope")
        return self._save(
            acct.model_copy(update={"mode": target, "enabled_feature": target}),
            "account.mode.changed",
            {"from": acct.mode.value, "by": actor.actor_id, "reason": reason, "gate": gate.gate if gate else None},
        )

    def halt(self, account_id: str, actor: Actor, *, reason: str, now: datetime) -> Account:
        acct = self._accounts[account_id]
        if actor.kind == ActorKind.AGENT:
            raise ControlDenied("agents cannot halt accounts (only humans, runtime monitors or the Kill Switch)")
        if actor.role not in MODE_CHANGERS and actor.role not in (Role.RUNTIME_MONITOR, Role.SYSTEM):
            raise ControlDenied("halt requires an authorised role")
        return self._save(
            acct.model_copy(
                update={"mode": AccountMode.HALTED, "halt_reason": reason, "pending_unhalt_by": None, "pending_unhalt_line": None}
            ),
            "account.halted",
            {"by": actor.actor_id, "reason": reason},
        )

    def restore_from_halt(self, account_id: str, actor: Actor, *, reason: str, now: datetime, target: AccountMode | None = None) -> Account:
        """Two-person rule from different lines. First call records the request; second completes it.

        The restore target can never exceed the feature the account was enabled for (Risk review F-02) and never
        re-enables autonomy: that needs the post-incident review and a normal gate-bound promotion.
        """
        acct = self._accounts[account_id]
        if acct.mode != AccountMode.HALTED:
            raise TransitionError("account is not HALTED")
        if not actor.is_human or actor.role not in MODE_CHANGERS:
            raise ControlDenied("restore requires an authorised human")
        enabled = acct.enabled_feature or AccountMode.OBSERVE
        ceiling = enabled if MODE_LADDER.index(enabled) <= MODE_LADDER.index(AccountMode.SUPERVISED) else AccountMode.SUPERVISED
        if target is None:
            target = ceiling
        if target in (AccountMode.HALTED, AccountMode.BOUNDED_AUTONOMOUS) or MODE_LADDER.index(target) > MODE_LADDER.index(ceiling):
            raise ControlDenied(f"restore target {target.value} exceeds the enabled feature {enabled.value} or re-enables autonomy")
        if acct.pending_unhalt_by is None:
            return self._save(
                acct.model_copy(update={"pending_unhalt_by": actor.actor_id, "pending_unhalt_line": actor.line.value}),
                "account.restore.pending",
                {"first": actor.actor_id, "reason": reason},
            )
        if actor.actor_id == acct.pending_unhalt_by:
            raise ControlDenied("two-person rule: the same person cannot complete the restore")
        if actor.line.value == acct.pending_unhalt_line:
            raise ControlDenied("two-person rule: second person must sit in a different line of defense")
        return self._save(
            acct.model_copy(update={"mode": target, "pending_unhalt_by": None, "pending_unhalt_line": None, "halt_reason": None}),
            "account.restored",
            {"first": acct.pending_unhalt_by, "second": actor.actor_id, "reason": reason},
        )

    def suspend_autonomy(self, account_id: str, *, reason: str, by: str) -> Account:
        acct = self._accounts[account_id]
        updated = acct.model_copy(update={"autonomy_suspended": True})
        if acct.mode == AccountMode.BOUNDED_AUTONOMOUS:
            updated = updated.model_copy(update={"mode": AccountMode.SUPERVISED})
        return self._save(updated, "account.autonomy.suspended", {"reason": reason, "by": by})

    def set_trading_status(self, account_id: str, status: TradingStatus, actor: Actor, *, reason: str) -> Account:
        if not actor.is_human or actor.role not in (Role.RISK_OFFICER, Role.CHIEF_RISK_AGENT, Role.COMPLIANCE_AGENT, Role.TENANT_ADMIN):
            raise ControlDenied("trading status changes require an authorised human")
        acct = self._accounts[account_id]
        return self._save(
            acct.model_copy(update={"trading_status": status}),
            "account.status.changed",
            {"status": status.value, "by": actor.actor_id, "reason": reason},
        )
