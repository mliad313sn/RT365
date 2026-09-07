"""``decide_eligibility`` — pure function of intent, customer, instrument, jurisdiction cells and lists."""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from rtcore.clock import ensure_utc
from rtcore.ids import deterministic_id
from rtcore.schemas.compliance import (
    CustomerProfile,
    EligibilityDecision,
    EligibilityOutcome,
    JurisdictionCell,
    RestrictedLists,
)
from rtcore.schemas.decision import CheckResult, EvaluatedCheck
from rtcore.schemas.intent import Side, ValidatedIntent
from rtcore.schemas.market import InstrumentAttributes

COMPLEX_ASSET_CLASSES = frozenset({"OPTION", "FUTURE", "CRYPTO", "CFD", "WARRANT"})


def _build_hash() -> str:
    digest = hashlib.sha256()
    for file in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(file.name.encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()[:16]


ELIGIBILITY_BUILD_HASH = _build_hash()


def _ev(check: str, value: object, threshold: object, ok: bool, code: str) -> EvaluatedCheck:
    return EvaluatedCheck(
        check=check,
        value=str(value),
        threshold=str(threshold),
        result=CheckResult.PASS if ok else CheckResult.FAIL,
        reason_code=None if ok else code,
    )


def find_cell(
    cells: tuple[JurisdictionCell, ...], *, country: str, customer_type: str, broker: str, venue: str, asset_class: str, feature: str
) -> JurisdictionCell | None:
    for c in cells:
        if c.key == (country, customer_type, broker, venue, asset_class, feature):
            return c
    return None


def decide_eligibility(
    validated_intent: ValidatedIntent | None,
    customer: CustomerProfile | None,
    instrument: InstrumentAttributes | None,
    cells: tuple[JurisdictionCell, ...] | None,
    restricted: RestrictedLists | None,
    *,
    broker: str,
    feature: str,
    now: datetime,
) -> EligibilityDecision:
    """INELIGIBLE on any failing check; unavailable inputs -> INELIGIBLE with CP-HALT-INPUT (fail closed)."""
    now = ensure_utc(now)
    pv = restricted.policy_version if restricted else "unavailable"
    if validated_intent is None or customer is None or instrument is None or cells is None or restricted is None:
        missing = [
            n
            for n, v in (
                ("intent", validated_intent),
                ("customer", customer),
                ("instrument", instrument),
                ("cells", cells),
                ("lists", restricted),
            )
            if v is None
        ]
        return EligibilityDecision(
            decision_id=deterministic_id("elg", "missing", *missing, pv, ELIGIBILITY_BUILD_HASH),
            intent_id=str(validated_intent.intent.intent_id) if validated_intent else "unknown",
            outcome=EligibilityOutcome.INELIGIBLE,
            policy_version=pv,
            reason_codes=("CP-HALT-INPUT",),
            evaluated=(
                EvaluatedCheck(
                    check="inputs_available",
                    value=",".join(missing),
                    threshold="all present",
                    result=CheckResult.FAIL,
                    reason_code="CP-HALT-INPUT",
                ),
            ),
            decided_at=now,
            engine_build_hash=ELIGIBILITY_BUILD_HASH,
            correlation_id=validated_intent.correlation_id if validated_intent else "unknown",
            intent_hash=validated_intent.intent_hash if validated_intent else "unknown",
        )
    i = validated_intent.intent
    evaluated: list[EvaluatedCheck] = []
    evaluated.append(
        _ev("intent_integrity", validated_intent.intent_hash[:12], "hash matches", validated_intent.integrity_ok(), "CP-INTEG")
    )
    evaluated.append(
        _ev("tenant_match", validated_intent.tenant_id, customer.tenant_id, validated_intent.tenant_id == customer.tenant_id, "CP-TENANT")
    )

    cell = find_cell(
        cells,
        country=customer.jurisdiction,
        customer_type=customer.customer_type.value,
        broker=broker,
        venue=i.venue,
        asset_class=instrument.asset_class,
        feature=feature,
    )
    if cell is None:
        evaluated.append(
            _ev(
                "jurisdiction_cell",
                f"{customer.jurisdiction}/{customer.customer_type.value}/{broker}/{i.venue}/{instrument.asset_class}/{feature}",
                "cell exists",
                False,
                "CP-JURIS-NOCELL",
            )
        )
    else:
        evaluated.append(
            _ev(
                "legal_record",
                cell.legal_record_ref or "none",
                "signed legal record",
                bool(cell.legal_record_ref and cell.legal_signed_by),
                "CP-JURIS-LEGAL",
            )
        )
        evaluated.append(
            _ev("technical_flag", cell.technical_flag, True, cell.technical_flag and bool(cell.flag_activated_by), "CP-JURIS-FLAG")
        )
        evaluated.append(
            _ev(
                "dual_key_distinct_persons",
                f"{cell.legal_signed_by}/{cell.flag_activated_by}",
                "different persons",
                cell.dual_key_satisfied(),
                "CP-JURIS-DUALKEY",
            )
        )

    evaluated.append(
        _ev(
            "product_permission",
            instrument.asset_class,
            ",".join(customer.product_permissions),
            instrument.asset_class in customer.product_permissions,
            "CP-PERM",
        )
    )
    if instrument.asset_class in COMPLEX_ASSET_CLASSES:
        evaluated.append(
            _ev(
                "appropriateness",
                customer.appropriateness_assessed and customer.complex_products_allowed,
                True,
                customer.appropriateness_assessed and customer.complex_products_allowed,
                "CP-APPR",
            )
        )
    if i.side == Side.SELL_SHORT:
        evaluated.append(_ev("short_sale_permission", customer.short_selling_allowed, True, customer.short_selling_allowed, "CP-SHORT"))
        evaluated.append(
            _ev(
                "short_sale_ban",
                i.instrument_id,
                "not banned",
                i.instrument_id not in restricted.short_sale_banned_instruments,
                "CP-SHORT-BAN",
            )
        )
    evaluated.append(
        _ev(
            "restricted_instrument",
            i.instrument_id,
            "not restricted",
            i.instrument_id not in restricted.restricted_instruments,
            "CP-LIST-INSTR",
        )
    )
    issuer = instrument.identifiers.get("issuer", "")
    evaluated.append(
        _ev(
            "restricted_issuer",
            issuer or "n/a",
            "not restricted",
            not issuer or issuer not in restricted.restricted_issuers,
            "CP-LIST-ISSUER",
        )
    )
    evaluated.append(_ev("restricted_venue", i.venue, "not restricted", i.venue not in restricted.restricted_venues, "CP-LIST-VENUE"))
    if restricted.whitelist_instruments is not None:
        evaluated.append(
            _ev("whitelist", i.instrument_id, "in whitelist", i.instrument_id in restricted.whitelist_instruments, "CP-LIST-WHITELIST")
        )

    codes = tuple(dict.fromkeys(e.reason_code for e in evaluated if e.result == CheckResult.FAIL and e.reason_code))
    outcome = EligibilityOutcome.INELIGIBLE if codes else EligibilityOutcome.ELIGIBLE
    return EligibilityDecision(
        decision_id=deterministic_id(
            "elg", validated_intent.intent_hash, customer.customer_id, instrument.instrument_id, pv, ELIGIBILITY_BUILD_HASH
        ),
        intent_id=str(i.intent_id),
        outcome=outcome,
        policy_version=pv,
        reason_codes=codes,
        evaluated=tuple(evaluated),
        decided_at=now,
        engine_build_hash=ELIGIBILITY_BUILD_HASH,
        correlation_id=validated_intent.correlation_id,
        intent_hash=validated_intent.intent_hash,
    )
