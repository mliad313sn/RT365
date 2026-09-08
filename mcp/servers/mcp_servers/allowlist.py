"""Per-tenant tool grants and the multi-tenant allowlist store [Source: 04; NFR-TEN-01; RAID R-22].

One ``TenantAllowlist`` per ``mcp/policies/allowlist.<tenant>.yaml``; the ``AllowlistStore`` is a read-only
mapping tenant -> allowlist. Tenant-wide revocation (kind ``tenant``) is persisted through the revocation
list so it survives restarts, and it is lifted only by two distinct human approvers — never by an auto-action.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from rtcore.errors import ControlDenied

from mcp_servers.revocation import RevocationList


class TenantAllowlist:
    """Per tenant/account/strategy tool grants (mcp/policies/allowlist.<tenant>.yaml).

    Grant revocation is scoped to (tenant, account, strategy, tool) and persisted via the revocation
    list (review OBJ-3); tenant-wide revocation is a human two-person action, never an auto-action.
    """

    def __init__(self, data: dict[str, Any], revocations: RevocationList | None = None) -> None:
        self.tenant_id = str(data["tenant_id"])
        self._accounts: dict[str, Any] = data.get("accounts", {})
        self._revocations = revocations or RevocationList()

    @classmethod
    def load(cls, path: Path, revocations: RevocationList | None = None) -> TenantAllowlist:
        return cls(yaml.safe_load(path.read_text(encoding="utf-8")), revocations)

    @staticmethod
    def grant_key(tenant_id: str, account_id: str, strategy_id: str, tool: str) -> str:
        return f"{tenant_id}/{account_id}/{strategy_id}/{tool}"

    @property
    def revoked(self) -> bool:
        return self._revocations.is_revoked("tenant", self.tenant_id)

    def allowed(self, *, tenant_id: str, account_id: str, strategy_id: str, tool: str) -> bool:
        if tenant_id != self.tenant_id:
            return False
        if self.revoked:
            return False
        if self._revocations.is_revoked("grant", self.grant_key(tenant_id, account_id, strategy_id, tool)):
            return False
        strategies = self._accounts.get(account_id, {}).get("strategies", {})
        return tool in strategies.get(strategy_id, {}).get("tools", [])

    def revoke_grant(self, *, account_id: str, strategy_id: str, tool: str, by: str, at: Any, reason: str = "") -> None:
        self._revocations.revoke("grant", self.grant_key(self.tenant_id, account_id, strategy_id, tool), by=by, at=at, reason=reason)

    def restore_grant(self, *, account_id: str, strategy_id: str, tool: str, by: str, at: Any) -> None:
        self._revocations.lift("grant", self.grant_key(self.tenant_id, account_id, strategy_id, tool), by=by, at=at)


class AllowlistStore(Mapping[str, TenantAllowlist]):
    """Read-only mapping tenant_id -> TenantAllowlist plus the tenant-wide revoke/restore control."""

    def __init__(
        self,
        allowlists: Iterable[TenantAllowlist] = (),
        revocations: RevocationList | None = None,
        audit: Callable[[str, dict[str, Any]], object] | None = None,
    ) -> None:
        self._revocations = revocations or RevocationList()
        self._audit = audit or (lambda action, payload: None)
        self._items: dict[str, TenantAllowlist] = {}
        for item in allowlists:
            self.add(item)

    # --- loading --------------------------------------------------------------------------------------------
    @staticmethod
    def load_file(path: Path, revocations: RevocationList | None = None) -> TenantAllowlist:
        """Load ``allowlist.<tenant>.yaml``; the file suffix must equal the ``tenant_id`` inside (fail closed)."""
        name = path.name
        if not (name.startswith("allowlist.") and name.endswith(".yaml")):
            raise ControlDenied(f"allowlist file name {name!r} must be allowlist.<tenant>.yaml")
        expected = name[len("allowlist.") : -len(".yaml")]
        allowlist = TenantAllowlist.load(path, revocations)
        if not expected or allowlist.tenant_id != expected:
            raise ControlDenied(f"allowlist file {name!r} declares tenant {allowlist.tenant_id!r}; suffix and tenant_id must match")
        return allowlist

    @classmethod
    def load_dir(
        cls,
        policies_dir: Path,
        revocations: RevocationList | None = None,
        *,
        tenants: Iterable[str] | None = None,
        audit: Callable[[str, dict[str, Any]], object] | None = None,
    ) -> AllowlistStore:
        """Load every ``allowlist.<tenant>.yaml`` under ``policies_dir`` (or only the named ``tenants``)."""
        revocations = revocations or RevocationList()
        wanted = None if tenants is None else set(tenants)
        paths = (
            sorted(policies_dir.glob("allowlist.*.yaml"))
            if wanted is None
            else [policies_dir / f"allowlist.{t}.yaml" for t in sorted(wanted)]
        )
        store = cls(revocations=revocations, audit=audit)
        for path in paths:
            if not path.exists():
                raise ControlDenied(f"allowlist for tenant {path.name!r} is missing under {policies_dir}")
            store.add(cls.load_file(path, revocations))
        if wanted is not None and set(store) != wanted:
            raise ControlDenied("allowlist store does not cover every requested tenant")
        return store

    def add(self, allowlist: TenantAllowlist) -> None:
        if allowlist.tenant_id in self._items:
            raise ControlDenied(f"duplicate allowlist for tenant {allowlist.tenant_id!r}")
        self._items[allowlist.tenant_id] = allowlist

    # --- Mapping protocol -------------------------------------------------------------------------------------
    def __getitem__(self, tenant_id: str) -> TenantAllowlist:
        return self._items[tenant_id]

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    # --- tenant-wide revocation (persisted; two-person restore) ------------------------------------------------
    def is_tenant_revoked(self, tenant_id: str) -> bool:
        return self._revocations.is_revoked("tenant", tenant_id)

    def revoke_tenant(self, tenant_id: str, *, by: str, at: datetime, reason: str = "") -> None:
        """Every grant of the tenant is refused from the next call on and after any restart."""
        if tenant_id not in self._items:
            raise ControlDenied(f"unknown tenant {tenant_id!r}")
        self._revocations.revoke("tenant", tenant_id, by=by, at=at, reason=reason)
        self._audit(
            "mcp.tenant.revoked",
            {"tenant": tenant_id, "by": by, "reason": reason, "at": at.isoformat(), "correlation_id": f"tenant:{tenant_id}"},
        )

    def restore_tenant(self, tenant_id: str, *, approvers: tuple[str, str], at: datetime) -> None:
        """Two distinct human approvers are required to restore (P4 two-person rule)."""
        if tenant_id not in self._items:
            raise ControlDenied(f"unknown tenant {tenant_id!r}")
        names = tuple(approvers)
        if len(names) != 2 or len(set(names)) != 2 or not all(names):
            raise ControlDenied("tenant restore requires two distinct approvers")
        self._revocations.lift("tenant", tenant_id, by="+".join(names), at=at)
        self._audit(
            "mcp.tenant.restored",
            {"tenant": tenant_id, "by": list(names), "at": at.isoformat(), "correlation_id": f"tenant:{tenant_id}"},
        )
