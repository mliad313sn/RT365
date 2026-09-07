"""Bitemporal snapshot store [Source: 08; C7 §1]: as-of (market_ts) and knowledge (ingest_ts) time.

A reader supplies both times; it can never see a snapshot ingested after its knowledge time.
This is the structural defence against look-ahead bias (R-03).
"""

from __future__ import annotations

from bisect import bisect_right
from datetime import datetime

from rtcore.errors import RTError
from rtcore.schemas.market import MarketSnapshot


class LookAheadViolation(RTError):
    """A reader asked for data beyond its knowledge time."""


class BitemporalStore:
    def __init__(self) -> None:
        self._rows: dict[str, list[MarketSnapshot]] = {}  # instrument -> sorted by (market_ts, ingest_ts)

    def put(self, snapshot: MarketSnapshot) -> None:
        rows = self._rows.setdefault(snapshot.instrument.instrument_id, [])
        rows.append(snapshot)
        rows.sort(key=lambda s: (s.market_ts, s.ingest_ts))

    def latest(self, instrument_id: str, *, as_of: datetime, knowledge_ts: datetime) -> MarketSnapshot | None:
        """Latest snapshot with market_ts <= as_of AND ingest_ts <= knowledge_ts."""
        if as_of > knowledge_ts:
            raise LookAheadViolation(f"as_of {as_of.isoformat()} is after knowledge time {knowledge_ts.isoformat()}")
        best: MarketSnapshot | None = None
        for s in self._rows.get(instrument_id, []):
            if s.market_ts <= as_of and s.ingest_ts <= knowledge_ts:
                best = s
            elif s.market_ts > as_of:
                break
        return best

    def series(self, instrument_id: str, *, start: datetime, end: datetime, knowledge_ts: datetime) -> tuple[MarketSnapshot, ...]:
        if end > knowledge_ts:
            raise LookAheadViolation("series end is after knowledge time")
        return tuple(s for s in self._rows.get(instrument_id, []) if start <= s.market_ts <= end and s.ingest_ts <= knowledge_ts)

    def market_timestamps(self, instrument_id: str) -> tuple[datetime, ...]:
        keys = sorted({s.market_ts for s in self._rows.get(instrument_id, [])})
        return tuple(keys)

    def count(self, instrument_id: str) -> int:
        return len(self._rows.get(instrument_id, []))

    def next_after(self, instrument_id: str, ts: datetime) -> datetime | None:
        keys = list(self.market_timestamps(instrument_id))
        i = bisect_right(keys, ts)
        return keys[i] if i < len(keys) else None

    def snapshot_id_for_range(self, instrument_id: str, start: datetime, end: datetime) -> str:
        """Reproducible data snapshot reference [Source: 08]: hash of the rows in range."""
        from rtcore.ids import hash_of

        rows = [s.model_dump(mode="json") for s in self._rows.get(instrument_id, []) if start <= s.market_ts <= end]
        return "ds_" + hash_of(rows)[:16]
