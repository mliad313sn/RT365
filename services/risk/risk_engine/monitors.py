"""Runtime controls -> HALT events [Source: 05]. Consumed by the Kill Switch service (P4); never bypass the engine."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from rtcore.money import ZERO, pct
from rtcore.schemas.account import AccountSnapshot
from rtcore.schemas.base import StrictModel

from risk_engine.policy import LimitScope, Metric, RiskPolicy, effective_limit


class RuntimeMetrics(StrictModel):
    """Observed values fed by execution, reconciliation, model monitoring and SRE probes."""

    orders_last_minute: int = 0
    slippage_bps_p95: Decimal = ZERO
    rejection_rate_pct: Decimal = ZERO
    decision_latency_p99_ms: Decimal = ZERO
    broker_connected: bool = True
    venue_healthy: bool = True
    model_drift_breached: bool = False
    open_reconciliation_breaks: int = 0


class RuntimeThresholds(StrictModel):
    """[Open: O-03] numeric targets after baselines; fixture values for sim only."""

    slippage_bps_p95: Decimal = Decimal("50")
    rejection_rate_pct: Decimal = Decimal("20")
    decision_latency_p99_ms: Decimal = Decimal("500")
    abnormal_orders_per_minute_factor: Decimal = Decimal("2")


class HaltEvent(StrictModel):
    reason_code: str
    level: str  # ACCOUNT | STRATEGY | PLATFORM | VENUE
    target_id: str
    value: str
    threshold: str
    observed_at: datetime


def evaluate_runtime(
    account: AccountSnapshot,
    policy: RiskPolicy,
    metrics: RuntimeMetrics,
    now: datetime,
    thresholds: RuntimeThresholds | None = None,
) -> tuple[HaltEvent, ...]:
    th = thresholds or RuntimeThresholds()
    scope = LimitScope(tenant_id=account.tenant_id, account_id=account.account_id, strategy_id="*", instrument_id="*")
    events: list[HaltEvent] = []

    def lim(metric: Metric) -> Decimal | None:
        return effective_limit(policy, metric, scope, now).threshold

    def halt(code: str, level: str, target: str, value: object, threshold: object) -> None:
        events.append(
            HaltEvent(reason_code=code, level=level, target_id=target, value=str(value), threshold=str(threshold), observed_at=now)
        )

    nav = account.nav
    for metric, pnl, code in (
        (Metric.DAILY_LOSS_LIMIT_PCT, account.daily_pnl, "RT-LOSS-DAILY"),
        (Metric.WEEKLY_LOSS_LIMIT_PCT, account.weekly_pnl, "RT-LOSS-WEEKLY"),
        (Metric.MONTHLY_LOSS_LIMIT_PCT, account.monthly_pnl, "RT-LOSS-MONTHLY"),
    ):
        limit = lim(metric)
        loss_pct = pct(-pnl, nav) if pnl < ZERO else ZERO
        if limit is not None and loss_pct >= limit:
            halt(code, "ACCOUNT", account.account_id, loss_pct, limit)
    dd_limit = lim(Metric.MAX_DRAWDOWN_PCT)
    drawdown = pct(account.peak_nav - nav, account.peak_nav) if account.peak_nav > nav else ZERO
    if dd_limit is not None and drawdown >= dd_limit:
        halt("RT-DRAWDOWN", "ACCOUNT", account.account_id, drawdown, dd_limit)
    opm = lim(Metric.ORDERS_PER_MINUTE)
    if opm is not None and Decimal(metrics.orders_last_minute) >= opm * th.abnormal_orders_per_minute_factor:
        halt("RT-FREQ", "ACCOUNT", account.account_id, metrics.orders_last_minute, opm * th.abnormal_orders_per_minute_factor)
    if metrics.slippage_bps_p95 > th.slippage_bps_p95:
        halt("RT-SLIPPAGE", "ACCOUNT", account.account_id, metrics.slippage_bps_p95, th.slippage_bps_p95)
    if metrics.rejection_rate_pct > th.rejection_rate_pct:
        halt("RT-REJECTS", "ACCOUNT", account.account_id, metrics.rejection_rate_pct, th.rejection_rate_pct)
    if metrics.decision_latency_p99_ms > th.decision_latency_p99_ms:
        halt("RT-LATENCY", "PLATFORM", "*", metrics.decision_latency_p99_ms, th.decision_latency_p99_ms)
    if not metrics.broker_connected:
        halt("RT-CONNECTIVITY", "ACCOUNT", account.account_id, False, True)
    if metrics.model_drift_breached:
        halt("RT-DRIFT", "STRATEGY", "*", True, False)
    if metrics.open_reconciliation_breaks > 0:
        halt("RT-RECON", "ACCOUNT", account.account_id, metrics.open_reconciliation_breaks, 0)
    if not metrics.venue_healthy:
        halt("RT-VENUE", "VENUE", "*", False, True)
    return tuple(events)
