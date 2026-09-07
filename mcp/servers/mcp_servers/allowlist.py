from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class TenantAllowlist:
    """Per tenant/account/strategy tool grants (mcp/policies/allowlist.<tenant>.yaml)."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.tenant_id = str(data["tenant_id"])
        self._accounts: dict[str, Any] = data.get("accounts", {})

    @classmethod
    def load(cls, path: Path) -> TenantAllowlist:
        return cls(yaml.safe_load(path.read_text(encoding="utf-8")))

    def allowed(self, *, tenant_id: str, account_id: str, strategy_id: str, tool: str) -> bool:
        if tenant_id != self.tenant_id:
            return False
        strategies = self._accounts.get(account_id, {}).get("strategies", {})
        return tool in strategies.get(strategy_id, {}).get("tools", [])

    def revoke_tool(self, tool: str) -> None:
        for acct in self._accounts.values():
            for strat in acct.get("strategies", {}).values():
                if tool in strat.get("tools", []):
                    strat["tools"].remove(tool)
