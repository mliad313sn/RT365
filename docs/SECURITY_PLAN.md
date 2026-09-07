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
| WAF/DDoS, egress control | Edge + per-plane egress allowlists | Cloud Architect | Chaos/Perf |
| Immutable logs | WORM audit with hash chain | SRE Lead | IVA |
| Backup/restore, incident response | DR_PLAN, INCIDENT_RESPONSE | SRE Lead | drill evidence |
| Red teaming, independent pen-test | Before Gate D and F | Red-Team & Pen-Test Lead | Security & Privacy Board |
