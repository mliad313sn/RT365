"""UTC clock helpers. Deterministic engines receive ``now`` as an argument; they never read the clock."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


def ensure_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware (UTC)")
    return ts.astimezone(UTC)


def age_seconds(older: datetime, newer: datetime) -> float:
    return (ensure_utc(newer) - ensure_utc(older)).total_seconds()


def age_seconds_decimal(older: datetime, newer: datetime) -> Decimal:
    """Exact age in seconds as a Decimal (``timedelta`` is integral days/seconds/microseconds; no float appears).

    Freshness is a decision input, so it is computed the way money is: exactly [Source: 05; NFR-DET-01].
    """
    delta = ensure_utc(newer) - ensure_utc(older)
    return Decimal(delta.days) * 86400 + Decimal(delta.seconds) + Decimal(delta.microseconds).scaleb(-6)


def seconds(n: float) -> timedelta:
    return timedelta(seconds=n)
