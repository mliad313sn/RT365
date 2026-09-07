# Session C5 — Security, Privacy & Threat Model (blueprint 06)

**Environment:** dev/sim only. No vault, KMS, IdP, WAF, SIEM or pen-test exists; the controls below are code and CI checks. Documented by the Program Orchestrator (1st line, recommends, never approves).

## 1 Roles

| Function | Role (line) | Basis |
|---|---|---|
| Accountable | Security Architect (Architecture tier, 1st line for controls it designs); Privacy Lead (2nd line) | COMMITTEE_DEEP_DIVE §C5 |
| Consulted | MCP Security Agent, Cloud Architect, SRE Lead | COMMITTEE_DEEP_DIVE §C5 |
| Builder | Backend Lead (1st line) — `services/audit/audit_service/store.py`, `services/compliance/compliance_engine/retention.py`, `observability/rtobs/logging.py`, `scripts/{secret_scan.py,generate_sbom.py,check_network_policies.py}`; Security Architect — `security/*`, `.github/CODEOWNERS` | RACI |
| Challenger (different line) | Privacy Lead and MCP Security Agent (2nd line) — challenged redaction placement, legal-hold semantics and dev-key custody | Protocol §1.4 rule 4 |
| Assurance / IVA | Security & Privacy Board (accepts residual risk — the Security Architect cannot accept its own); Red-Team & Pen-Test Leads (3rd line); Independent Validation Agent | COMMITTEE_DEEP_DIVE §C5 |

Statement: author != reviewer != approver. Backend Lead and Security Architect authored; Privacy Lead/MCP Security Agent challenge; Red-Team/Pen-Test and IVA verify; Security & Privacy Board approves. Nothing here is self-certified; no pen-test or red-team report exists (MISSING_ACTIONS H-10).

## 2 Purpose

- [Source: 06] Named threats (prompt/tool injection through data exfiltration), required controls (zero trust through independent penetration testing), privacy obligations (purpose limitation through privacy-safe telemetry).
- [Committee] Eight trust boundaries B1–B8 and the T-01..T-13 table in `docs/THREAT_MODEL.md`; telemetry redaction at emission; legal-hold flags suppress rather than destroy; protected paths need 2nd-line CODEOWNER approval.
- Build scope of this session: immutable hash-chained audit (T-12), secret hygiene and SBOM in CI (T-05, T-10), redaction at emission (NFR-PRV-01), retention with legal hold (O-09), CODEOWNERS for protected paths (T-07), plane and MCP invariants (T-02, T-13; detailed in C2/C3).
- [Open: O-09] legal-hold rules per jurisdiction; [Open: O-10] DPIA per launch jurisdiction; [Open: O-05] data-processing terms.

## 3 Decisions and ADRs

