"""Durable control-state store: the adapter seam named by ADR-010 [Source: 03; Committee: ADR-010; ADR-018 proposed; R-05].

Every control invariant that must outlive a process (executor lease and its fencing counter, outbox and inbox,
the gateway's order / decision / consumed-grant indexes, Kill Switch activations) sits behind one narrow
``Store`` protocol: namespaced key/value rows, a monotonic sequence, a transaction and an integrity check.

``MemoryStore`` is the dev/sim default and behaves exactly like the dict-based stores it replaces.
``SqliteStore`` keeps the rows in one SQLite file (WAL, ``synchronous=FULL``). Every mutation is appended to a
hash-chained journal carrying the caller's ``correlation_id``, and every row carries its own digest: an edited
value is refused at read time, a deleted or inserted row and a rewritten history are refused at open (the
journal is replayed and compared with the state). Fail closed: any SQLite error surfaces as ``StoreError`` and
no caller proceeds. Replicated Postgres and a Kafka-compatible outbox relay replace these implementations
before shadow [Open: R-05]. The digests hold no secret: they are tamper-evident, not tamper-proof against an
attacker with write access who re-computes them [Open: ADR-018 concern C-3].
"""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Protocol

from rtcore.errors import RTError

GENESIS = "genesis"
SEQUENCE_TABLE = "__sequence"
_SEP = "\x1f"


class StoreError(RTError):
    """The store could not be read or written; every caller fails closed."""


class StoreIntegrityError(StoreError):
    """A row or the journal does not match its digest: the store is refused."""


def row_digest(table: str, key: str, value: str, seq: int) -> str:
    return sha256(_SEP.join((table, key, value, str(seq))).encode("utf-8")).hexdigest()


def journal_digest(prev: str, seq: int, op: str, table: str, key: str, value: str, correlation_id: str, at: str) -> str:
    return sha256(_SEP.join((prev, str(seq), op, table, key, value, correlation_id, at)).encode("utf-8")).hexdigest()


class Store(Protocol):
    """Namespaced rows with a journal. Values are opaque strings (JSON by convention); keys are unique per table."""

    def get(self, table: str, key: str) -> str | None: ...

    def put(self, table: str, key: str, value: str, *, correlation_id: str = "-") -> None: ...

    def delete(self, table: str, key: str, *, correlation_id: str = "-") -> None: ...

    def items(self, table: str) -> tuple[tuple[str, str], ...]: ...

    def next_sequence(self, name: str, *, correlation_id: str = "-") -> int: ...

    def transaction(self) -> AbstractContextManager[None]: ...

    def verify(self) -> None: ...

    def dump(self) -> tuple[tuple[str, str, str], ...]: ...

    def close(self) -> None: ...


class MemoryStore:
    """In-process store: the dev/sim default. Same interface, no durability, no digests (nothing to tamper with from outside)."""

    def __init__(self) -> None:
        self._tables: dict[str, dict[str, str]] = {}
        self._lock = threading.RLock()
        self.journal: list[tuple[str, str, str, str]] = []  # (op, table, key, correlation_id)

    def get(self, table: str, key: str) -> str | None:
        return self._tables.get(table, {}).get(key)

    def put(self, table: str, key: str, value: str, *, correlation_id: str = "-") -> None:
        with self._lock:
            self._tables.setdefault(table, {})[key] = value
            self.journal.append(("put", table, key, correlation_id))

    def delete(self, table: str, key: str, *, correlation_id: str = "-") -> None:
        with self._lock:
            self._tables.get(table, {}).pop(key, None)
            self.journal.append(("delete", table, key, correlation_id))

    def items(self, table: str) -> tuple[tuple[str, str], ...]:
        return tuple(self._tables.get(table, {}).items())

    def next_sequence(self, name: str, *, correlation_id: str = "-") -> int:
        with self._lock:
            current = int(self.get(SEQUENCE_TABLE, name) or 0) + 1
            self.put(SEQUENCE_TABLE, name, str(current), correlation_id=correlation_id)
            return current

    @contextmanager
    def transaction(self) -> Iterator[None]:
        with self._lock:
            yield

    def verify(self) -> None:
        return None

    def dump(self) -> tuple[tuple[str, str, str], ...]:
        return tuple((table, key, value) for table, rows in self._tables.items() for key, value in rows.items())

    def close(self) -> None:
        return None


