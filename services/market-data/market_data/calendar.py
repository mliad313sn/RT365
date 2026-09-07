"""Session calendars per venue [Source: 17 items 4]. Minutes are UTC; holidays are dates."""

from __future__ import annotations

from datetime import date, datetime, time

from rtcore.clock import ensure_utc
from rtcore.schemas.market import SessionState


class SessionCalendar:
    def __init__(self) -> None:
        self._sessions: dict[str, tuple[time, time]] = {}
        self._holidays: dict[str, set[date]] = {}

    def add_venue(self, venue: str, open_utc: time, close_utc: time, holidays: set[date] | None = None) -> None:
        self._sessions[venue] = (open_utc, close_utc)
        self._holidays[venue] = set(holidays or set())

    def state(self, venue: str, ts: datetime) -> SessionState:
        ts = ensure_utc(ts)
        if venue not in self._sessions:
            return SessionState.CLOSED
        if ts.weekday() >= 5 or ts.date() in self._holidays[venue]:
            return SessionState.CLOSED
        o, c = self._sessions[venue]
        t = ts.time()
        if o <= t < c:
            return SessionState.OPEN
        return SessionState.PRE_OPEN if t < o else SessionState.CLOSED

    def close_time(self, venue: str, ts: datetime) -> datetime | None:
        if venue not in self._sessions:
            return None
        return datetime.combine(ensure_utc(ts).date(), self._sessions[venue][1], tzinfo=ensure_utc(ts).tzinfo)
