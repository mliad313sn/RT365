from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

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

    def allowed(self, *, tenant_id: str, account_id: str, strategy_id: str, tool: str) -> bool:
        if tenant_id != self.tenant_id:
            return False
        if self._revocations.is_revoked("grant", self.grant_key(tenant_id, account_id, strategy_id, tool)):
            return False
        strategies = self._accounts.get(account_id, {}).get("strategies", {})
        return tool in strategies.get(strategy_id, {}).get("tools", [])

    def revoke_grant(self, *, account_id: str, strategy_id: str, tool: str, by: str, at: Any, reason: str = "") -> None:
        self._revocations.revoke("grant", self.grant_key(self.tenant_id, account_id, strategy_id, tool), by=by, at=at, reason=reason)

    def restore_grant(self, *, account_id: str, strategy_id: str, tool: str, by: str, at: Any) -> None:
        self._revocations.lift("grant", self.grant_key(self.tenant_id, account_id, strategy_id, tool), by=by, at=at)
