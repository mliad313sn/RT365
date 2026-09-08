"""TC-CP — Compliance eligibility & dual-key market enablement [Source: 07; FR-15; C6]."""

from __future__ import annotations

from datetime import timedelta

import pytest
from compliance_engine.eligibility import decide_eligibility
from compliance_engine.retention import LegalHold, RetentionSchedule
from compliance_engine.surveillance import OrderEvent, StrategyDeclaration, screen_strategy_declaration, surveil
from conftest import ACCOUNT, COMPLIANCE, INSTRUMENT, LEGAL, VENUE, agent, human, sim_legal_record
from rtcore.errors import ControlDenied
from rtcore.lines import Role
from rtcore.schemas.account import AccountMode
from rtcore.schemas.compliance import (
    ClassificationBasis,
    ClassificationEvidence,
    CustomerType,
    DisclosureAcknowledgement,
    EligibilityOutcome,
    JurisdictionCell,
    LegalRecordRef,
    ModeConsent,
)
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
        "classification_evidence",
        "disclosure_acknowledged",
    }
    # The fixture cell's legal record is a typed, hashed reference labelled simulated (never a legal opinion) [O-71].
    cell = platform.jurisdictions.cells()[0]
    assert isinstance(cell.legal_record_ref, LegalRecordRef) and cell.legal_record_ref.simulated and cell.simulated
    legal_check = next(e for e in d1.evaluated if e.check == "legal_record")
    assert cell.legal_record_ref.record_id in legal_check.value and cell.legal_record_ref.document_sha256[:12] in legal_check.value
    # PAPER needs no per-mode consent; the fixture customer's classification is assessor-established, not self-declared.
    assert "mode_consent" not in {e.check for e in d1.evaluated}
    assert all(e.result.value == "PASS" for e in d1.evaluated)


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
    p.jurisdictions.record_legal(cell, legal_record_ref=sim_legal_record("SIM-LEGAL-1"), actor=LEGAL)
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
        simulated=True,
        legal_record_ref=sim_legal_record("SIM-L"),
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
        simulated=True,
        technical_flag=True,
        flag_activated_by="y",
    )
    vi = p.submit_intent(p.make_intent())
    assert "CP-JURIS-LEGAL" in _elig(p, vi, cells=(forged,)).reason_codes
    p.jurisdictions.record_legal(cell, legal_record_ref=sim_legal_record("SIM-LEGAL-1"), actor=LEGAL)
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
    ret.add_schedule(
        RetentionSchedule(record_class="session_log", jurisdiction="ZZ", retain_for=timedelta(days=7), source_ref="SIM-FIXTURE")
    )
    created = platform.now - timedelta(days=30)
    assert (
        ret.request_deletion(
            record_class="trading_record",
            jurisdiction="ZZ",
            scopes=("cust-sim-001", "acct-sim-001"),
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
            scopes=("cust-sim-001", "acct-sim-001"),
            record_created_at=created,
            now=platform.now,
            requested_by="cust",
        )
        == DeletionOutcome.SUPPRESSED_LEGAL_HOLD
    )
    ret.release_hold("h1", LEGAL)
    assert (
        ret.request_deletion(
            record_class="session_log",
            jurisdiction="ZZ",
            scopes=("cust-sim-001", "acct-sim-001"),
            record_created_at=created,
            now=platform.now,
            requested_by="cust",
        )
        == DeletionOutcome.DELETED
    )
    assert len(platform.audit.by_action("retention.deletion.decided")) == 3


