# SECURITY_PLAN

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Security Architect | MCP Security Agent | Security & Privacy Board | B | Draft v1.0 |

Required controls [Source: 06] and implementation owner [Committee]:
| Control | Implementation | Owner | Verified by |
|---|---|---|---|
| Zero trust, mTLS | Mesh on Control/Execution planes (ADR-006), workload identity | Cloud Architect | Pen-Test |
| MFA/passkeys, PIM, separation of duties | Identity service, maker-checker primitive | Backend Lead | Red-Team |
| Signed artefacts, SBOM, SAST/DAST/SCA, secret scanning | CI gates; unsigned deploy refused | Cloud Architect | QA |
| Encryption, tokenisation | KMS-managed keys; tokenised identifiers in analytics | Security Architect | Pen-Test |
| Tenant isolation | Partitioned streams/storage/caches | Backend Lead | Red-Team |
| Secure SDLC | DoR/DoD security items, protected paths | Program Orchestrator | IVA |
| Fail-closed distribution (installer, wheel, one-file executable) | `rtcore.resources` marker check, environment label required, fixture registry refused outside dev/sim, SHA-256 per artefact (signing [Open: O-23]) | Security Architect / SRE Lead | TC-PKG quartet; release workflow |
| Agent segregation (three lines for delivery agents) | Generated roster + PreToolUse write guard; CODEOWNERS remains the control of record | Product Owner / MCP Security Agent | TC-AGT quartet; IVA |
| WAF/DDoS, egress control | Edge + per-plane egress allowlists | Cloud Architect | Chaos/Perf |
| Immutable logs | WORM audit with hash chain | SRE Lead | IVA |
| Backup/restore, incident response | DR_PLAN, INCIDENT_RESPONSE | SRE Lead | drill evidence |
| Red teaming, independent pen-test | Before Gate D and F | Red-Team & Pen-Test Lead | Security & Privacy Board |
