"""Single-code-path backtest runner (ADR-008): replays snapshots through the production pipeline.

Leakage defence: the strategy only ever sees ``store.series(..., knowledge_ts=bar_ts)``; the
risk engine receives the snapshot for ``now = bar_ts``; execution happens on the next bar
(``CostModel.latency_bars``). A ``LookAheadViolation`` anywhere fails the run.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Any

from rtcore.money import ZERO
from rtcore.schemas.base import StrictModel
from rtcore.schemas.intent import Side, TradeIntent
from rtcore.schemas.market import MarketSnapshot
from strategy_service.signals import timed_signal

from backtest_engine.costs import CostModel
from backtest_engine.metrics import BacktestMetrics, compute_metrics

DISCLAIMER = (
    "Backtest metrics inform decisions; they do not prove future profitability [Source: 08]. "
    "Simulated data, simulated broker, sim policy fixtures; no market, strategy or autonomy is enabled by this result."
)


class BacktestReport(StrictModel):
    strategy_id: str
    strategy_version: str
    instrument_id: str
    data_snapshot_id: str
    cost_model_version: str
    hypothesis_hash: str | None
    bars: int
    intents: int
    approved: int
    rejected: int
    fills: int
    metrics: BacktestMetrics
    fills_hash: str
    decisions_hash: str
    disclaimer: str = DISCLAIMER


class BacktestRunner:
    """The runner is handed callables that execute the *production* pipeline for one bar."""

    def __init__(
        self,
        *,
        history: Callable[[str, datetime], tuple[MarketSnapshot, ...]],
        position_qty: Callable[[str], Decimal],
        nav: Callable[[], Decimal],
        gross: Callable[[], Decimal],
        submit_and_process: Callable[[TradeIntent, datetime], dict[str, Any]],
        settle_bar: Callable[[datetime], tuple[Decimal, ...]],  # marks, polls fills, returns per-trade pnl closed on this bar
        cost_model: CostModel,
        observe: Callable[..., object] | None = None,  # signal_latency_ms emission; measurement only, never an input
    ) -> None:
        self._history = history
        self._position_qty = position_qty
        self._nav = nav
        self._gross = gross
        self._submit = submit_and_process
        self._settle = settle_bar
        self._costs = cost_model
        self._observe = observe

    def run(
        self,
        *,
        strategy: Any,
        intent_builder: Callable[[Any, MarketSnapshot, Decimal], TradeIntent | None],
        instrument_id: str,
        bar_timestamps: tuple[datetime, ...],
        data_snapshot_id: str,
        hypothesis_hash: str | None,
    ) -> BacktestReport:
        from rtcore.ids import hash_of

        nav_series: list[Decimal] = []
        gross_series: list[Decimal] = []
        trade_pnls: list[Decimal] = []
        traded_notional = ZERO
        fills_log: list[dict[str, Any]] = []
        decisions_log: list[dict[str, Any]] = []
        intents = approved = rejected = fills = 0
        pending: list[tuple[datetime, TradeIntent]] = []
        for ts in bar_timestamps:
            # Execute intents generated on earlier bars (latency)
            due = [p for p in pending if (ts - p[0]) >= (bar_timestamps[1] - bar_timestamps[0]) * self._costs.latency_bars]
            pending = [p for p in pending if p not in due]
            for _, intent in due:
                res = self._submit(intent, ts)
                decisions_log.append({"intent": str(intent.intent_id), "outcome": res.get("outcome"), "reasons": res.get("reason_codes")})
                if res.get("outcome") == "APPROVED":
                    approved += 1
                    for f in res.get("fills", []):
                        fills += 1
                        traded_notional += Decimal(str(f["quantity"])) * Decimal(str(f["price"]))
                        fills_log.append(f)
                else:
                    rejected += 1
            trade_pnls.extend(self._settle(ts))
            hist = self._history(instrument_id, ts)
            if not hist:
                continue
            nav_series.append(self._nav())
            gross_series.append(self._gross())
            signal = timed_signal(
                strategy,
                hist,
                position_qty=self._position_qty(instrument_id),
                nav=self._nav(),
                observe=self._observe,
                runner="backtest",
            )
            if signal is not None:
                new_intent = intent_builder(signal, hist[-1], self._position_qty(instrument_id))
                if new_intent is not None:
                    intents += 1
                    pending.append((ts, new_intent))
        metrics = compute_metrics(nav_series, gross_series, traded_notional, trade_pnls)
        return BacktestReport(
            strategy_id=strategy.strategy_id,
            strategy_version=strategy.version,
            instrument_id=instrument_id,
            data_snapshot_id=data_snapshot_id,
            cost_model_version=self._costs.version,
            hypothesis_hash=hypothesis_hash,
            bars=len(bar_timestamps),
            intents=intents,
            approved=approved,
            rejected=rejected,
            fills=fills,
            metrics=metrics,
            fills_hash=hash_of(fills_log),
            decisions_hash=hash_of(decisions_log),
        )


def side_sign(side: Side) -> Decimal:
    return Decimal(1) if side in (Side.BUY, Side.BUY_TO_COVER) else Decimal(-1)
