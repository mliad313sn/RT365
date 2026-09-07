# Signing keys

- Tool registry: HMAC-SHA256 with `RT_MCP_REGISTRY_KEY`. The dev key inside `mcp_servers/registry.py`
  is public and is refused by `scripts/verify_tool_registry.py --production`. Production keys live in
  the KMS/HSM (security namespace) and are used only by the MCP Security Agent's signing job.
- Artefact/image signing and model artefact signing (T-04): [Open] tooling selection at ARB; policy is
  "unsigned deploy refused" (SECURITY_PLAN.md).
