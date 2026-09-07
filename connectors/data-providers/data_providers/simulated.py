"""Deterministic simulated feed for dev/sim: a seeded random walk. Provenance = SIMULATED, never licensed."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from rtcore.provenance import Provenance

from data_providers.base import DataProvider, RawBar


@dataclass
class SimulatedFeed(DataProvider):
    name: str = "sim-feed"
    provenance: Provenance = Provenance.SIMULATED
    seed: int = 7
    step: timedelta = timedelta(minutes=1)
    start_prices: dict[str, Decimal] = field(default_factory=dict)
    entitlements: dict[str, set[str]] = field(default_factory=dict)  # tenant -> instruments ('*' for all)
    depth_entitled: set[str] = field(default_factory=set)  # tenants entitled to bid/ask
    adv: Decimal = Decimal("1000000")

    def entitled(self, tenant_id: str, instrument_id: str) -> bool:
        allowed = self.entitlements.get(tenant_id, set())
        return "*" in allowed or instrument_id in allowed

    def entitled_field(self, tenant_id: str, field_name: str) -> bool:
        if field_name == "depth":
            return tenant_id in self.depth_entitled
        return True

    def bars(self, instrument_id: str, *, start: datetime, end: datetime) -> tuple[RawBar, ...]:
        rng = random.Random(f"{self.seed}:{instrument_id}")
        price = self.start_prices.get(instrument_id, Decimal("100"))
        out: list[RawBar] = []
        ts = start
        vol = Decimal("20")
        while ts <= end:
            move = Decimal(str(round(rng.gauss(0, 0.002), 6)))
            price = (price * (1 + move)).quantize(Decimal("0.01"))
            if price <= 0:
                price = Decimal("0.01")
            spread = (price * Decimal("0.0005")).quantize(Decimal("0.01"))
            out.append(
                RawBar(
                    instrument_id=instrument_id,
                    market_ts=ts,
                    last=price,
                    bid=price - spread,
                    ask=price + spread,
                    volume=Decimal(rng.randint(100, 5000)),
                    average_daily_volume=self.adv,
                    realized_volatility_pct=vol,
                )
            )
            ts += self.step
        return tuple(out)
