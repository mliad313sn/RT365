# MCP policies [Source: 04]
Protected path — 2nd-line CODEOWNER (MCP Security Agent) approval required. Nothing here is approved by the role that wrote it [Source: 13].
- `tool_registry.signed.json` — signed allowlist of servers/tools with scopes, masking class, quota, timeout, payload limit, read/write class, owner, approval record. **Today: a sim fixture, HMAC-signed under the documented dev key, refused outside dev/sim; it embodies no approval** [Open: O-127, O-35].
- `tool_registry.json` — the unsigned source of the above. Changing an `approval_record` here has no effect until the registry is re-signed, and the seat that edits an approval record must not be the seat that approves it [Source: 13].
- `trust/registry_keys.json` — the **public** trust set (key_id, algorithm, public key, valid_from/until, revoked, ceremony reference) that the loader checks Ed25519 signatures against. **This file does not exist yet.** Absent means an empty trust set, which refuses every asymmetric signature — fail closed by design [Open: O-141, O-126]. It carries public material only; no private key, seed or HMAC secret ever enters this directory or this repository. Its author must not be its reviewer: either CODEOWNERS names the Security Architect as author and the MCP Security Agent as reviewer for `trust/`, or the file lives under `security/signing/trust/` and the loader is pointed there [Open: MSA-9].
- `allowlist.<tenant>.yaml` — per tenant/account/strategy tool grants; one file per tenant, filename cross-checked against `tenant_id`, duplicates refused. A per-tenant allowlist is an approval record for that tenant, and these files are **not covered by the registry signature** [Open: O-81]. Only `tenant-sim` ships; the second tenant stays a test fixture under `test/fixtures/policies/` until a tenant onboarding process exists [Committee: D-061 (8), O-123].
- `egress.yaml` — egress allowlist (Analytics-plane services only; no vault, no brokers, no arbitrary web). Enforced today by the NetworkPolicy manifests and their union checker; the in-process `EgressPolicy` is loaded by the composition root and is **not on the tool call path** [Open: REVIEW_C3 F-20].
- `runtime.yaml` — read-only FS, no shell, no secrets mount, quotas. **These are declarations**: `rt365 check` and `scripts/verify_tool_registry.py` verify the file says what it must say; nothing enforces them at runtime, and in dev/sim the MCP runtime shares a process with the BFF on a writable filesystem [Open: H-05, MSA-3].

## Emergency revocation — procedure and drill record [Source: 04; mandate of the MCP Security Agent]
**Mechanism.** Revoke the registry signature → every runtime sharing the revocation list refuses at the next call with `REGISTRY_REVOKED`, and still refuses after a restart, because revocations are journalled. Restoring requires **two distinct** named approvers. Scope-level revocation (PLATFORM / TENANT / ACCOUNT / STRATEGY) and per-tool revocation follow the same rule.

**Drill cadence.** Quarterly. **No drill has ever been run** [Open: H-19]. `docs/TEST_CASES/TC-AI.md` TC-AI-003/004/008/015 are tests of the mechanism; a test is not a drill.

**A drill is only a drill if it produces this record**, filed in `docs/AUDIT_EVIDENCE_INDEX.md`:
1. the named human who revoked, the clock time, and the observed denial on a real call;
2. the observed denial **after a restart** of the serving process;
3. the refusal of a single-approver restore, and the success of a restore by two distinct named approvers;
4. once the trust set exists, the retirement of a trust-set key and the observed refusal of the registry signed under it;
5. **the case that is expected to fail today**: a line deleted from `revocations.jsonl` between the revocation and the restart silently un-revokes, because the journal has no digest and no chain [Open: O-55, O-118, O-128]. A drill that does not attempt this is theatre; the record must state that it failed and why, and the same case must pass once the journals move onto the Store seam [Committee: D-061 (6)].

The drill is run by the SRE Lead with operators the Product Owner names; the MCP Security Agent owns the semantics and reviews the record and does not run or sign off the drill [Source: 13].
