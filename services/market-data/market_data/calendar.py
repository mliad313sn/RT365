"""Session calendars per venue [Source: 17 items 4]. Sessions are declared in UTC or in the venue's own timezone
(IANA name, D-050 global compatibility); holidays are local dates. Evaluation always happens on a UTC instant."""

from __future__ import annotations

from datetime import date, datetime, time, tzinfo
from zoneinfo import ZoneInfo

from rtcore.clock import ensure_utc
from rtcore.schemas.market import SessionState


class SessionCalendar:
    def __init__(self) -> None:
        self._sessions: dict[str, tuple[time, time]] = {}
        self._holidays: dict[str, set[date]] = {}
        self._zones: dict[str, tzinfo] = {}

    def add_venue(self, venue: str, open_utc: time, close_utc: time, holidays: set[date] | None = None) -> None:
        """A venue whose session is declared in UTC (legacy and simulated venues)."""
        self._sessions[venue] = (open_utc, close_utc)
        self._holidays[venue] = set(holidays or set())
        self._zones[venue] = ensure_utc(datetime(2000, 1, 1, tzinfo=ZoneInfo("UTC"))).tzinfo or ZoneInfo("UTC")

    def add_venue_local(self, venue: str, open_local: time, close_local: time, zone: str, holidays: set[date] | None = None) -> None:
        """A venue whose session and holidays are declared in its own IANA timezone (any country, any continent)."""
        self._sessions[venue] = (open_local, close_local)
        self._holidays[venue] = set(holidays or set())
        self._zones[venue] = ZoneInfo(zone)

    def zone(self, venue: str) -> tzinfo | None:
        return self._zones.get(venue)

    def _local(self, venue: str, ts: datetime) -> datetime:
        return ensure_utc(ts).astimezone(self._zones[venue])

    def state(self, venue: str, ts: datetime) -> SessionState:
        if venue not in self._sessions:
            return SessionState.CLOSED
        local = self._local(venue, ts)
        if local.weekday() >= 5 or local.date() in self._holidays[venue]:
            return SessionState.CLOSED
        o, c = self._sessions[venue]
        t = local.time()
        if o <= t < c:
            return SessionState.OPEN
        return SessionState.PRE_OPEN if t < o else SessionState.CLOSED

    def close_time(self, venue: str, ts: datetime) -> datetime | None:
        if venue not in self._sessions:
            return None
        local = self._local(venue, ts)
        return datetime.combine(local.date(), self._sessions[venue][1], tzinfo=self._zones[venue])
