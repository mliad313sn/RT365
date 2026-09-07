# THREAT_MODEL

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Security Architect | Red-Team & Pen-Test Lead | Security & Privacy Board | B | Draft v1.0 |

## Trust boundaries [Committee]
B1 user↔BFF · B2 BFF↔services · B3 Analytics↔Control plane · B4 Control↔Execution plane · B5 Execution↔broker · B6 MCP server↔tool · B7 data provider↔ingest · B8 CI↔production.

## Threats [Source: 06] → control → test → owner
| ID | Threat | Boundary | Control | Test ID | Owner |
|---|---|---|---|---|---|
| T-01 | Prompt/tool injection | B6 | Provenance labels, delimited untrusted text, allowlisted tools, output schema | TC-AI-002/003 | MCP Security Agent |
| T-02 | Excessive agency | B3, B6 | Write-class tool writes to queue only; no broker route | TC-NET-003 | MCP Security Agent |
| T-03 | Poisoned market data | B7 | Source contracts, outlier policy, cross-source check, freshness | TC-MD-003 | Data Architect |
| T-04 | Model supply-chain compromise | B8 | Signed model artefacts, registry, SBOM | TC-SC-002 | Model Risk Lead |
| T-05 | Credential theft | B5 | Vault/HSM, workload identity, rotation, no secrets in agent context | TC-SEC-001 | Security Architect |
| T-06 | Account takeover | B1 | MFA/passkeys, session controls, anomaly alerts | TC-ID-003 | Backend Lead |
| T-07 | Insider misuse | B2 | Separation of duties, PIM, maker-checker, immutable logs | TC-ID-004 | Security & Privacy Board |
| T-08 | Replay | B3, B4 | Signed intents with expiry, idempotency | TC-EX-003 | Integration Architect |
| T-09 | Duplicate orders / race | B4, B5 | Executor lease + fencing token | TC-EX-002/004 | Integration Architect |
| T-10 | Dependency compromise | B8 | SCA, signed images, SBOM | TC-SC-001 | Cloud Architect |
| T-11 | Denial of service | B1, B7 | WAF/DDoS, backpressure shedding analytics first | TC-PERF-004 | SRE Lead |
| T-12 | Audit tampering | all | WORM, hash chain, restricted delete (none) | TC-AUD-003 | SRE Lead |
| T-13 | Data exfiltration | B6, B2 | Egress allowlist, canary tokens, tenant isolation | TC-AI-004, TC-TEN-003 | Security Architect |
Each row carries the control quartet (positive/negative/abuse/recovery) in TEST_CASES/.