@pytest.mark.tc("TC-CP-007")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("abuse")
def test_dual_key_requires_legal_and_compliance_hands():  # type: ignore[no-untyped-def]
    """The legal record must be signed by a human Legal Agent: two Compliance people, an agent, or the same person twice never satisfy the dual key (council finding F-1, 2026-09-08)."""
    p = build_sim_platform(enable_cell=False)
    cell = p.jurisdictions.cells()[0]
    for signer in (COMPLIANCE, human("analyst", Role.COMPLIANCE_ANALYST), agent(), human("po", Role.PRODUCT_OWNER)):
        with pytest.raises(ControlDenied):
            p.jurisdictions.record_legal(cell, legal_record_ref=sim_legal_record("SIM-LEGAL-X"), actor=signer)
    with pytest.raises(ControlDenied):
        p.jurisdictions.activate_flag(cell, actor=COMPLIANCE, now=p.now)  # nothing signed
    signed = p.jurisdictions.record_legal(cell, legal_record_ref=sim_legal_record("SIM-LEGAL-1"), actor=LEGAL)
    with pytest.raises(ControlDenied):
        p.jurisdictions.activate_flag(signed, actor=LEGAL, now=p.now)  # same person
    with pytest.raises(ControlDenied):
        p.jurisdictions.activate_flag(signed, actor=human("legal.2", Role.LEGAL_AGENT), now=p.now)  # two Legal hands, no Compliance
    with pytest.raises(ControlDenied):
        p.jurisdictions.activate_flag(
            signed, actor=human("po", Role.PRODUCT_OWNER), now=p.now
        )  # the Product Owner is never a dual-key hand
    live = p.jurisdictions.activate_flag(signed, actor=COMPLIANCE, now=p.now)
    assert p.jurisdictions.is_live(live) and live.legal_signed_by == LEGAL.actor_id and live.flag_activated_by == COMPLIANCE.actor_id


def _customer(p):  # type: ignore[no-untyped-def]
    return p.customers[list(p.customers)[0]]


def _set_customer(p, **update):  # type: ignore[no-untyped-def]
    cid = list(p.customers)[0]
    p.customers[cid] = p.customers[cid].model_copy(update=update)
    return p.customers[cid]


def _codes(p, feature=None):  # type: ignore[no-untyped-def]
    vi = p.submit_intent(p.make_intent())
    return _elig(p, vi, **({"feature": feature} if feature else {})).reason_codes


@pytest.mark.tc("TC-CP-008")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("abuse")
def test_legal_record_reference_integrity():  # type: ignore[no-untyped-def]
    """A legal record is a typed reference (record id, signing entity, date, document hash): free strings, malformed hashes and SIM- records on real-country cells (or real-looking records on simulated cells) are refused; the accepted record is anchored in the audit chain with a correlation_id (council P-2, O-71)."""
    p = build_sim_platform(enable_cell=False)
    zz = p.jurisdictions.cells()[0]
    assert zz.simulated
    with pytest.raises(ControlDenied):
        p.jurisdictions.record_legal(zz, legal_record_ref="SIM-LEGAL-FIXTURE-001", actor=LEGAL)  # type: ignore[arg-type]
    with pytest.raises(ControlDenied):
        p.jurisdictions.record_legal(zz, legal_record_ref={"record_id": "SIM-X"}, actor=LEGAL)  # type: ignore[arg-type]
    good = sim_legal_record("SIM-LEGAL-1")
    for bad in (
        {"document_sha256": "abc"},
        {"document_sha256": good.document_sha256.upper()},
        {"document_sha256": ""},
        {"signing_entity": ""},
        {"signing_entity": " "},
        {"record_id": ""},
        {"record_id": "sim-lower"},
        {"record_id": "SIM LEGAL 1"},
    ):
        with pytest.raises(ValueError):
            LegalRecordRef(**{**good.model_dump(), **bad})
    with pytest.raises(ValueError):
        LegalRecordRef(record_id="SIM-1", signing_entity="x", signed_on="not-a-date", document_sha256=good.document_sha256)  # type: ignore[arg-type]
    # A real-looking record on the simulated cell is refused: sim evidence must never look like a legal opinion (D-012, X-6).
    real_looking = good.model_copy(update={"record_id": "LEGAL-OPINION-2026-001"})
    assert not real_looking.simulated
    with pytest.raises(ControlDenied):
        p.jurisdictions.record_legal(zz, legal_record_ref=real_looking, actor=LEGAL)
    # A SIM- record on a real-country cell is refused, both at the registry and at the schema.
    fr = p.jurisdictions.propose(
        country="FR", customer_type=CustomerType.PROFESSIONAL, broker=BROKER, venue=VENUE, asset_class="EQUITY", feature="PAPER"
    )
    assert not fr.simulated
    with pytest.raises(ControlDenied):
        p.jurisdictions.record_legal(fr, legal_record_ref=good, actor=LEGAL)
    with pytest.raises(ValueError):
        JurisdictionCell(**{**fr.model_dump(), "legal_record_ref": good})
    with pytest.raises(ValueError):
        JurisdictionCell(**{**zz.model_dump(), "legal_record_ref": real_looking})
    # The simulated label itself cannot be forged: a user-assigned code is always simulated, an ISO country never.
    with pytest.raises(ValueError):
        JurisdictionCell(**{**zz.model_dump(), "simulated": False})
    with pytest.raises(ValueError):
        JurisdictionCell(**{**fr.model_dump(), "simulated": True})
    # A record for a cell that was never proposed is refused (nothing to attach it to).
    ghost = zz.model_copy(update={"venue": "GHOSTX"})
    with pytest.raises(ControlDenied):
        p.jurisdictions.record_legal(ghost, legal_record_ref=good, actor=LEGAL)
    assert not p.audit.by_action("jurisdiction.legal.recorded")
    # The well-formed simulated record is accepted and anchored: id, signer, date and hash are in the audit payload.
    signed = p.jurisdictions.record_legal(zz, legal_record_ref=good, actor=LEGAL)
    assert signed.legal_record_ref == good and signed.legal_signed_by == LEGAL.actor_id
    ev = p.audit.by_action("jurisdiction.legal.recorded")[-1]
    rec = ev.payload["legal_record_ref"]
    assert rec["record_id"] == "SIM-LEGAL-1" and rec["document_sha256"] == good.document_sha256 and rec["signed_on"] == "2026-09-01"
    assert ev.correlation_id not in ("", "-") and ev.payload["correlation_id"] == ev.correlation_id
    # The registry only ever hands out the stored cell: a caller-side record on the cell object is ignored.
    live = p.jurisdictions.activate_flag(zz, actor=COMPLIANCE, now=p.now)
    assert live.legal_record_ref == good and p.jurisdictions.is_live(live)


