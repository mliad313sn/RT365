"""TC-MD — Market data: provenance, freshness, quality, look-ahead [Source: 03, 08; FR-03; T-03]."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from conftest import ACCOUNT, INSTRUMENT, TENANT
from data_providers.base import RawBar
from market_data.store import LookAheadViolation
from rtcore.errors import ControlDenied
from rtcore.schemas.decision import Outcome
from rtcore.schemas.market import DataQuality


@pytest.mark.tc("TC-MD-001")
@pytest.mark.req("FR-03")
@pytest.mark.quartet("positive")
def test_bar_stored_with_timestamps_and_provenance(platform):  # type: ignore[no-untyped-def]
    """Every stored snapshot carries market_ts, ingest_ts, provenance and quality; the universe includes delisted names as of date."""
    snap = platform.market_snapshot(INSTRUMENT)
    assert snap and snap.ingest_ts > snap.market_ts and snap.provenance.value == "simulated" and snap.quality == DataQuality.OK
    universe = platform.market.instruments.universe(as_of=platform.now)
    assert {i.instrument_id for i in universe} >= {INSTRUMENT, "SIMDELISTED"}
    assert platform.market.instruments.get("SIMDELISTED", as_of=platform.now) is None


@pytest.mark.tc("TC-MD-002")
@pytest.mark.req("FR-03")
@pytest.mark.quartet("negative")
def test_stale_beyond_budget_rejected(platform):  # type: ignore[no-untyped-def]
    """Snapshot older than the per-asset-class freshness budget -> RK-FRESH rejection; autonomy would be suspended by SLO semantics."""
    platform.now = platform.now + timedelta(seconds=30)
    r = platform.run_intent(platform.make_intent(market_ts=(platform.now - timedelta(seconds=31)).isoformat()))
    assert r.decision.outcome == Outcome.REJECTED and "RK-FRESH" in r.decision.reason_codes


@pytest.mark.tc("TC-MD-003")
@pytest.mark.req("FR-03")
@pytest.mark.quartet("abuse")
def test_outlier_backdated_and_unentitled_data(platform):  # type: ignore[no-untyped-def]
    """Poisoned tick (outlier) is flagged SUSPECT and rejected; backdated ingest is a clock anomaly; unentitled tenant is denied."""
    last = platform.market_snapshot(INSTRUMENT)
    poisoned = RawBar(
        instrument_id=INSTRUMENT,
        market_ts=platform.now,
        last=last.last_price * Decimal("3"),
        average_daily_volume=Decimal("1000000"),
        realized_volatility_pct=Decimal("20"),
    )
    snap = platform.market.ingest(platform.feed, poisoned, tenant_id=TENANT, ingest_ts=platform.now)
    assert snap.quality == DataQuality.SUSPECT and platform.audit.by_action("market.quality.outlier")
    platform.now = platform.now + timedelta(seconds=1)
    r = platform.run_intent(platform.make_intent())
    assert "RK-FRESH-QUALITY" in r.decision.reason_codes
    with pytest.raises(ControlDenied):
        platform.market.ingest(platform.feed, poisoned, tenant_id="tenant-unlicensed", ingest_ts=platform.now)
    with pytest.raises(LookAheadViolation):
        platform.market.store.latest(INSTRUMENT, as_of=platform.now + timedelta(minutes=5), knowledge_ts=platform.now)


@pytest.mark.tc("TC-MD-004")
@pytest.mark.req("FR-03")
@pytest.mark.quartet("recovery")
def test_feed_restored_next_intent_passes(platform):  # type: ignore[no-untyped-def]
    """After a stale period, a fresh bar restores decisions without any manual step."""
    platform.now = platform.now + timedelta(minutes=2)
    stale = platform.run_intent(platform.make_intent())
    assert "RK-FRESH" in stale.decision.reason_codes
    platform.ingest_bars(INSTRUMENT, start=platform.now - timedelta(seconds=1), count=1)
    fresh = platform.run_intent(platform.make_intent())
    assert fresh.decision.outcome == Outcome.APPROVED
    assert platform.ledger.positions(ACCOUNT)
