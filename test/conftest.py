from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from rtcore.lines import Actor, ActorKind, Role
from rtcore.schemas.account import AccountMode
from web_bff.platform import ACCOUNT, BASE_TIME, INSTRUMENT, INSTRUMENT_2, STRATEGY, TENANT, VENUE, SimPlatform, build_sim_platform

__all__ = ["ACCOUNT", "BASE_TIME", "INSTRUMENT", "INSTRUMENT_2", "STRATEGY", "TENANT", "VENUE"]


@pytest.fixture
def platform() -> SimPlatform:
    return build_sim_platform()


@pytest.fixture
def supervised() -> SimPlatform:
    return build_sim_platform(mode=AccountMode.SUPERVISED)


@pytest.fixture
def autonomous() -> SimPlatform:
    return build_sim_platform(mode=AccountMode.BOUNDED_AUTONOMOUS)


def human(actor_id: str, role: Role) -> Actor:
    return Actor(actor_id=actor_id, role=role, kind=ActorKind.HUMAN, tenant_id=TENANT)


def agent(actor_id: str = "agent-sim-1") -> Actor:
    return Actor(actor_id=actor_id, role=Role.STRATEGY_AGENT, kind=ActorKind.AGENT, tenant_id=TENANT)


RISK_OFFICER = human("risk.officer.1", Role.RISK_OFFICER)  # 2nd line
CHIEF_RISK = human("chief.risk", Role.CHIEF_RISK_AGENT)  # 2nd line
SRE = human("sre.lead", Role.SRE_LEAD)  # 1st line
TRADING_LEAD = human("trading.lead", Role.TRADING_DOMAIN_LEAD)  # 1st line
COMPLIANCE = human("compliance.agent", Role.COMPLIANCE_AGENT)  # 2nd line
LEGAL = human("legal.agent", Role.LEGAL_AGENT)  # 2nd line
TRADER = human("trader.1", Role.TRADER)  # 1st line
PM = human("pm.1", Role.PORTFOLIO_MANAGER)  # 1st line
OPS = human("ops.1", Role.OPERATIONS_ANALYST)  # 1st line
AUDITOR = human("auditor.1", Role.AUDITOR)  # 3rd line
IVA = human("iva.1", Role.INDEPENDENT_VALIDATION)  # 3rd line
QUANT = human("quant.fixture", Role.QUANT_RESEARCH_LEAD)  # 1st line (strategy owner)
MODEL_RISK = human("model.risk", Role.MODEL_RISK_LEAD)  # 2nd line


def resting_limit_intent(p: SimPlatform, **overrides: object) -> dict[str, object]:
    """A LIMIT buy far below the reference: stays open at the broker (used for cancel/kill-switch tests)."""
    snap = p.market_snapshot(INSTRUMENT)
    assert snap is not None
    price = (snap.reference_price * Decimal("0.96")).quantize(Decimal("0.01"))
    base = p.make_intent(
        order_type="LIMIT",
        limit_price=str(price),
        time_in_force="GTC",
        quantity="10",
        protective_stop=str((price * Decimal("0.98")).quantize(Decimal("0.01"))),
    )
    base.update(overrides)
    return base


def later(p: SimPlatform, seconds: float) -> datetime:
    return p.now + timedelta(seconds=seconds)