@pytest.mark.tc("TC-CP-009")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("negative")
@pytest.mark.parametrize("customer_type", list(CustomerType))
@pytest.mark.parametrize("feature", ["PAPER", "SUPERVISED", "BOUNDED_AUTONOMOUS"])
def test_customer_type_by_mode_needs_its_own_cell(customer_type, feature):  # type: ignore[no-untyped-def]
    """A cell enabled for PROFESSIONAL/PAPER makes only PROFESSIONAL/PAPER eligible: every other CustomerType x mode pair is CP-JURIS-NOCELL (six-dimension match is exact; D-045 rule 1)."""
    p = build_sim_platform(enable_cell=False)
    cell = p.jurisdictions.propose(
        country="ZZ", customer_type=CustomerType.PROFESSIONAL, broker=BROKER, venue=VENUE, asset_class="EQUITY", feature="PAPER"
    )
    cell = p.jurisdictions.record_legal(cell, legal_record_ref=sim_legal_record("SIM-LEGAL-PRO"), actor=LEGAL)
    live = p.jurisdictions.activate_flag(cell, actor=COMPLIANCE, now=p.now)
    assert p.jurisdictions.is_live(live)
    _set_customer(p, customer_type=customer_type)  # fixture consents cover every mode, so only the cell decides
    vi = p.submit_intent(p.make_intent())
    d = _elig(p, vi, cells=(live,), feature=feature)
    if customer_type == CustomerType.PROFESSIONAL and feature == "PAPER":
        assert d.outcome == EligibilityOutcome.ELIGIBLE and "CP-JURIS-NOCELL" not in d.reason_codes
    else:
        assert d.outcome == EligibilityOutcome.INELIGIBLE and "CP-JURIS-NOCELL" in d.reason_codes
        cell_check = next(e for e in d.evaluated if e.check == "jurisdiction_cell")
        assert cell_check.value == f"ZZ/{customer_type.value}/{BROKER}/{VENUE}/EQUITY/{feature}"


