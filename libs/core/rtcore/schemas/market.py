"""Market snapshot with bitemporal timestamps and provenance [Source: 03, 08]."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import Field, field_validator

from rtcore.clock import ensure_utc
from rtcore.provenance import Provenance
from rtcore.schemas.base import StrictModel


class SessionState(str, Enum):
    OPEN = "OPEN"
    PRE_OPEN = "PRE_OPEN"
    AUCTION = "AUCTION"
    CLOSED = "CLOSED"
    HALTED = "HALTED"


class DataQuality(str, Enum):
    OK = "OK"
    SUSPECT = "SUSPECT"
    STALE = "STALE"
    MISSING = "MISSING"


class InstrumentAttributes(StrictModel):
    """Point-in-time instrument master row [Source: 08; DATA_MODEL]."""

    instrument_id: str
    venue: str
    asset_class: str
    currency: str
    sector: str = "UNKNOWN"
    country: str = "UNKNOWN"
    tick_size: Decimal = Field(gt=0)
    lot_size: Decimal = Field(gt=0)
    tradable: bool = True
    shortable: bool = False
    valid_from: datetime
    valid_to: datetime | None = None
    identifiers: dict[str, str] = Field(default_factory=dict)

    @field_validator("valid_from", "valid_to")
    @classmethod
    def _tz(cls, v: datetime | None) -> datetime | None:
        return None if v is None else ensure_utc(v)

    def valid_at(self, ts: datetime) -> bool:
        ts = ensure_utc(ts)
        return self.valid_from <= ts and (self.valid_to is None or ts < self.valid_to)


class MarketSnapshot(StrictModel):
    snapshot_id: str
    instrument: InstrumentAttributes
    market_ts: datetime
    ingest_ts: datetime
    provenance: Provenance
    quality: DataQuality = DataQuality.OK
    last_price: Decimal = Field(gt=0)
    bid: Decimal | None = Field(default=None, gt=0)
    ask: Decimal | None = Field(default=None, gt=0)
    reference_price: Decimal = Field(gt=0)
    average_daily_volume: Decimal = Field(ge=0)
    realized_volatility_pct: Decimal = Field(ge=0)
    session_state: SessionState = SessionState.OPEN
    venue_healthy: bool = True

    @field_validator("market_ts", "ingest_ts")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return ensure_utc(v)
