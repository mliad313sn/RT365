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

## Servers and transports [Committee; ADR-016]
| Server | Transport | Where | Identity | Exposes | Status |
|---|---|---|---|---|---|
| `rt365-sim` (`.mcp.json`) | MCP stdio, JSON-RPC 2.0 one frame per line (`mcp_servers.stdio`, `rt365 mcp-serve --env sim`) | agent host machine (Claude Code or any MCP client) | issued by the host process for `agent-claude-code` on `tenant-sim`/`acct-sim-001`/`strat-sma-xover@0.1`; never client-asserted | tools/list and tools/call for the six registered tools only; no resources, prompts or sampling; 1 MiB frame cap; per-tool payload/quota/timeout inside the runtime | implemented in sim (TC-AI-012..015); registration pending MCP Security Agent review with the tools (REVIEW_C3, O-35) |
| BFF agent route (`POST /v1/intents` with bearer + call signature) | HTTPS | `apps/web` | signed MCP identity | `submit_trade_intent` only | implemented in sim (TC-E2E-API) |
Both transports call `ToolRuntime.call`; there is no third path to a tool. Forbidden servers for any agent context: broker, vault/secrets, shell, arbitrary web, limit/mode/audit mutation.
