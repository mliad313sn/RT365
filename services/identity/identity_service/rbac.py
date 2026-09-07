from __future__ import annotations

from datetime import datetime
from enum import Enum

from rtcore.errors import ControlDenied
from rtcore.lines import Actor, Role
from rtcore.schemas.base import StrictModel


class Permission(str, Enum):
    """The complete permission model. Absent by design: CUSTODY, MONEY_MOVEMENT, MARKET_MAKING,
    COPY_TRADING, PERSONAL_ADVICE [Source: 01; SCOPE.md]."""

    VIEW_DASHBOARD = "view_dashboard"
    SUBMIT_INTENT = "submit_intent"
    APPROVE_ORDER = "approve_order"
    CANCEL_ORDER = "cancel_order"
    PROPOSE_LIMIT = "propose_limit"
    CHECK_LIMIT = "check_limit"
    ACTIVATE_KILL_SWITCH = "activate_kill_switch"
    DEACTIVATE_KILL_SWITCH = "deactivate_kill_switch"
    RESOLVE_BREAK = "resolve_break"
    VIEW_AUDIT = "view_audit"
    EXPORT_AUDIT = "export_audit"
    MANAGE_USERS = "manage_users"
    MANAGE_BROKERS = "manage_brokers"
    RECORD_LEGAL = "record_legal"
    ACTIVATE_JURISDICTION_FLAG = "activate_jurisdiction_flag"
    REGISTER_TOOL = "register_tool"
    CHANGE_MODE = "change_mode"
    VIEW_SUPPORT = "view_support"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.TRADER: frozenset({Permission.VIEW_DASHBOARD, Permission.SUBMIT_INTENT, Permission.APPROVE_ORDER, Permission.CANCEL_ORDER}),
    Role.PORTFOLIO_MANAGER: frozenset(
        {Permission.VIEW_DASHBOARD, Permission.SUBMIT_INTENT, Permission.APPROVE_ORDER, Permission.CANCEL_ORDER, Permission.CHANGE_MODE}
    ),
    Role.RISK_OFFICER: frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.PROPOSE_LIMIT,
            Permission.CHECK_LIMIT,
            Permission.ACTIVATE_KILL_SWITCH,
            Permission.DEACTIVATE_KILL_SWITCH,
            Permission.APPROVE_ORDER,
            Permission.CHANGE_MODE,
            Permission.VIEW_AUDIT,
            Permission.RESOLVE_BREAK,
        }
    ),
    Role.CHIEF_RISK_AGENT: frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.PROPOSE_LIMIT,
            Permission.CHECK_LIMIT,
            Permission.ACTIVATE_KILL_SWITCH,
            Permission.DEACTIVATE_KILL_SWITCH,
            Permission.CHANGE_MODE,
            Permission.VIEW_AUDIT,
            Permission.RESOLVE_BREAK,
        }
    ),
    Role.TRADING_DOMAIN_LEAD: frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.ACTIVATE_KILL_SWITCH,
            Permission.DEACTIVATE_KILL_SWITCH,
            Permission.MANAGE_BROKERS,
            Permission.CHECK_LIMIT,
            Permission.VIEW_AUDIT,
            Permission.RESOLVE_BREAK,
        }
    ),
    Role.COMPLIANCE_AGENT: frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.ACTIVATE_KILL_SWITCH,
            Permission.DEACTIVATE_KILL_SWITCH,
            Permission.RECORD_LEGAL,
            Permission.ACTIVATE_JURISDICTION_FLAG,
            Permission.VIEW_AUDIT,
        }
    ),
    Role.COMPLIANCE_ANALYST: frozenset({Permission.VIEW_DASHBOARD, Permission.ACTIVATE_JURISDICTION_FLAG, Permission.VIEW_AUDIT}),
    Role.LEGAL_AGENT: frozenset({Permission.RECORD_LEGAL, Permission.ACTIVATE_JURISDICTION_FLAG, Permission.VIEW_AUDIT}),
    Role.SRE_LEAD: frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.ACTIVATE_KILL_SWITCH,
            Permission.DEACTIVATE_KILL_SWITCH,
            Permission.VIEW_AUDIT,
            Permission.RESOLVE_BREAK,
        }
    ),
    Role.OPERATIONS_ANALYST: frozenset({Permission.VIEW_DASHBOARD, Permission.RESOLVE_BREAK, Permission.VIEW_AUDIT}),
    Role.TENANT_ADMIN: frozenset({Permission.VIEW_DASHBOARD, Permission.MANAGE_USERS, Permission.MANAGE_BROKERS}),
    Role.AUDITOR: frozenset({Permission.VIEW_AUDIT, Permission.EXPORT_AUDIT}),
    Role.SUPPORT_ENGINEER: frozenset({Permission.VIEW_DASHBOARD, Permission.VIEW_SUPPORT}),
    Role.MCP_SECURITY_AGENT: frozenset({Permission.REGISTER_TOOL, Permission.VIEW_AUDIT}),
    Role.INDEPENDENT_VALIDATION: frozenset({Permission.VIEW_AUDIT, Permission.EXPORT_AUDIT}),
    Role.STRATEGY_AGENT: frozenset({Permission.SUBMIT_INTENT}),
    Role.RUNTIME_MONITOR: frozenset({Permission.ACTIVATE_KILL_SWITCH}),
}


class User(StrictModel):
    user_id: str
    tenant_id: str
    roles: tuple[Role, ...]
    mfa_enrolled: bool = False
    privileged_until: datetime | None = None  # PIM elevation window

    def actor(self, role: Role | None = None) -> Actor:
        chosen = role or self.roles[0]
        if chosen not in self.roles:
            raise ControlDenied(f"user {self.user_id} does not hold role {chosen.value}")
        return Actor(actor_id=self.user_id, role=chosen, tenant_id=self.tenant_id)


PRIVILEGED = frozenset(
    {
        Permission.DEACTIVATE_KILL_SWITCH,
        Permission.CHECK_LIMIT,
        Permission.ACTIVATE_JURISDICTION_FLAG,
        Permission.REGISTER_TOOL,
        Permission.MANAGE_USERS,
        Permission.CHANGE_MODE,
    }
)


def permissions_for(user: User) -> frozenset[Permission]:
    perms: set[Permission] = set()
    for role in user.roles:
        perms |= ROLE_PERMISSIONS.get(role, frozenset())
    return frozenset(perms)


def authorize(user: User, permission: Permission, *, now: datetime, mfa_verified: bool) -> None:
    """RBAC + MFA + PIM: privileged permissions need an active elevation window [Source: 02]."""
    if permission not in permissions_for(user):
        raise ControlDenied(f"{user.user_id} lacks {permission.value}")
    if not user.mfa_enrolled or not mfa_verified:
        raise ControlDenied("MFA required")
    if permission in PRIVILEGED and (user.privileged_until is None or user.privileged_until <= now):
        raise ControlDenied(f"{permission.value} requires an active privileged-access elevation")
