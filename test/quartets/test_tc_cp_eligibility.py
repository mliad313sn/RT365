"""TC-CP — Compliance eligibility & dual-key market enablement [Source: 07; FR-15; C6]."""

from __future__ import annotations

from datetime import timedelta

import pytest
from compliance_engine.eligibility import decide_eligibility
from compliance_engine.retention import LegalHold, RetentionSchedule
from compliance_engine.surveillance import OrderEvent, StrategyDeclaration, screen_strategy_declaration, surveil
from conftest import ACCOUNT, COMPLIANCE, INSTRUMENT, LEGAL, VENUE, agent, human
from rtcore.errors import ControlDenied
from rtcore.lines import Role
from rtcore.schemas.compliance import CustomerType, EligibilityOutcome, JurisdictionCell
from rtcore.schemas.intent import Side
from web_bff.platform import BROKER, build_sim_platform


def _elig(p, vi, **kw):  # type: ignore[no-untyped-def]
    inputs = p.pipeline.eligibility_inputs(vi, p.now)
    return decide_eligibility(
        vi,
        inputs.customer,
        inputs.instrument,
        kw.get("cells", inputs.cells),
        inputs.restricted,
        broker=inputs.broker,
        feature=kw.get("feature", inputs.feature),
        now=p.now,
    )


@pytest.mark.tc("TC-CP-001")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("positive")
def test_eligible_combination_passes_and_is_deterministic(platform):  # type: ignore[no-untyped-def]
    """Eligible customer/instrument/cell -> ELIGIBLE with policy version; identical inputs give identical decision."""
    vi = platform.submit_intent(platform.make_intent())
    d1, d2 = _elig(platform, vi), _elig(platform, vi)
    assert d1 == d2 and d1.outcome == EligibilityOutcome.ELIGIBLE and d1.policy_version == "lists-sim-v0.1"
    assert {e.check for e in d1.evaluated} >= {
        "jurisdiction_cell" if False else "legal_record",
        "technical_flag",
        "dual_key_distinct_persons",
        "product_permission",
        "restricted_instrument",
    }


@pytest.mark.tc("TC-CP-002")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("negative")
def test_ineligible_combinations_carry_reason_codes(platform):  # type: ignore[no-untyped-def]
    """Restricted instrument/venue, missing product permission, short-sale ban and missing inputs are INELIGIBLE with reason codes."""
    p = platform
    p.restricted = p.restricted.model_copy(update={"restricted_venues": (VENUE,)})
    r = p.run_intent(p.make_intent())
    assert r.eligibility.outcome == EligibilityOutcome.INELIGIBLE and "CP-LIST-VENUE" in r.eligibility.reason_codes and r.decision is None
    p.restricted = p.restricted.model_copy(update={"restricted_venues": ()})
    p.restricted = p.restricted.model_copy(update={"restricted_instruments": (INSTRUMENT,)})
    assert "CP-LIST-INSTR" in p.run_intent(p.make_intent()).eligibility.reason_codes
    p.restricted = p.restricted.model_copy(update={"restricted_instruments": (), "whitelist_instruments": ("SIMEQ2",)})
    assert "CP-LIST-WHITELIST" in p.run_intent(p.make_intent()).eligibility.reason_codes
    p.restricted = p.restricted.model_copy(update={"whitelist_instruments": None})
    p.customers[list(p.customers)[0]] = p.customers[list(p.customers)[0]].model_copy(update={"product_permissions": ("ETF",)})
    assert "CP-PERM" in p.run_intent(p.make_intent()).eligibility.reason_codes
    vi = p.submit_intent(p.make_intent(side="SELL_SHORT", protective_stop="150"))
    assert {"CP-SHORT"} <= set(_elig(p, vi).reason_codes)
    missing = decide_eligibility(vi, None, None, None, None, broker=BROKER, feature="PAPER", now=p.now)
    assert missing.outcome == EligibilityOutcome.INELIGIBLE and missing.reason_codes == ("CP-HALT-INPUT",)


