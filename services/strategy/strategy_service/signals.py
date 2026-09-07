"""Signal and explainability contract [Source: 00; C3 §6]: thesis code, evidence references, confidence.

A signal without evidence references is schema-invalid. The sample strategy is deterministic
so that replay tests can assert identical intents from identical snapshots (ADR-008).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Protocol
from uuid import UUID, uuid5

from pydantic import Field
from rtcore.money import ZERO, round_down_to_lot
from rtcore.schemas.base import StrictModel
from rtcore.schemas.intent import OrderType, Side, TimeInForce, TradeIntent
from rtcore.schemas.market import MarketSnapshot

INTENT_NAMESPACE = UUID("6f1c9e4a-1b47-4c1c-9d4c-3d5f2c8a9b01")


class Signal(StrictModel):
    strategy_id: str
    strategy_version: str
    model_id: str
    model_version: str
    instrument_id: str
    venue: str
    side: Side
    thesis_code: str
    evidence_refs: tuple[str, ...] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    market_ts: datetime
    data_provenance: tuple[str, ...] = Field(min_length=1)
    target_notional: Decimal = Field(gt=0)


class Strategy(Protocol):
    strategy_id: str
    version: str

    def on_snapshot(self, history: tuple[MarketSnapshot, ...], *, position_qty: Decimal, nav: Decimal) -> Signal | None: ...


class SmaCrossoverStrategy:
    """Simulation-only sample: long when the fast SMA crosses above the slow SMA; flat when it crosses below.

    [Committee] It exists to exercise the control envelope end to end. Nothing about it is a
    performance claim; see docs/STRATEGY_CARDS/strat-sma-xover.md.
    """

    def __init__(
        self,
        *,
        strategy_id: str = "strat-sma-xover",
        version: str = "0.1",
        model_id: str = "rule-sma",
        model_version: str = "0.1",
        fast: int = 3,
        slow: int = 8,
        target_pct_nav: Decimal = Decimal("5"),
    ) -> None:
        self.strategy_id = strategy_id
        self.version = version
        self.model_id = model_id
        self.model_version = model_version
        self.fast = fast
        self.slow = slow
        self.target_pct_nav = target_pct_nav

    @staticmethod
    def _sma(prices: list[Decimal], n: int) -> Decimal | None:
        if len(prices) < n:
            return None
        return sum(prices[-n:], ZERO) / Decimal(n)

    def on_snapshot(self, history: tuple[MarketSnapshot, ...], *, position_qty: Decimal, nav: Decimal) -> Signal | None:
        if len(history) < self.slow + 1:
            return None
        prices = [s.last_price for s in history]
        fast_now, slow_now = self._sma(prices, self.fast), self._sma(prices, self.slow)
        fast_prev, slow_prev = self._sma(prices[:-1], self.fast), self._sma(prices[:-1], self.slow)
        if None in (fast_now, slow_now, fast_prev, slow_prev):
            return None
        assert fast_now is not None and slow_now is not None and fast_prev is not None and slow_prev is not None
        latest = history[-1]
        evidence = (f"snapshot:{latest.snapshot_id}", f"sma{self.fast}={fast_now:.4f}", f"sma{self.slow}={slow_now:.4f}")

        def make(side: Side, thesis: str, notional: Decimal) -> Signal:
            return Signal(
                strategy_id=self.strategy_id,
                strategy_version=self.version,
                model_id=self.model_id,
                model_version=self.model_version,
                instrument_id=latest.instrument.instrument_id,
                venue=latest.instrument.venue,
                side=side,
                thesis_code=thesis,
                evidence_refs=evidence,
                confidence=0.55,
                market_ts=latest.market_ts,
                data_provenance=(latest.provenance.value,),
                target_notional=notional,
            )

        if fast_prev <= slow_prev and fast_now > slow_now and position_qty <= ZERO:
            return make(Side.BUY, "SMA_XOVER_UP", nav * self.target_pct_nav / Decimal("100"))
        if fast_prev >= slow_prev and fast_now < slow_now and position_qty > ZERO:
            return make(Side.SELL, "SMA_XOVER_DOWN", position_qty * latest.last_price)
        return None


def intent_from_signal(
    signal: Signal,
    snapshot: MarketSnapshot,
    *,
    account_id: str,
    position_qty: Decimal,
    ttl: timedelta = timedelta(minutes=5),
    protective_stop_pct: Decimal = Decimal("2"),
) -> TradeIntent | None:
    price = snapshot.last_price
    if signal.side == Side.SELL:
        qty = abs(position_qty)
    else:
        qty = round_down_to_lot(signal.target_notional / price, snapshot.instrument.lot_size)
    if qty <= ZERO:
        return None
    stop = None
    if signal.side == Side.BUY:
        stop = (price * (Decimal("100") - protective_stop_pct) / Decimal("100")).quantize(snapshot.instrument.tick_size)
    intent_id = uuid5(
        INTENT_NAMESPACE,
        f"{signal.strategy_id}|{signal.strategy_version}|{account_id}|{signal.instrument_id}|{signal.market_ts.isoformat()}|{signal.side.value}",
    )
    return TradeIntent(
        intent_id=intent_id,
        strategy_id=signal.strategy_id,
        strategy_version=signal.strategy_version,
        model_id=signal.model_id,
        model_version=signal.model_version,
        account_id=account_id,
        venue=signal.venue,
        instrument_id=signal.instrument_id,
        side=signal.side,
        order_type=OrderType.MARKET,
        quantity=qty,
        time_in_force=TimeInForce.DAY,
        thesis_code=signal.thesis_code,
        confidence=signal.confidence,
        market_ts=signal.market_ts,
        data_provenance=list(signal.data_provenance),
        expiry=signal.market_ts + ttl,
        protective_stop=stop,
        evidence_refs=list(signal.evidence_refs),
    )
