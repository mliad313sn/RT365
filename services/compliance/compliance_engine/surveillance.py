"""Post-trade surveillance pattern library and strategy-registration screen [Source: 07; C6 §4].

[Committee] The detectors below are deliberately simple, explainable heuristics for the sim
environment; parameters are fixtures pending Compliance & Legal Committee review [Open: O-21].
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from rtcore.money import ZERO
from rtcore.schemas.base import StrictModel
from rtcore.schemas.intent import Side


class OrderEvent(StrictModel):
    order_id: str
    account_id: str
    instrument_id: str
    side: Side
    quantity: Decimal
    price: Decimal
    submitted_at: datetime
    cancelled_at: datetime | None = None
    filled_quantity: Decimal = ZERO
    session_close: datetime | None = None


class SurveillanceAlert(StrictModel):
    pattern: str
    account_id: str
    instrument_id: str
    order_ids: tuple[str, ...]
    detail: str


def _is_buy(side: Side) -> bool:
    return side in (Side.BUY, Side.BUY_TO_COVER)


def surveil(
    events: tuple[OrderEvent, ...],
    *,
    wash_window: timedelta = timedelta(minutes=5),
    spoof_cancel_within: timedelta = timedelta(seconds=10),
    close_window: timedelta = timedelta(minutes=5),
) -> tuple[SurveillanceAlert, ...]:
    alerts: list[SurveillanceAlert] = []
    by_key: dict[tuple[str, str], list[OrderEvent]] = {}
    for e in events:
        by_key.setdefault((e.account_id, e.instrument_id), []).append(e)
    for (acct, inst), evs in by_key.items():
        evs = sorted(evs, key=lambda x: x.submitted_at)
        # Wash trading: opposite-side fills on the same instrument/account within the window at same price.
        for a in evs:
            for b in evs:
                if a.order_id >= b.order_id:
                    continue
                if _is_buy(a.side) != _is_buy(b.side) and a.filled_quantity > ZERO and b.filled_quantity > ZERO:
                    if abs(a.submitted_at - b.submitted_at) <= wash_window and a.price == b.price:
                        alerts.append(
                            SurveillanceAlert(
                                pattern="WASH_TRADE",
                                account_id=acct,
                                instrument_id=inst,
                                order_ids=(a.order_id, b.order_id),
                                detail="opposite-side fills at same price within window",
                            )
                        )
        # Spoofing / layering: large orders cancelled quickly while an opposite-side order fills.
        for a in evs:
            if a.cancelled_at is None or a.filled_quantity > ZERO:
                continue
            if a.cancelled_at - a.submitted_at > spoof_cancel_within:
                continue
            for b in evs:
                if b is a or _is_buy(a.side) == _is_buy(b.side) or b.filled_quantity == ZERO:
                    continue
                if abs(b.submitted_at - a.submitted_at) <= spoof_cancel_within and a.quantity >= b.filled_quantity * 3:
                    alerts.append(
                        SurveillanceAlert(
                            pattern="SPOOFING",
                            account_id=acct,
                            instrument_id=inst,
                            order_ids=(a.order_id, b.order_id),
                            detail="large quickly-cancelled order opposite an executed order",
                        )
                    )
        # Marking the close: fills concentrated in the last minutes of the session.
        for a in evs:
            if a.session_close is not None and a.filled_quantity > ZERO and a.session_close - a.submitted_at <= close_window:
                alerts.append(
                    SurveillanceAlert(
                        pattern="MARKING_THE_CLOSE",
                        account_id=acct,
                        instrument_id=inst,
                        order_ids=(a.order_id,),
                        detail="execution inside the closing window",
                    )
                )
        # Momentum ignition (heuristic): burst of same-side aggressive orders then reversal within window.
        buys = [e for e in evs if _is_buy(e.side)]
        sells = [e for e in evs if not _is_buy(e.side)]
        if len(buys) >= 5 and sells:
            burst_end = buys[4].submitted_at
            if burst_end - buys[0].submitted_at <= timedelta(seconds=30) and any(
                s.submitted_at - burst_end <= timedelta(minutes=2) for s in sells
            ):
                alerts.append(
                    SurveillanceAlert(
                        pattern="MOMENTUM_IGNITION",
                        account_id=acct,
                        instrument_id=inst,
                        order_ids=tuple(e.order_id for e in buys[:5]),
                        detail="burst of same-side orders followed by reversal",
                    )
                )
    return tuple(alerts)


class StrategyDeclaration(StrictModel):
    """Behaviours a strategy declares at registration [C6 §4; SCOPE.md out-of-scope enforcement]."""

    strategy_id: str
    two_sided_resting_quotes: bool = False  # market making — out of scope [Source: 01]
    expected_cancel_ratio: Decimal = ZERO  # cancels / orders
    trades_near_close: bool = False
    replicates_other_accounts: bool = False  # copy trading — out of scope
    provides_personal_advice: bool = False  # out of scope


def screen_strategy_declaration(decl: StrategyDeclaration, *, max_cancel_ratio: Decimal = Decimal("0.8")) -> tuple[str, ...]:
    """Returns rejection reason codes; empty tuple means the declaration passes the screen."""
    reasons: list[str] = []
    if decl.two_sided_resting_quotes:
        reasons.append("CP-SCOPE-MARKET-MAKING")
    if decl.expected_cancel_ratio > max_cancel_ratio:
        reasons.append("CP-SURV-CANCEL-RATIO")
    if decl.trades_near_close:
        reasons.append("CP-SURV-CLOSE")
    if decl.replicates_other_accounts:
        reasons.append("CP-SCOPE-COPY-TRADING")
    if decl.provides_personal_advice:
        reasons.append("CP-SCOPE-ADVICE")
    return tuple(reasons)