@pytest.mark.tc("TC-CP-010")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("negative")
def test_disclosure_consent_and_classification_are_decision_inputs():  # type: ignore[no-untyped-def]
    """Missing or stale disclosure acknowledgement gives CP-DISCL; SUPERVISED/BOUNDED without a recorded consent for that mode gives CP-MODE-CONSENT (PAPER needs none); absent classification evidence gives CP-CLASS; each carries value and threshold (council P-3/P-4)."""
    p = build_sim_platform(mode=AccountMode.SUPERVISED)
    base = _customer(p)
    assert base.disclosure_acknowledgement is not None and base.classification_evidence is not None
    assert p.run_intent(p.make_intent()).eligibility.outcome == EligibilityOutcome.ELIGIBLE
    # Disclosure
    _set_customer(p, disclosure_acknowledgement=None)
    assert "CP-DISCL" in _codes(p)
    _set_customer(
        p, disclosure_acknowledgement=DisclosureAcknowledgement(version="SIM-DISCL-v0.0", acknowledged_at=p.now - timedelta(days=1))
    )
    vi = p.submit_intent(p.make_intent())
    d = _elig(p, vi)
    chk = next(e for e in d.evaluated if e.check == "disclosure_acknowledged")
    assert "CP-DISCL" in d.reason_codes and chk.value == "SIM-DISCL-v0.0" and chk.threshold == "SIM-DISCL-v0.1"
    _set_customer(
        p, disclosure_acknowledgement=DisclosureAcknowledgement(version="SIM-DISCL-v0.1", acknowledged_at=p.now + timedelta(minutes=1))
    )
    assert "CP-DISCL" in _codes(p)  # an acknowledgement dated in the future is not an acknowledgement
    _set_customer(p, disclosure_acknowledgement=base.disclosure_acknowledgement)
    assert "CP-DISCL" not in _codes(p)
    # Mode consent
    _set_customer(p, mode_consents=())
    assert "CP-MODE-CONSENT" in _codes(p, "SUPERVISED") and "CP-MODE-CONSENT" in _codes(p, "BOUNDED_AUTONOMOUS")
    assert "CP-MODE-CONSENT" not in _codes(p, "PAPER")
    _set_customer(p, mode_consents=(ModeConsent(mode="SUPERVISED", consented_at=p.now + timedelta(minutes=1)),))
    assert "CP-MODE-CONSENT" in _codes(p, "SUPERVISED")  # future-dated consent is not consent
    _set_customer(p, mode_consents=(ModeConsent(mode="SUPERVISED", consented_at=p.now - timedelta(days=1)),))
    assert "CP-MODE-CONSENT" not in _codes(p, "SUPERVISED") and "CP-MODE-CONSENT" in _codes(p, "BOUNDED_AUTONOMOUS")
    with pytest.raises(ValueError):
        ModeConsent(mode="OBSERVE", consented_at=p.now)  # consent is only meaningful for order-placing modes
    _set_customer(p, mode_consents=base.mode_consents)
    # Classification evidence
    _set_customer(p, classification_evidence=None)
    vi = p.submit_intent(p.make_intent())
    d = _elig(p, vi)
    chk = next(e for e in d.evaluated if e.check == "classification_evidence")
    assert "CP-CLASS" in d.reason_codes and chk.value == "none" and d.outcome == EligibilityOutcome.INELIGIBLE
    _set_customer(p, classification_evidence=base.classification_evidence)
    assert p.run_intent(p.make_intent()).eligibility.outcome == EligibilityOutcome.ELIGIBLE


