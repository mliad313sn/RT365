"""Executor lease with fencing token (ADR-002). One active executor per account."""

from __future__ import annotations

from datetime import datetime, timedelta

from rtcore.errors import RTError
from rtcore.schemas.base import StrictModel


class LeaseHeld(RTError):
    """Another executor holds a live lease for this account."""


class Lease(StrictModel):
    account_id: str
    executor_id: str
    fencing_token: int
    acquired_at: datetime
    expires_at: datetime


class LeaseStore:
    """Strongly consistent lease store. In-process here; production backs it with a CP store [Committee; ADR-010]."""

    def __init__(self) -> None:
        self._leases: dict[str, Lease] = {}
        self._tokens: dict[str, int] = {}

    def acquire(self, account_id: str, executor_id: str, *, now: datetime, ttl: timedelta = timedelta(seconds=30)) -> Lease:
        cur = self._leases.get(account_id)
        if cur is not None and cur.executor_id != executor_id and cur.expires_at > now:
            raise LeaseHeld(f"account {account_id} leased by {cur.executor_id} until {cur.expires_at.isoformat()}")
        if cur is not None and cur.executor_id == executor_id and cur.expires_at > now:
            renewed = cur.model_copy(update={"expires_at": now + ttl})
            self._leases[account_id] = renewed
            return renewed
        token = self._tokens.get(account_id, 0) + 1
        self._tokens[account_id] = token
        lease = Lease(account_id=account_id, executor_id=executor_id, fencing_token=token, acquired_at=now, expires_at=now + ttl)
        self._leases[account_id] = lease
        return lease

    def preempt(self, account_id: str, executor_id: str, *, now: datetime, ttl: timedelta = timedelta(seconds=30)) -> Lease:
        """Kill Switch / failover: issue a new token unconditionally; the previous holder's token becomes stale."""
        token = self._tokens.get(account_id, 0) + 1
        self._tokens[account_id] = token
        lease = Lease(account_id=account_id, executor_id=executor_id, fencing_token=token, acquired_at=now, expires_at=now + ttl)
        self._leases[account_id] = lease
        return lease

    def release(self, account_id: str, executor_id: str) -> None:
        cur = self._leases.get(account_id)
        if cur is not None and cur.executor_id == executor_id:
            del self._leases[account_id]

    def current(self, account_id: str) -> Lease | None:
        return self._leases.get(account_id)

    def is_valid(self, account_id: str, fencing_token: int, *, now: datetime) -> bool:
        cur = self._leases.get(account_id)
        return cur is not None and cur.fencing_token == fencing_token and cur.expires_at > now
