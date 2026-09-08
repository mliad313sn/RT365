"""Bitemporal FX snapshot store [Source: 08; F-3]. Same two axes as the market-data store: as-of (the rate's own
``as_of``) and knowledge time (when the platform learned it).

A reader supplies both, so it can never see a snapshot ingested after its knowledge time — the structural defence
against look-ahead (R-03) applied to rates. Unlike ``BitemporalStore`` this store does *not* refuse a query whose
as-of is later than its knowledge time: "value the book as of now with what I knew an hour ago" is exactly the
question reconciliation and replay ask, and answering it with ``None`` (fail closed, NAV UNKNOWN) is safer than
raising inside a valuation. Rates enter only here; no MCP tool and no trade intent can write one.
"""

from __future__ import annotations

from datetime import datetime

from rtcore.clock import ensure_utc
from rtcore.schemas.fx import FxSnapshot


class FxStore:
    def __init__(self) -> None:
        self._rows: list[tuple[datetime, FxSnapshot]] = []  # (knowledge_ts, snapshot), sorted by (as_of, knowledge_ts)

    def put(self, snapshot: FxSnapshot, *, knowledge_ts: datetime) -> None:
        self._rows.append((ensure_utc(knowledge_ts), snapshot))
        self._rows.sort(key=lambda row: (row[1].as_of, row[0]))

    def latest(self, *, as_of: datetime, knowledge_ts: datetime) -> FxSnapshot | None:
        """Latest snapshot with ``as_of <= as_of`` AND ``knowledge_ts <= knowledge_ts``; None when there is none."""
        as_of, knowledge_ts = ensure_utc(as_of), ensure_utc(knowledge_ts)
        best: FxSnapshot | None = None
        for known_at, snap in self._rows:
            if snap.as_of <= as_of and known_at <= knowledge_ts:
                best = snap
            elif snap.as_of > as_of:
                break
        return best

    def count(self) -> int:
        return len(self._rows)