@pytest.mark.tc("TC-CP-011")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("abuse")
def test_self_declared_classification_never_unlocks_a_cell():  # type: ignore[no-untyped-def]
    """A customer who ticks 'professional' (SELF_DECLARED basis, or assessed by themselves) stays INELIGIBLE with CP-CLASS even when a PROFESSIONAL cell is live; consent for one mode never covers another; evidence fields are typed and cannot be free strings (council X-5, P-4)."""
    p = build_sim_platform(enable_cell=False)
    cell = p.jurisdictions.propose(
        country="ZZ", customer_type=CustomerType.PROFESSIONAL, broker=BROKER, venue=VENUE, asset_class="EQUITY", feature="SUPERVISED"
    )
    cell = p.jurisdictions.record_legal(cell, legal_record_ref=sim_legal_record("SIM-LEGAL-PRO-S"), actor=LEGAL)
    live = p.jurisdictions.activate_flag(cell, actor=COMPLIANCE, now=p.now)
    base = _customer(p)
    assert base.classification_evidence is not None
    opt_up = base.classification_evidence.model_copy(update={"basis": ClassificationBasis.SELF_DECLARED, "assessed_by": base.customer_id})
    _set_customer(p, customer_type=CustomerType.PROFESSIONAL, classification_evidence=opt_up)
    vi = p.submit_intent(p.make_intent())
    d = _elig(p, vi, cells=(live,), feature="SUPERVISED")
    assert d.outcome == EligibilityOutcome.INELIGIBLE and "CP-CLASS" in d.reason_codes and "CP-JURIS-NOCELL" not in d.reason_codes
    chk = next(e for e in d.evaluated if e.check == "classification_evidence")
    assert "SELF_DECLARED" in chk.value and "not self-declared" in chk.threshold
    # Assessor-basis but assessed by the customer themself is still self-declared.
    _set_customer(p, classification_evidence=base.classification_evidence.model_copy(update={"assessed_by": base.customer_id}))
    assert "CP-CLASS" in _elig(p, p.submit_intent(p.make_intent()), cells=(live,), feature="SUPERVISED").reason_codes
    # Assessment dated in the future is not an assessment.
    _set_customer(p, classification_evidence=base.classification_evidence.model_copy(update={"assessed_at": p.now + timedelta(minutes=1)}))
    assert "CP-CLASS" in _elig(p, p.submit_intent(p.make_intent()), cells=(live,), feature="SUPERVISED").reason_codes
    # Proper assessor evidence + PROFESSIONAL + consent for SUPERVISED is eligible; consent only for BOUNDED does not cover SUPERVISED.
    _set_customer(p, classification_evidence=base.classification_evidence)
    assert _elig(p, p.submit_intent(p.make_intent()), cells=(live,), feature="SUPERVISED").outcome == EligibilityOutcome.ELIGIBLE
    _set_customer(p, mode_consents=tuple(c for c in base.mode_consents if c.mode == "BOUNDED_AUTONOMOUS"))
    assert "CP-MODE-CONSENT" in _elig(p, p.submit_intent(p.make_intent()), cells=(live,), feature="SUPERVISED").reason_codes
    # Typed fields: no free-string evidence, no unknown basis, no extra fields.
    for bad in (
        {"classification_evidence": "assessed by ops"},
        {"classification_evidence": {"evidence_ref": "x"}},
        {"disclosure_acknowledgement": "v1"},
        {"mode_consents": ("SUPERVISED",)},
    ):
        with pytest.raises(ValueError):
            type(base).model_validate({**base.model_dump(), **bad})
    with pytest.raises(ValueError):
        ClassificationEvidence(evidence_ref="x", assessed_by="a", assessed_at=p.now, basis="VERBAL")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        ClassificationEvidence(evidence_ref="", assessed_by="a", assessed_at=p.now, basis=ClassificationBasis.ASSESSOR_REVIEW)
    with pytest.raises(ValueError):
        ClassificationEvidence(evidence_ref="x", assessed_by="", assessed_at=p.now, basis=ClassificationBasis.ASSESSOR_REVIEW)


@pytest.mark.tc("TC-CP-012")
@pytest.mark.req("FR-15")
@pytest.mark.quartet("recovery")
def test_consent_and_acknowledgement_can_be_restored_and_withdrawn():  # type: ignore[no-untyped-def]
    """Withdrawing consent or acknowledgement makes the next decision INELIGIBLE immediately; recording them again restores eligibility; every decision is audited under the intent's correlation_id."""
    p = build_sim_platform(mode=AccountMode.SUPERVISED)
    base = _customer(p)
    ok1 = p.run_intent(p.make_intent())
    assert ok1.eligibility.outcome == EligibilityOutcome.ELIGIBLE
    _set_customer(p, mode_consents=tuple(c for c in base.mode_consents if c.mode != "SUPERVISED"))
    withdrawn = p.run_intent(p.make_intent())
    assert withdrawn.eligibility.outcome == EligibilityOutcome.INELIGIBLE and "CP-MODE-CONSENT" in withdrawn.eligibility.reason_codes
    assert withdrawn.decision is None
    _set_customer(
        p, mode_consents=base.mode_consents + (ModeConsent(mode="SUPERVISED", consented_at=p.now, consent_ref="SIM-RECONSENT-1"),)
    )
    restored = p.run_intent(p.make_intent())
    assert restored.eligibility.outcome == EligibilityOutcome.ELIGIBLE
    _set_customer(p, disclosure_acknowledgement=None)
    assert "CP-DISCL" in p.run_intent(p.make_intent()).eligibility.reason_codes
    _set_customer(p, disclosure_acknowledgement=DisclosureAcknowledgement(version="SIM-DISCL-v0.1", acknowledged_at=p.now))
    assert p.run_intent(p.make_intent()).eligibility.outcome == EligibilityOutcome.ELIGIBLE
    for r in (ok1, withdrawn, restored):
        rows = p.audit.by_correlation(r.validated_intent.correlation_id)
        assert any(row.action == "eligibility.decided.v1" for row in rows)
