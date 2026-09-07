# MCP_TOOL_CATALOG

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| MCP Security Agent | Security Architect | Security & Privacy Board | B | Draft v1.0 |

Allowed capabilities [Source: 04]; attributes [Committee]. Anything not listed is forbidden and structurally impossible (no broker route, no secrets, read-only FS, no shell, egress allowlist).

| Tool | Class | Scope | Masking | Quota / timeout / payload | Owner | Status |
|---|---|---|---|---|---|---|
| read_market_snapshot | read | instrument list within entitlement | unlicensed fields removed | per-tenant quota, 2s, 1 MB | Data Engineering Lead | Proposed — implemented in sim (`mcp_servers.tools`), registration pending MCP Security Agent review |
| read_account_state | read | account | identifiers masked; balances rounded per policy | per-account quota, 2s, 256 KB | Backend Lead | Proposed — implemented in sim (`mcp_servers.tools`), registration pending MCP Security Agent review |
| calculate_indicator | read | approved indicator registry only | — | quota, 5s, 1 MB | Quant Research Lead | Proposed — implemented in sim (`mcp_servers.tools`), registration pending MCP Security Agent review |
| run_simulation | read | approved simulation templates, pinned snapshot | — | queued, 60s, 5 MB | Quant Research Lead | Proposed — implemented in sim (`mcp_servers.tools`), registration pending MCP Security Agent review |
| get_strategy_docs | read | strategy registry docs | — | quota, 2s, 512 KB | Product Director | Proposed — implemented in sim (`mcp_servers.tools`), registration pending MCP Security Agent review |
| submit_trade_intent | **write** (queue only) | strategy/account allowlist | — | rate limit per strategy, 2s, 32 KB | Backend Lead | Proposed — implemented in sim (`mcp_servers.tools`), registration pending MCP Security Agent review |

Forbidden [Source: 04]: direct broker calls, arbitrary code execution, shell access, secret retrieval, risk-policy mutation, audit deletion, unrestricted web access, dynamic installation in production.

Registration process: proposal → threat-model delta → sandbox tests (injection corpus, escalation, oversize payload, revoked call) → signature → per-tenant allowlist → quarterly re-attestation.

Dev/sim status [Committee]: all six tools are implemented behind `mcp_servers.runtime.ToolRuntime` (identity → signed registry → revocation → allowlist → quota → payload → input schema → handler deadline → output schema → canary → tamper-evident log). Registry signed with the documented dev key [Open: O-22]. Independent review: SESSIONS/REVIEW_C3_mcp_security_agent.md.