@pytest.mark.tc("TC-CP-003")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("abuse")
def test_legal_record_without_flag_blocked(platform):  # type: ignore[no-untyped-def]
    """Legal record alone (no technical flag) blocks; same person signing and activating blocks; agents cannot activate flags."""
    p = build_sim_platform(enable_cell=False)
    cell = p.jurisdictions.cells()[0]
    p.jurisdictions.record_legal(cell, legal_record_ref="LEGAL-1", actor=LEGAL)
    r = p.run_intent(p.make_intent())
    assert r.eligibility.outcome == EligibilityOutcome.INELIGIBLE and "CP-JURIS-FLAG" in r.eligibility.reason_codes
    with pytest.raises(ControlDenied):
        p.jurisdictions.activate_flag(cell, actor=LEGAL, now=p.now)  # same person
    with pytest.raises(ControlDenied):
        p.jurisdictions.activate_flag(cell, actor=agent(), now=p.now)
    same_person = JurisdictionCell(
        country="ZZ",
        customer_type=CustomerType.RETAIL,
        broker=BROKER,
        venue=VENUE,
        asset_class="EQUITY",
        feature="PAPER",
        legal_record_ref="L",
        legal_signed_by="x",
        technical_flag=True,
        flag_activated_by="x",
    )
    vi = p.submit_intent(p.make_intent())
    assert "CP-JURIS-DUALKEY" in _elig(p, vi, cells=(same_person,)).reason_codes


@pytest.mark.tc("TC-CP-004")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("recovery")
def test_flag_without_record_blocked_then_dual_key_enables_and_disable_is_single_person(platform):  # type: ignore[no-untyped-def]
    """Flag without legal record is impossible/blocked; after dual key the cell is live; one person can disable (rollback)."""
    p = build_sim_platform(enable_cell=False)
    cell = p.jurisdictions.cells()[0]
    with pytest.raises(ControlDenied):
        p.jurisdictions.activate_flag(cell, actor=COMPLIANCE, now=p.now)
    forged = JurisdictionCell(
        country="ZZ",
        customer_type=CustomerType.RETAIL,
        broker=BROKER,
        venue=VENUE,
        asset_class="EQUITY",
        feature="PAPER",
        technical_flag=True,
        flag_activated_by="y",
    )
    vi = p.submit_intent(p.make_intent())
    assert "CP-JURIS-LEGAL" in _elig(p, vi, cells=(forged,)).reason_codes
    p.jurisdictions.record_legal(cell, legal_record_ref="LEGAL-1", actor=LEGAL)
    live = p.jurisdictions.activate_flag(cell, actor=COMPLIANCE, now=p.now)
    assert p.jurisdictions.is_live(live) and p.run_intent(p.make_intent()).eligibility.outcome == EligibilityOutcome.ELIGIBLE
    p.jurisdictions.disable_flag(live, actor=human("analyst", Role.COMPLIANCE_ANALYST), reason="rollback drill")
    assert p.run_intent(p.make_intent()).eligibility.outcome == EligibilityOutcome.INELIGIBLE
    assert p.audit.by_action("jurisdiction.flag.changed")
    assert "CP-JURIS-NOCELL" in _elig(p, vi, feature="BOUNDED_AUTONOMOUS").reason_codes


