# security/ — Security Architect owned [Source: 06]

| Control | Where | Verified by |
|---|---|---|
| Plane topology, no analytics→execution route | infra/kubernetes/network-policies, rtcore.planes.PlaneGuard | scripts/check_network_policies.py, TC-NET |
| MCP forbidden capabilities structurally impossible | mcp/policies/*, mcp_servers.runtime | scripts/verify_tool_registry.py, TC-AI |
| Signed tool registry | mcp/policies/tool_registry.signed.json (dev key until KMS key exists — MISSING_ACTIONS) | verify_tool_registry.py --production |
| Secrets never in code or agent context | broker_adapters.VaultRef, rtobs.logging.redact | scripts/secret_scan.py, TC-SEC |
| Immutable audit with hash chain | audit_service.AuditStore | TC-AUD |
| SBOM | scripts/generate_sbom.py → security/sbom/ | CI |
| Protected paths | .github/CODEOWNERS | branch protection (human setup) |
| Distribution fails closed (resource root, environment label, fixture registry) | rtcore.resources, rt365_cli.main | TC-PKG-001..004; release workflow smoke tests |
| Agent write scope (author != reviewer != approver for agents) | scripts/agent_guard.py from .claude/agents/roster.json (guard rail, not a control of record) | TC-AGT-001..004; `make agents-check` |

`signing/` documents key custody; no private key material is ever committed.