| # | Decision | Alternatives compared | Why chosen | Evidence |
|---|---|---|---|---|
| C5-D1 | Audit store is append-only with a SHA-256 hash chain from `GENESIS_HASH`: each event hashes (seq, event_id, ts, correlation_id, tenant, account, actor, action, payload_hash, prev_hash); `verify()` reports first bad seq and reason; no delete/update/remove method exists; optional JSONL file opened in append mode only. | (a) Database table with row-level permissions; (b) external WORM object store from day one; (c) chosen: in-process chain now, WORM object store with replicated chain head before Gate C (DR_PLAN). | (a) is mutable by a privileged DBA; (b) needs cloud provisioning (H-05). The chain makes tampering detectable in any backend. | ADR-010 (in-process store); TC-AUD-001..004 |
| C5-D2 | Redaction at emission in `JsonFormatter` (`rtobs/logging.py`): emails, bearer tokens, `vault://` refs, 12–19 digit numbers, secret/password/api_key/token assignments; correlation ID on every line. | (a) Redact at storage/SIEM ingest; (b) chosen: at emission. | [Committee C5 §4] data that never leaves the process cannot leak through log shipping. | TC-OB-002 |
| C5-D3 | Legal hold and retention: `RetentionService.request_deletion` returns `SUPPRESSED_LEGAL_HOLD` / `SUPPRESSED_RETENTION` / `DELETED` and audits every decision; holds are placed/released with audit. | (a) Hard delete with exception list; (b) chosen: suppress-not-destroy with logged decision; (c) crypto-shredding. | (a) destroys records under a regulatory duty; (c) is a Gate D design once residency/DPIA (O-10) are known. | **Proposed ADR-020** [Committee, pending Security & Privacy Board and Legal] ; TC-CP-006 |
| C5-D4 | CI security gates (`.github/workflows/ci.yml`): `make policy-check` (planes + registry), `make secret-scan` (regex scanner with an explicit allowlist `security/secret_scan_allowlist.txt`), `make sbom` (CycloneDX 1.5 from installed distributions), evidence artefact upload. | (a) Rely on GitHub-native scanning only; (b) full SAST/DAST/SCA suite now; (c) chosen: lightweight in-repo gates now, dedicated scanners added by Gate B (O-32). | (b) needs tool procurement; (a) is not visible in the evidence index. The dev registry key is the only allowlisted "secret" and is documented as public. | `scripts/secret_scan.py`, `scripts/generate_sbom.py`, `security/sbom/sbom.cdx.json` |
| C5-D5 | Protected paths in `.github/CODEOWNERS`: `/services/risk`, `/services/compliance`, `/services/execution`, `/services/killswitch`, `/mcp/policies`, `/security`, `/contracts`, network policies, and the four policy/matrix docs each require a 2nd-line or 3rd-line handle. | (a) Single reviewers team; (b) chosen: per-path 2nd-line owners plus IVA on risk/compliance/execution/killswitch. | [Source: 13] builder never sole approver. Team handles are placeholders [Open: O-20]. | `.github/CODEOWNERS` |
| C5-D6 | HMAC dev signing of the tool registry with a public dev key refused for production (`verify_tool_registry.py --production`). | See C3-D1. | Custody documented in `security/signing/README.md`; no private key material committed. | **Proposed ADR-011** (C3) |

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| NFR-AUD-01 | `AuditStore` hash chain; every service audits through `audit5/audit3/audit2` hooks | Backend Lead / SRE Lead | Immutable, hash-chained, correlation ID | TC-AUD-001..004 | `test/quartets/test_tc_aud_audit.py` | C |
| NFR-PRV-01 | `rtobs.logging.redact`, `JsonFormatter` | SRE Lead / Privacy Lead | Redaction at emission | TC-OB-002 | `test/quartets/test_tc_ob_observability.py` | C |
| FR-15 (retention) / NFR-PRV-01 | `RetentionService`, `LegalHold`, `RetentionSchedule` | Backend Lead | Suppress under hold/retention; decision audited | TC-CP-006 | `test/quartets/test_tc_cp_eligibility.py` | D |
| NFR-SEC-02 | CI: policy-check, secret-scan, SBOM, evidence upload | Security Architect / Cloud Architect | CI gate | `test_tool_registry_policy_invariants`, TC-NET-003 (runs checker) | `.github/workflows/ci.yml`, `security/sbom/sbom.cdx.json` | B |
| NFR-SEC-01 | Network policies, `PlaneGuard`, MCP egress | Cloud Architect | No analytics -> execution; no secrets in agent context | TC-NET-001..004, TC-AI-005 | C2/C3 packets | B |
| NFR-OBS-01 | Correlation ID in envelope, audit and logs; tracer completeness | SRE Lead | End-to-end correlation | TC-OB-001, TC-OB-003, TC-OB-004 | `observability/rtobs/*` | C |
| NFR-TEN-01 | `CP-TENANT` check, tenant-scoped allowlist, `X-Actor`/tenant checks in approvals | Backend Lead | Tenant mismatch rejected | TC-CP-002 (partial), TC-AI-002 (`SCOPE`) | `services/compliance/compliance_engine/eligibility.py` | C — GAP: no TC-TEN quartet |

