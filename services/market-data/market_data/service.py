"""Ingest: source contract -> entitlement check -> provenance stamp -> quality check -> bitemporal store [Source: 08]."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal

from data_providers.base import DataProvider, RawBar
from rtcore.errors import ControlDenied
from rtcore.ids import deterministic_id
from rtcore.schemas.market import DataQuality, MarketSnapshot

from market_data.calendar import SessionCalendar
from market_data.instruments import InstrumentMaster
from market_data.store import BitemporalStore


class MarketDataService:
    def __init__(
        self,
        store: BitemporalStore,
        instruments: InstrumentMaster,
        calendar: SessionCalendar,
        *,
        outlier_jump_pct: Decimal = Decimal("20"),
        audit: Callable[[str, dict[str, object]], object] | None = None,
    ) -> None:
        self.store = store
        self.instruments = instruments
        self.calendar = calendar
        self._outlier = outlier_jump_pct
        self._audit = audit or (lambda action, payload: None)
        self._venue_health: dict[str, bool] = {}

    def set_venue_health(self, venue: str, healthy: bool) -> None:
        self._venue_health[venue] = healthy

    def ingest(self, provider: DataProvider, bar: RawBar, *, tenant_id: str, ingest_ts: datetime) -> MarketSnapshot:
        if not provider.entitled(tenant_id, bar.instrument_id):
            self._audit("market.entitlement.denied", {"tenant": tenant_id, "instrument": bar.instrument_id, "provider": provider.name})
            raise ControlDenied(f"tenant {tenant_id} not entitled to {bar.instrument_id} from {provider.name}")
        inst = self.instruments.get(bar.instrument_id, as_of=bar.market_ts)
        if inst is None:
            raise ControlDenied(f"instrument {bar.instrument_id} not valid at {bar.market_ts.isoformat()}")
        quality = DataQuality.OK
        prev = self.store.latest(bar.instrument_id, as_of=bar.market_ts, knowledge_ts=ingest_ts)
        if prev is not None and prev.last_price > 0:
            jump = abs(bar.last - prev.last_price) / prev.last_price * Decimal("100")
            if jump > self._outlier:
                quality = DataQuality.SUSPECT
                self._audit("market.quality.outlier", {"instrument": bar.instrument_id, "jump_pct": str(jump)})
        snap = MarketSnapshot(
            snapshot_id=deterministic_id("mks", bar.instrument_id, bar.market_ts.isoformat(), provider.name, str(bar.last)),
            instrument=inst,
            market_ts=bar.market_ts,
            ingest_ts=ingest_ts,
            provenance=provider.provenance,
            quality=quality,
            last_price=bar.last,
            bid=bar.bid if provider.entitled_field(tenant_id, "depth") else None,
            ask=bar.ask if provider.entitled_field(tenant_id, "depth") else None,
            reference_price=bar.last,
            average_daily_volume=bar.average_daily_volume,
            realized_volatility_pct=bar.realized_volatility_pct,
            session_state=self.calendar.state(inst.venue, bar.market_ts),
            venue_healthy=self._venue_health.get(inst.venue, True),
        )
        self.store.put(snap)
        return snap

    def for_decision(self, instrument_id: str, *, now: datetime) -> MarketSnapshot | None:
        """Snapshot usable at decision time ``now``: knowledge time == now (no look-ahead)."""
        snap = self.store.latest(instrument_id, as_of=now, knowledge_ts=now)
        if snap is None:
            return None
        venue_ok = self._venue_health.get(snap.instrument.venue, True)
        state = self.calendar.state(snap.instrument.venue, now)
        return snap.model_copy(update={"venue_healthy": venue_ok, "session_state": state})
