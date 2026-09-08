"""Executor lease with fencing token (ADR-002). One active executor per account.

State lives behind the ``rtcore.store.Store`` seam (ADR-010): the fencing counter is a store sequence, so a
token is never reissued lower after a restart, and ``acquire``/``preempt`` run inside a store transaction so two
executors on one store cannot both hold a live lease [Open: R-05 replicated CP store before shadow].
"""

from __future__ import annotations

from datetime import datetime, timedelta

from rtcore.errors import RTError
from rtcore.schemas.base import StrictModel
from rtcore.store import MemoryStore, Store


class LeaseHeld(RTError):
    """Another executor holds a live lease for this account."""


class Lease(StrictModel):
    account_id: str
    executor_id: str
    fencing_token: int
    acquired_at: datetime
    expires_at: datetime


class LeaseStore:
    """Strongly consistent lease store. In-process by default; SQLite in dev/sim with ``store_dir``; production backs it with a CP store [Committee; ADR-010]."""

    def __init__(self, store: Store | None = None, *, table: str = "execution.leases") -> None:
        self._store: Store = store or MemoryStore()
        self._table = table

    def _read(self, account_id: str) -> Lease | None:
        raw = self._store.get(self._table, account_id)
        return Lease.model_validate_json(raw) if raw is not None else None

    def _write(self, lease: Lease) -> Lease:
        self._store.put(
            self._table, lease.account_id, lease.model_dump_json(), correlation_id=f"lease:{lease.account_id}:{lease.executor_id}"
        )
        return lease

    def _issue(self, account_id: str, executor_id: str, now: datetime, ttl: timedelta) -> Lease:
        token = self._store.next_sequence(f"fencing:{account_id}", correlation_id=f"lease:{account_id}:{executor_id}")
        return self._write(
            Lease(account_id=account_id, executor_id=executor_id, fencing_token=token, acquired_at=now, expires_at=now + ttl)
        )

    def acquire(self, account_id: str, executor_id: str, *, now: datetime, ttl: timedelta = timedelta(seconds=30)) -> Lease:
        with self._store.transaction():
            cur = self._read(account_id)
            if cur is not None and cur.executor_id != executor_id and cur.expires_at > now:
                raise LeaseHeld(f"account {account_id} leased by {cur.executor_id} until {cur.expires_at.isoformat()}")
            if cur is not None and cur.executor_id == executor_id and cur.expires_at > now:
                return self._write(cur.model_copy(update={"expires_at": now + ttl}))
            return self._issue(account_id, executor_id, now, ttl)

    def preempt(self, account_id: str, executor_id: str, *, now: datetime, ttl: timedelta = timedelta(seconds=30)) -> Lease:
        """Kill Switch / failover: issue a new token unconditionally; the previous holder's token becomes stale."""
        with self._store.transaction():
            return self._issue(account_id, executor_id, now, ttl)

    def renew(self, account_id: str, executor_id: str, *, now: datetime, ttl: timedelta = timedelta(seconds=30)) -> Lease | None:
        with self._store.transaction():
            cur = self._read(account_id)
            if cur is None or cur.executor_id != executor_id or cur.expires_at <= now:
                return None
            return self._write(cur.model_copy(update={"expires_at": now + ttl}))

    def release(self, account_id: str, executor_id: str) -> None:
        with self._store.transaction():
            cur = self._read(account_id)
            if cur is not None and cur.executor_id == executor_id:
                self._store.delete(self._table, account_id, correlation_id=f"lease:{account_id}:{executor_id}")

    def current(self, account_id: str) -> Lease | None:
        return self._read(account_id)

    def is_valid(self, account_id: str, fencing_token: int, *, now: datetime) -> bool:
        cur = self._read(account_id)
        return cur is not None and cur.fencing_token == fencing_token and cur.expires_at > now