## 5 Threat-model delta

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| T-12 Audit tampering | all | Hash chain, append-only API, file append mode, export/reload verification | TC-AUD-002, TC-AUD-003, TC-AUD-004 | SRE Lead |
| T-05 Credential theft | B5 | Secret scan in CI; `vault://` refs redacted; no secrets mount for MCP | `make secret-scan`, TC-OB-002, TC-AI-005 | Security Architect |
| T-10 Dependency compromise | B8 | CycloneDX SBOM generated each CI run; SCA not yet wired | GAP (O-32) | Cloud Architect |
| T-07 Insider misuse | B2/B8 | CODEOWNERS on protected paths; maker-checker | TC-ID-001; branch protection is a human act (O-20) | Security & Privacy Board |
| T-13 Data exfiltration | B2/B6 | Redaction, canary tokens, masked tool outputs | TC-OB-002, TC-AI-003 | Security Architect |
| NEW T-22 Audit file truncation by an OS-level actor (append mode is not WORM) | all | Chain head replication and object-lock storage before Gate C | GAP (R-10) | SRE Lead |
| NEW T-23 Redaction regex bypass (unicode / encoded secrets) | B2 | Pattern list is finite; needs red-team corpus | GAP | Privacy Lead, Red-Team Lead |
| NEW T-24 Deletion request during legal hold interpreted as destroyed | B2 | `SUPPRESSED_*` outcomes, audit of every decision | TC-CP-006 | Privacy Lead, Legal Agent (O-09) |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Immutable audit | TC-AUD-001 `test_every_decision_and_transition_is_audited_with_correlation_id` | TC-AUD-002 `test_no_update_or_delete_api_exists` | TC-AUD-003 `test_tampering_detected_by_hash_chain` (modify, remove, re-hash) | TC-AUD-004 `test_export_reload_and_file_backed_worm` |
| Redaction at emission | TC-OB-001 (log lines carry correlation ID) | TC-OB-002 `test_redaction_at_emission` | GAP — no encoded/obfuscated secret bypass test (T-23) | GAP — no test that a redaction-pattern change is itself audited |
| Retention / legal hold | TC-CP-006 (deletion allowed after hold release and outside retention) | TC-CP-006 (`SUPPRESSED_RETENTION`) | TC-CP-006 (`SUPPRESSED_LEGAL_HOLD`) | TC-CP-006 (hold released -> `DELETED`, three audit events) |
| Secret hygiene / SBOM | CI `make secret-scan`, `make sbom` pass on current tree | `test_tool_registry_policy_invariants` (`--production` refuses dev key) | GAP — no test that a planted secret fails CI | GAP — no rotation drill (T-05 rotation) |
| Protected-path review | CODEOWNERS present for all six blueprint-protected paths | GAP — branch protection not verifiable in-repo (O-20) | GAP — no test that a PR touching `/services/risk` without 2nd-line approval is blocked | GAP |

## 7 Evidence list

- `docs/THREAT_MODEL.md`, `docs/SECURITY_PLAN.md`, `docs/PRIVACY_IMPACT.md`, `docs/SBOM.md`, `docs/DR_PLAN.md`, `docs/INCIDENT_RESPONSE.md`
- `security/README.md`, `security/signing/README.md`, `security/secret_scan_allowlist.txt`, `security/sbom/sbom.cdx.json`; `.github/CODEOWNERS`; `.github/workflows/ci.yml`
- `scripts/secret_scan.py`, `scripts/generate_sbom.py`, `scripts/check_network_policies.py`, `scripts/verify_tool_registry.py`
- `services/audit/audit_service/store.py`, `services/compliance/compliance_engine/retention.py`, `observability/rtobs/logging.py`
- `test/quartets/test_tc_aud_audit.py` (TC-AUD-001..004), `test/quartets/test_tc_ob_observability.py` (TC-OB-001..004), `test/quartets/test_tc_cp_eligibility.py::test_retention_deletion_suppressed_under_legal_hold` (TC-CP-006)

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Gate |
|---|---|---|---|---|
| O-32 | Gap | Dedicated SAST/DAST/SCA and secret scanners are not in CI; `secret_scan.py` is a five-pattern regex; SBOM is generated but not evaluated against vulnerability data | Security Architect, Cloud Architect | B |
| O-33 | Gap | Artefact/image and model-artefact signing tooling (T-04, T-10) unselected; "unsigned deploy refused" is policy text only | Cloud Architect, Model Risk Lead | B |
| O-34 | Gap | No TC-TEN and TC-SEC quartets exist although `docs/TEST_CASES/README.md` defines the areas | QA Lead | C |
| R-10 | Risk | `AuditStore` JSONL backend is append-mode, not WORM; OS-level truncation would be detected only if the chain head is replicated elsewhere (T-22) | SRE Lead | C |
| R-11 | Risk | Redaction patterns are a finite list; encoded secrets or non-Latin PII pass through (T-23) | Privacy Lead, Red-Team Lead | D |

Assumptions: dev/sim runs single-tenant (`tenant-sim`); no real PII is processed; the dev registry key is intentionally public; branch protection and team mapping (O-20) are human acts.

Confidence: **high** for hash-chain detection and legal-hold semantics (tests trace to code); **medium** for redaction (pattern-based); **low** for supply-chain and secret controls (regex scanner, SBOM without SCA, no signing tool).

Provenance: [Source: 06, 07, 13] threats, controls, privacy duties, protected paths; [Committee] boundaries B1–B8, ADR-011/020 proposals, CI gate design; [Open] O-05, O-09, O-10, O-20, O-32..O-34. Evidence cited by path; Security & Privacy Board acceptance and external pen-test pending.
