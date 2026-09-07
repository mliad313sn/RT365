from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from rtcore.provenance import Provenance
from rtcore.schemas.base import StrictModel


class RawBar(StrictModel):
    instrument_id: str
    market_ts: datetime
    last: Decimal
    bid: Decimal | None = None
    ask: Decimal | None = None
    volume: Decimal = Decimal("0")
    average_daily_volume: Decimal = Decimal("0")
    realized_volatility_pct: Decimal = Decimal("0")


class DataProvider(ABC):
    name: str
    provenance: Provenance

    @abstractmethod
    def entitled(self, tenant_id: str, instrument_id: str) -> bool: ...

    @abstractmethod
    def entitled_field(self, tenant_id: str, field: str) -> bool: ...

    @abstractmethod
    def bars(self, instrument_id: str, *, start: datetime, end: datetime) -> tuple[RawBar, ...]: ...
