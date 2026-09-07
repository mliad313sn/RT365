"""Three Lines of Defense actor model [Source: 13; Committee Part 1].

Every action that a control evaluates carries an ``Actor``: who, which role, which line, and
whether the actor is a human, an AI agent or a system component. Agents never satisfy a
human-only control [Source: 00].
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class DefenseLine(str, Enum):
    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"


class ActorKind(str, Enum):
    HUMAN = "HUMAN"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


class Role(str, Enum):
    # 1st line
    PRODUCT_OWNER = "product_owner"  # accountable for completeness and executability; docs/PRODUCT_OWNER.md
    PRODUCT_DIRECTOR = "product_director"
    PROGRAM_ORCHESTRATOR = "program_orchestrator"
    TRADING_DOMAIN_LEAD = "trading_domain_lead"
    QUANT_RESEARCH_LEAD = "quant_research_lead"
    BACKEND_LEAD = "backend_lead"
    SRE_LEAD = "sre_lead"
    OPERATIONS_ANALYST = "operations_analyst"
    TRADER = "trader"
    PORTFOLIO_MANAGER = "portfolio_manager"
    TENANT_ADMIN = "tenant_admin"
    SUPPORT_ENGINEER = "support_engineer"
    # 2nd line
    CHIEF_RISK_AGENT = "chief_risk_agent"
    RISK_OFFICER = "risk_officer"
    MODEL_RISK_LEAD = "model_risk_lead"
    COMPLIANCE_AGENT = "compliance_agent"
    COMPLIANCE_ANALYST = "compliance_analyst"
    LEGAL_AGENT = "legal_agent"
    MCP_SECURITY_AGENT = "mcp_security_agent"
    PRIVACY_LEAD = "privacy_lead"
    # 3rd line
    INDEPENDENT_VALIDATION = "independent_validation"
    AUDITOR = "auditor"
    QA_LEAD = "qa_lead"
    RED_TEAM = "red_team"
    # non-human
    STRATEGY_AGENT = "strategy_agent"
    RUNTIME_MONITOR = "runtime_monitor"
    SYSTEM = "system"


ROLE_LINE: dict[Role, DefenseLine] = {
    Role.PRODUCT_OWNER: DefenseLine.FIRST,
    Role.PRODUCT_DIRECTOR: DefenseLine.FIRST,
    Role.PROGRAM_ORCHESTRATOR: DefenseLine.FIRST,
    Role.TRADING_DOMAIN_LEAD: DefenseLine.FIRST,
    Role.QUANT_RESEARCH_LEAD: DefenseLine.FIRST,
    Role.BACKEND_LEAD: DefenseLine.FIRST,
    Role.SRE_LEAD: DefenseLine.FIRST,
    Role.OPERATIONS_ANALYST: DefenseLine.FIRST,
    Role.TRADER: DefenseLine.FIRST,
    Role.PORTFOLIO_MANAGER: DefenseLine.FIRST,
    Role.TENANT_ADMIN: DefenseLine.FIRST,
    Role.SUPPORT_ENGINEER: DefenseLine.FIRST,
    Role.CHIEF_RISK_AGENT: DefenseLine.SECOND,
    Role.RISK_OFFICER: DefenseLine.SECOND,
    Role.MODEL_RISK_LEAD: DefenseLine.SECOND,
    Role.COMPLIANCE_AGENT: DefenseLine.SECOND,
    Role.COMPLIANCE_ANALYST: DefenseLine.SECOND,
    Role.LEGAL_AGENT: DefenseLine.SECOND,
    Role.MCP_SECURITY_AGENT: DefenseLine.SECOND,
    Role.PRIVACY_LEAD: DefenseLine.SECOND,
    Role.INDEPENDENT_VALIDATION: DefenseLine.THIRD,
    Role.AUDITOR: DefenseLine.THIRD,
    Role.QA_LEAD: DefenseLine.THIRD,
    Role.RED_TEAM: DefenseLine.THIRD,
    Role.STRATEGY_AGENT: DefenseLine.FIRST,
    Role.RUNTIME_MONITOR: DefenseLine.FIRST,
    Role.SYSTEM: DefenseLine.FIRST,
}

# Emergency authority [Committee, C11]: any one of these may *activate* the Kill Switch.
KILL_SWITCH_ACTIVATORS: frozenset[Role] = frozenset(
    {
        Role.SRE_LEAD,
        Role.CHIEF_RISK_AGENT,
        Role.RISK_OFFICER,
        Role.COMPLIANCE_AGENT,
        Role.TRADING_DOMAIN_LEAD,
        Role.RUNTIME_MONITOR,
    }
)

# Roles that may approve an intent in the approval queue (maker != checker enforced separately).
APPROVERS: frozenset[Role] = frozenset({Role.TRADER, Role.PORTFOLIO_MANAGER, Role.RISK_OFFICER})


class Actor(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    actor_id: str
    role: Role
    kind: ActorKind = ActorKind.HUMAN
    tenant_id: str | None = None

    @property
    def line(self) -> DefenseLine:
        return ROLE_LINE[self.role]

    @property
    def is_human(self) -> bool:
        return self.kind == ActorKind.HUMAN


def system_actor(component: str) -> Actor:
    return Actor(actor_id=component, role=Role.SYSTEM, kind=ActorKind.SYSTEM)
