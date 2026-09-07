"""UTC clock helpers. Deterministic engines receive ``now`` as an argument; they never read the clock."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


def ensure_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware (UTC)")
    return ts.astimezone(UTC)


def age_seconds(older: datetime, newer: datetime) -> float:
    return (ensure_utc(newer) - ensure_utc(older)).total_seconds()


def seconds(n: float) -> timedelta:
    return timedelta(seconds=n)
