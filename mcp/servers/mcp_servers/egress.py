from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

import yaml
from rtcore.errors import PlaneViolation


class EgressPolicy:
    def __init__(self, allowed_hosts: tuple[str, ...]) -> None:
        self._allowed = allowed_hosts

    @classmethod
    def load(cls, path: Path) -> EgressPolicy:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(tuple(data.get("allowed_hosts", ())))

    def allows(self, host: str) -> bool:
        return any(fnmatch(host, pattern) for pattern in self._allowed)

    def check(self, host: str) -> None:
        if not self.allows(host):
            raise PlaneViolation(f"egress to {host} denied by mcp/policies/egress.yaml")