class SqliteStore:
    """One SQLite file per platform (WAL, synchronous=FULL) with a hash-chained journal and per-row digests.

    Two connections on the same file see one truth (a lease acquired by one process is held for the other);
    ``BEGIN IMMEDIATE`` serialises writers so a fencing counter can never be issued twice.
    """

    def __init__(self, path: Path, *, verify: bool = True, busy_timeout_s: float = 5.0) -> None:
        self._path = Path(path)
        self._lock = threading.RLock()
        self._depth = 0
        self._failed = False
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self._path), isolation_level=None, check_same_thread=False, timeout=busy_timeout_s)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=FULL")
            self._conn.execute(f"PRAGMA busy_timeout={int(busy_timeout_s * 1000)}")
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS kv (tbl TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, "
                "created_seq INTEGER NOT NULL, seq INTEGER NOT NULL, digest TEXT NOT NULL, PRIMARY KEY (tbl, key))"
            )
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS journal (seq INTEGER PRIMARY KEY, op TEXT NOT NULL, tbl TEXT NOT NULL, key TEXT NOT NULL, "
                "value TEXT NOT NULL, correlation_id TEXT NOT NULL, at TEXT NOT NULL, prev TEXT NOT NULL, digest TEXT NOT NULL)"
            )
        except sqlite3.Error as exc:
            raise StoreError(f"cannot open store at {self._path}: {type(exc).__name__}") from exc
        if verify:
            self.verify()

    @property
    def path(self) -> Path:
        return self._path

    # --- plumbing -----------------------------------------------------------------------------------------
    def _execute(self, sql: str, params: tuple[object, ...] = ()) -> sqlite3.Cursor:
        try:
            return self._conn.execute(sql, params)
        except sqlite3.Error as exc:
            raise StoreError(f"store operation failed: {type(exc).__name__}: {exc}") from exc

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Reentrant: nested blocks join the outermost transaction; any exception inside rolls the whole thing back."""
        with self._lock:
            if self._depth == 0:
                self._failed = False
                self._execute("BEGIN IMMEDIATE")
            self._depth += 1
            try:
                yield
            except BaseException:
                self._failed = True
                raise
            finally:
                self._depth -= 1
                if self._depth == 0:
                    try:
                        self._execute("ROLLBACK" if self._failed else "COMMIT")
                    except StoreError:
                        if not self._failed:
                            raise

    @staticmethod
    def _check_row(table: str, key: str, value: str, seq: int, digest: str) -> None:
        if row_digest(table, key, value, seq) != digest:
            raise StoreIntegrityError(f"row digest mismatch: {table}/{key} at seq {seq} (fail closed)")

    def _append(self, op: str, table: str, key: str, value: str, correlation_id: str) -> int:
        last = self._execute("SELECT seq, digest FROM journal ORDER BY seq DESC LIMIT 1").fetchone()
        seq, prev = (int(last[0]) + 1, str(last[1])) if last else (1, GENESIS)
        at = datetime.now(tz=UTC).isoformat()
        digest = journal_digest(prev, seq, op, table, key, value, correlation_id, at)
        self._execute(
            "INSERT INTO journal (seq, op, tbl, key, value, correlation_id, at, prev, digest) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (seq, op, table, key, value, correlation_id, at, prev, digest),
        )
        return seq

    # --- rows -----------------------------------------------------------------------------------------------
    def get(self, table: str, key: str) -> str | None:
        with self._lock:
            row = self._execute("SELECT value, seq, digest FROM kv WHERE tbl = ? AND key = ?", (table, key)).fetchone()
            if row is None:
                return None
            value, seq, digest = str(row[0]), int(row[1]), str(row[2])
            self._check_row(table, key, value, seq, digest)
            return value

    def put(self, table: str, key: str, value: str, *, correlation_id: str = "-") -> None:
        with self.transaction():
            seq = self._append("put", table, key, value, correlation_id)
            existing = self._execute("SELECT created_seq FROM kv WHERE tbl = ? AND key = ?", (table, key)).fetchone()
            created = int(existing[0]) if existing else seq
            self._execute(
                "INSERT OR REPLACE INTO kv (tbl, key, value, created_seq, seq, digest) VALUES (?, ?, ?, ?, ?, ?)",
                (table, key, value, created, seq, row_digest(table, key, value, seq)),
            )

    def delete(self, table: str, key: str, *, correlation_id: str = "-") -> None:
        with self.transaction():
            self._append("delete", table, key, "", correlation_id)
            self._execute("DELETE FROM kv WHERE tbl = ? AND key = ?", (table, key))

    def items(self, table: str) -> tuple[tuple[str, str], ...]:
        with self._lock:
            rows = self._execute("SELECT key, value, seq, digest FROM kv WHERE tbl = ? ORDER BY created_seq", (table,)).fetchall()
            out = []
            for key, value, seq, digest in rows:
                self._check_row(table, str(key), str(value), int(seq), str(digest))
                out.append((str(key), str(value)))
            return tuple(out)

    def next_sequence(self, name: str, *, correlation_id: str = "-") -> int:
        with self.transaction():
            current = int(self.get(SEQUENCE_TABLE, name) or 0) + 1
            self.put(SEQUENCE_TABLE, name, str(current), correlation_id=correlation_id)
            return current

    def dump(self) -> tuple[tuple[str, str, str], ...]:
        with self._lock:
            rows = self._execute("SELECT tbl, key, value, seq, digest FROM kv ORDER BY created_seq").fetchall()
            for table, key, value, seq, digest in rows:
                self._check_row(str(table), str(key), str(value), int(seq), str(digest))
            return tuple((str(t), str(k), str(v)) for t, k, v, _, _ in rows)

    # --- integrity ----------------------------------------------------------------------------------------------
    def verify(self) -> None:
        """Replay the journal (chain check) and compare the result with the state rows; raise on any difference."""
        with self._lock:
            rows = self._execute("SELECT seq, op, tbl, key, value, correlation_id, at, prev, digest FROM journal ORDER BY seq").fetchall()
            prev = GENESIS
            expected: dict[tuple[str, str], tuple[str, int]] = {}
            for n, (seq, op, table, key, value, corr, at, p, digest) in enumerate(rows, start=1):
                if (
                    int(seq) != n
                    or str(p) != prev
                    or journal_digest(prev, int(seq), str(op), str(table), str(key), str(value), str(corr), str(at)) != str(digest)
                ):
                    raise StoreIntegrityError(f"journal chain broken at seq {seq} (fail closed)")
                prev = str(digest)
                if op == "put":
                    expected[(str(table), str(key))] = (str(value), int(seq))
                elif op == "delete":
                    expected.pop((str(table), str(key)), None)
                else:
                    raise StoreIntegrityError(f"unknown journal op at seq {seq} (fail closed)")
            actual: dict[tuple[str, str], tuple[str, int]] = {}
            for table, key, value, seq, digest in self._execute("SELECT tbl, key, value, seq, digest FROM kv").fetchall():
                self._check_row(str(table), str(key), str(value), int(seq), str(digest))
                actual[(str(table), str(key))] = (str(value), int(seq))
            if actual != expected:
                differing = sorted(set(actual) ^ set(expected)) or sorted(k for k in actual if actual[k] != expected[k])
                raise StoreIntegrityError(
                    f"state does not match the journal: {len(differing)} row(s), first {differing[0][0]}/{differing[0][1]} (fail closed)"
                )

    def close(self) -> None:
        with self._lock:
            try:
                self._conn.close()
            except sqlite3.Error as exc:  # pragma: no cover - close failures are not control decisions
                raise StoreError(f"store close failed: {type(exc).__name__}") from exc
