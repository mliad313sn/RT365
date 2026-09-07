from __future__ import annotations

from decimal import Decimal

from rtcore.schemas.base import StrictModel


class CostModel(StrictModel):
    """[Source: 08] commissions, spread, slippage, latency, financing, borrow, partial fills, delistings."""

    version: str = "cost-v0.1-sim"
    commission_bps: Decimal = Decimal("1")
    spread_bps: Decimal = Decimal("5")
    slippage_bps: Decimal = Decimal("2")
    latency_bars: int = 1  # decisions execute on the next bar, never the signal bar
    financing_bps_per_day: Decimal = Decimal("0.5")
    borrow_bps_per_day: Decimal = Decimal("1")
    partial_fill_ratio: Decimal | None = None

    def scaled(self, factor: Decimal) -> CostModel:
        return self.model_copy(
            update={
                "version": f"{self.version}x{factor}",
                "commission_bps": self.commission_bps * factor,
                "spread_bps": self.spread_bps * factor,
                "slippage_bps": self.slippage_bps * factor,
                "financing_bps_per_day": self.financing_bps_per_day * factor,
                "borrow_bps_per_day": self.borrow_bps_per_day * factor,
            }
        )

    def fee_for(self, notional: Decimal) -> Decimal:
        return notional * (self.commission_bps + self.slippage_bps) / Decimal("10000")
