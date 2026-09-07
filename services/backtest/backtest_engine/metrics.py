from __future__ import annotations

from decimal import Decimal

from rtcore.money import ZERO
from rtcore.schemas.base import StrictModel


class BacktestMetrics(StrictModel):
    """Minimum metric set [Source: 08]. Informational only; not a forecast."""

    bars: int
    total_return_pct: Decimal
    volatility_pct: Decimal
    max_drawdown_pct: Decimal
    turnover: Decimal
    exposure_pct_avg: Decimal
    trades: int
    hit_rate_pct: Decimal
    profit_factor: Decimal | None
    tail_loss_pct: Decimal


def compute_metrics(
    nav_series: list[Decimal], gross_series: list[Decimal], traded_notional: Decimal, trade_pnls: list[Decimal]
) -> BacktestMetrics:
    if not nav_series:
        return BacktestMetrics(
            bars=0,
            total_return_pct=ZERO,
            volatility_pct=ZERO,
            max_drawdown_pct=ZERO,
            turnover=ZERO,
            exposure_pct_avg=ZERO,
            trades=0,
            hit_rate_pct=ZERO,
            profit_factor=None,
            tail_loss_pct=ZERO,
        )
    start, end = nav_series[0], nav_series[-1]
    rets = [(nav_series[i] / nav_series[i - 1] - 1) if nav_series[i - 1] != ZERO else ZERO for i in range(1, len(nav_series))]
    mean = sum(rets, ZERO) / Decimal(len(rets)) if rets else ZERO
    var = sum(((r - mean) ** 2 for r in rets), ZERO) / Decimal(len(rets)) if rets else ZERO
    vol = var.sqrt() * Decimal("100") if var > ZERO else ZERO
    peak, mdd = nav_series[0], ZERO
    for v in nav_series:
        peak = max(peak, v)
        dd = (peak - v) / peak * Decimal("100") if peak > ZERO else ZERO
        mdd = max(mdd, dd)
    exposure = sum((g / n * Decimal("100") if n > ZERO else ZERO for g, n in zip(gross_series, nav_series, strict=False)), ZERO) / Decimal(
        len(nav_series)
    )
    wins = [p for p in trade_pnls if p > ZERO]
    losses = [p for p in trade_pnls if p < ZERO]
    gross_win, gross_loss = sum(wins, ZERO), -sum(losses, ZERO)
    pf = (gross_win / gross_loss) if gross_loss > ZERO else None
    worst = sorted(rets)[: max(1, len(rets) // 20)] if rets else [ZERO]
    tail = -(sum(worst, ZERO) / Decimal(len(worst))) * Decimal("100")
    return BacktestMetrics(
        bars=len(nav_series),
        total_return_pct=((end / start - 1) * Decimal("100")) if start > ZERO else ZERO,
        volatility_pct=vol,
        max_drawdown_pct=mdd,
        turnover=(traded_notional / start) if start > ZERO else ZERO,
        exposure_pct_avg=exposure,
        trades=len(trade_pnls),
        hit_rate_pct=(Decimal(len(wins)) / Decimal(len(trade_pnls)) * Decimal("100")) if trade_pnls else ZERO,
        profit_factor=pf,
        tail_loss_pct=tail,
    )
