"""Backtest & strategy lifecycle [Source: 08; FR-06/FR-08; ADR-008; R-03]."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from conftest import IVA, MODEL_RISK, QUANT, STRATEGY, human
from rtcore.errors import ControlDenied
from rtcore.lines import Role
from strategy_service.registry import PreRegistration, StrategyStatus
from web_bff.platform import run_sim_backtest


@pytest.mark.tc("TC-BT-001")
@pytest.mark.req("FR-08")
@pytest.mark.quartet("positive")
def test_same_snapshot_identical_fills_and_decisions():  # type: ignore[no-untyped-def]
    """Replay determinism: same data snapshot -> identical fills and decisions; report carries the disclaimer."""
    a, b = run_sim_backtest(bars=120), run_sim_backtest(bars=120)
    assert a.fills_hash == b.fills_hash and a.decisions_hash == b.decisions_hash and a.data_snapshot_id == b.data_snapshot_id
    assert a.fills > 0 and a.approved > 0 and "do not prove future profitability" in a.disclaimer
    assert a.metrics.trades >= 1


@pytest.mark.tc("TC-BT-002")
@pytest.mark.req("FR-08")
@pytest.mark.quartet("negative")
def test_cost_sensitivity_runs_change_results():  # type: ignore[no-untyped-def]
    """x1.5 and x2 cost assumptions produce distinct, labelled reports."""
    base, x15, x2 = (
        run_sim_backtest(bars=120),
        run_sim_backtest(bars=120, cost_factor=Decimal("1.5")),
        run_sim_backtest(bars=120, cost_factor=Decimal("2")),
    )
    assert x15.cost_model_version.endswith("x1.5") and x2.cost_model_version.endswith("x2")
    assert base.metrics.total_return_pct >= x15.metrics.total_return_pct >= x2.metrics.total_return_pct


@pytest.mark.tc("TC-BT-003")
@pytest.mark.req("FR-08")
@pytest.mark.quartet("abuse")
def test_look_ahead_is_structurally_impossible(platform):  # type: ignore[no-untyped-def]
    """Reading beyond knowledge time raises; the strategy sees only bars ingested before the decision time."""
    from market_data.store import LookAheadViolation

    store = platform.market.store
    with pytest.raises(LookAheadViolation):
        store.series("SIMEQ1", start=platform.now - timedelta(hours=1), end=platform.now + timedelta(minutes=1), knowledge_ts=platform.now)
    last_bar = store.market_timestamps("SIMEQ1")[-1]
    # the bar at last_bar is ingested 200 ms later: with knowledge time == last_bar it is invisible, one second later it is visible
    invisible = store.latest("SIMEQ1", as_of=last_bar, knowledge_ts=last_bar)
    assert invisible is not None and invisible.market_ts < last_bar
    assert store.latest("SIMEQ1", as_of=last_bar, knowledge_ts=last_bar + timedelta(seconds=1)).market_ts == last_bar


@pytest.mark.tc("TC-BT-004")
@pytest.mark.req("FR-06")
@pytest.mark.quartet("recovery")
def test_strategy_lifecycle_pre_registration_and_segregation(platform):  # type: ignore[no-untyped-def]
    """Unregistered results cannot be recorded; owner cannot validate own strategy; promotion needs gates; rollback retires versions."""
    reg = platform.strategies
    with pytest.raises(ControlDenied):
        reg.promote(STRATEGY, "0.1", StrategyStatus.BACKTESTED, QUANT, now=platform.now, evidence_ref="exploratory")
    pre = PreRegistration(
        hypothesis="fast SMA above slow SMA precedes drift (sim)",
        universe=("SIMEQ1",),
        period_start=platform.now - timedelta(days=3),
        period_end=platform.now,
        split_scheme="train/validation/test 60/20/20 + walk-forward",
        success_criteria="drawdown below limit; no leakage; cost x2 sensitivity",
        registered_at=platform.now,
        registered_by=QUANT.actor_id,
    )
    reg.pre_register(STRATEGY, "0.1", pre, QUANT, data_snapshot_id="ds_fixture")
    reg.promote(STRATEGY, "0.1", StrategyStatus.BACKTESTED, QUANT, now=platform.now, evidence_ref="backtest report")
    with pytest.raises(ControlDenied):
        reg.promote(STRATEGY, "0.1", StrategyStatus.VALIDATED, QUANT, now=platform.now, evidence_ref="self")
    reg.promote(STRATEGY, "0.1", StrategyStatus.VALIDATED, MODEL_RISK, now=platform.now, evidence_ref="validation")
    reg.promote(STRATEGY, "0.1", StrategyStatus.REPRODUCED, IVA, now=platform.now, evidence_ref="iva reproduction")
    reg.promote(STRATEGY, "0.1", StrategyStatus.CHALLENGER, MODEL_RISK, now=platform.now, evidence_ref="MRC minutes")
    reg.promote(STRATEGY, "0.1", StrategyStatus.SHADOW, MODEL_RISK, now=platform.now, evidence_ref="shadow")
    with pytest.raises(ControlDenied):
        reg.promote(STRATEGY, "0.1", StrategyStatus.PAPER, MODEL_RISK, now=platform.now, evidence_ref="no gate")
    reg.promote(STRATEGY, "0.1", StrategyStatus.PAPER, MODEL_RISK, now=platform.now, evidence_ref="gate C", gate_passed="C")
    with pytest.raises(ControlDenied):
        reg.promote(
            STRATEGY,
            "0.1",
            StrategyStatus.SUPERVISED_PILOT,
            human("agentish", Role.TRADER),
            now=platform.now,
            evidence_ref="x",
            gate_passed="D",
        )
    rolled = reg.rollback(STRATEGY, to_version="0.1", actor=MODEL_RISK, now=platform.now, reason="drill")
    assert rolled.version == "0.1" and platform.audit.by_action("strategy.rollback")
    assert reg.get(STRATEGY, "0.1").pre_registration.hypothesis_hash


def test_signal_without_evidence_is_schema_invalid():  # type: ignore[no-untyped-def]
    from pydantic import ValidationError
    from rtcore.schemas.intent import Side
    from strategy_service.signals import Signal
    from web_bff.platform import BASE_TIME

    with pytest.raises(ValidationError):
        Signal(
            strategy_id="s",
            strategy_version="1",
            model_id="m",
            model_version="1",
            instrument_id="SIMEQ1",
            venue="SIMX",
            side=Side.BUY,
            thesis_code="T",
            evidence_refs=(),
            confidence=0.5,
            market_ts=BASE_TIME,
            data_provenance=("simulated",),
            target_notional=Decimal("100"),
        )
