"""Persisted revocation list [Source: 04 emergency revocation; review F/OBJ-3].

Revocations survive process restarts: every entry is appended to a JSON-lines file that each
runtime and issuer reads at start-up. In deployment the file is replaced by the replicated
revocation head pushed over the Control->Analytics ``revocation`` channel.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from rtcore.schemas.base import StrictModel


class Revocation(StrictModel):
    kind: str  # tool | registry | agent | scope | grant
    target: str  # tool name, agent id, "LEVEL:target", "tenant/account/strategy/tool"
    by: str
    at: datetime
    reason: str = ""


class RevocationList:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path
        self._items: list[Revocation] = []
        self._lifted: set[tuple[str, str]] = set()
        if path is not None and path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    if rec.get("lift"):
                        self._lifted.add((rec["kind"], rec["target"]))
                    else:
                        self._items.append(Revocation.model_validate(rec))
                        self._lifted.discard((rec["kind"], rec["target"]))

    def _write(self, rec: dict[str, object]) -> None:
        if self._path is not None:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, default=str) + "\n")

    def revoke(self, kind: str, target: str, *, by: str, at: datetime, reason: str = "") -> Revocation:
        rec = Revocation(kind=kind, target=target, by=by, at=at, reason=reason)
        self._items.append(rec)
        self._lifted.discard((kind, target))
        self._write(rec.model_dump(mode="json"))
        return rec

    def lift(self, kind: str, target: str, *, by: str, at: datetime) -> None:
        """Lifting is a two-person human action at the service layer; the list only records it."""
        self._lifted.add((kind, target))
        self._write({"kind": kind, "target": target, "by": by, "at": at.isoformat(), "lift": True})

    def is_revoked(self, kind: str, target: str) -> bool:
        if (kind, target) in self._lifted:
            return False
        return any(r.kind == kind and r.target == target for r in self._items)

    def active(self, kind: str | None = None) -> tuple[Revocation, ...]:
        return tuple(r for r in self._items if (kind is None or r.kind == kind) and (r.kind, r.target) not in self._lifted)