@pytest.mark.tc("TC-CP-005")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("negative")
def test_surveillance_patterns_and_registration_screen(platform):  # type: ignore[no-untyped-def]
    """Synthetic wash/spoof/close patterns are detected; manipulation-capable or out-of-scope strategies are rejected at registration."""
    from decimal import Decimal

    t = platform.now
    evs = (
        OrderEvent(
            order_id="a",
            account_id=ACCOUNT,
            instrument_id=INSTRUMENT,
            side=Side.BUY,
            quantity=Decimal(100),
            price=Decimal(100),
            submitted_at=t,
            filled_quantity=Decimal(100),
        ),
        OrderEvent(
            order_id="b",
            account_id=ACCOUNT,
            instrument_id=INSTRUMENT,
            side=Side.SELL,
            quantity=Decimal(100),
            price=Decimal(100),
            submitted_at=t + timedelta(minutes=1),
            filled_quantity=Decimal(100),
        ),
        OrderEvent(
            order_id="c",
            account_id=ACCOUNT,
            instrument_id=INSTRUMENT,
            side=Side.SELL,
            quantity=Decimal(5000),
            price=Decimal(101),
            submitted_at=t + timedelta(minutes=2),
            cancelled_at=t + timedelta(minutes=2, seconds=3),
        ),
        OrderEvent(
            order_id="d",
            account_id=ACCOUNT,
            instrument_id=INSTRUMENT,
            side=Side.BUY,
            quantity=Decimal(50),
            price=Decimal(100),
            submitted_at=t + timedelta(minutes=2, seconds=1),
            filled_quantity=Decimal(50),
        ),
        OrderEvent(
            order_id="e",
            account_id=ACCOUNT,
            instrument_id=INSTRUMENT,
            side=Side.BUY,
            quantity=Decimal(10),
            price=Decimal(100),
            submitted_at=t + timedelta(hours=7),
            filled_quantity=Decimal(10),
            session_close=t + timedelta(hours=7, minutes=2),
        ),
    )
    patterns = {a.pattern for a in surveil(evs)}
    assert {"WASH_TRADE", "SPOOFING", "MARKING_THE_CLOSE"} <= patterns
    assert screen_strategy_declaration(
        StrategyDeclaration(strategy_id="mm", two_sided_resting_quotes=True, replicates_other_accounts=True)
    ) == ("CP-SCOPE-MARKET-MAKING", "CP-SCOPE-COPY-TRADING")
    from strategy_service.registry import StrategyStatus, StrategyVersion

    with pytest.raises(ControlDenied):
        platform.strategies.register(
            StrategyVersion(
                strategy_id="mm",
                version="1",
                owner_id="q",
                model_id="m",
                model_version="1",
                params={},
                declaration=StrategyDeclaration(strategy_id="mm", provides_personal_advice=True),
                status=StrategyStatus.PROPOSED,
            )
        )


@pytest.mark.tc("TC-CP-006")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("recovery")
def test_retention_deletion_suppressed_under_legal_hold(platform):  # type: ignore[no-untyped-def]
    """Deletion requests are suppressed (not destroyed) under legal hold or retention; decision logged [O-09]."""
    from compliance_engine.retention import DeletionOutcome

    ret = platform.retention
    ret.add_schedule(
        RetentionSchedule(record_class="trading_record", jurisdiction="ZZ", retain_for=timedelta(days=365 * 5), source_ref="SIM-FIXTURE")
    )
    created = platform.now - timedelta(days=30)
    assert (
        ret.request_deletion(
            record_class="trading_record",
            jurisdiction="ZZ",
            scope="cust-sim-001",
            record_created_at=created,
            now=platform.now,
            requested_by="cust",
        )
        == DeletionOutcome.SUPPRESSED_RETENTION
    )
    ret.place_hold(LegalHold(hold_id="h1", scope="cust-sim-001", reason="investigation", placed_by="legal.agent", placed_at=platform.now))
    assert (
        ret.request_deletion(
            record_class="session_log",
            jurisdiction="ZZ",
            scope="cust-sim-001",
            record_created_at=created,
            now=platform.now,
            requested_by="cust",
        )
        == DeletionOutcome.SUPPRESSED_LEGAL_HOLD
    )
    ret.release_hold("h1", released_by="legal.agent")
    assert (
        ret.request_deletion(
            record_class="session_log",
            jurisdiction="ZZ",
            scope="cust-sim-001",
            record_created_at=created,
            now=platform.now,
            requested_by="cust",
        )
        == DeletionOutcome.DELETED
    )
    assert len(platform.audit.by_action("retention.deletion.decided")) == 3
