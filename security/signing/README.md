# Signing keys [Source: 04, 06] / [Committee: ADR-011, ADR-015, D-053, ADR-019 proposed] / [Open: O-22, O-53, H-20]

Two purposes, two key pairs, one design: the signer holds a private key, every verifier holds only a **public trust set**
keyed by `key_id` (`rtcore.trust.TrustSet`, schema `trust_set.schema.json`). Rotation is overlap-then-retire: add the
new key to the trust set, re-sign under it, retire the old key (`revoked: true`); a retired key verifies nothing.

| Purpose | Signer (private key) | Verifier (public material only) | Trust set | Dev/sim mechanism |
|---|---|---|---|---|
| Tool registry | MCP Security Agent's signing job: `scripts/sign_tool_registry.py --ed25519-key FILE --key-id ID` | `mcp_servers.registry.load_registry` (MCP servers, CLI `rt365 check`, installers) | `mcp/policies/trust/registry_keys.json` (proposed; absent = empty = refuse) | dev HMAC key `dev-key-v0` via `--dev`, accepted only in `RT_ENV` dev/sim |
| Order-command authorisation | the composition root / pipeline identity (`Ed25519CommandAuthoriser`) | `PublicKeyCommandVerifier` in the execution gateway | held by the composition root; a file for the gateway process [Open: O-53] | in-process HMAC `CommandAuthoriser` (default) |
| Risk-policy artefact (R-29) | Chief Risk Agent's policy job [Open] | policy loader [Open] | `risk-policy` purpose reserved in the schema | — |

Rules (no exceptions):
- Verifiers import `rtcore.trust` only; `rtcore.signing` is banned from `mcp_servers` (TC-AI-005) and is imported only by
  composition roots and signing jobs.
- Algorithm allowlist before any cryptographic operation: `Ed25519` through the trust set; `HMAC-SHA256` in dev/sim only.
- Domain separation: every signature binds a purpose string (`rt365.tool-registry.v1`, `rt365.order-command.v1`) and the
  `key_id`, so a registry signature can never pass as a command grant and vice versa.
- No private key is ever committed. Test key pairs are generated in the test process (TC-SIG-001..004). The pure-Python
  Ed25519 signer (standard library only; `cryptography` is not in the declared closure) is dev/sim material; the
  production private key is generated non-exportable in the KMS/HSM and only its public half enters a trust set.
- Ceremony (H-20): three distinct humans (operator, KMS administrator, witness); record in `ceremonies/<key_id>.md`
  from `ceremonies/TEMPLATE.md`; public key and record committed under 2nd-line CODEOWNER review; AUDIT_EVIDENCE_INDEX row.
- Rotation proposal (D-053): 12 months per key, 30-day overlap, immediate on compromise; every rotation is a ceremony record.
- Emergency: `revoked: true` on the compromised key plus a re-signed artefact under a fresh key; the runtime
  `revoke_registry` flag (registry revocation) stays a separate, drilled control.
- Artefact/image signing and model artefact signing (T-04): [Open: O-23] tooling selection at ARB; policy is
  "unsigned deploy refused" (SECURITY_PLAN.md).
