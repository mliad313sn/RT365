# MCP policies [Source: 04]
Protected path — 2nd-line CODEOWNER (MCP Security Agent) approval required.
- `tool_registry.signed.json` — signed allowlist of servers/tools with scopes, masking class, quota, timeout, payload limit, read/write class, owner, approval record.
- `allowlist.<tenant>.yaml` — per tenant/account/strategy tool grants.
- `egress.yaml` — egress allowlist (Analytics-plane services only; no vault, no brokers, no arbitrary web).
- `runtime.yaml` — read-only FS, no shell, no secrets mount, quotas.
Emergency revocation: revoke registry signature → all servers refuse at next call; drill quarterly.
