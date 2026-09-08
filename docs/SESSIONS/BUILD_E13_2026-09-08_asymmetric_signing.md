# Build session — E13 asymmetric signing and trust-set rotation (register B-4, delegation D-051)

| Field | Value |
|---|---|
| Date | 2026-09-08 |
| Epic | E13 Security & privacy |
| Register item | B-4 (asymmetric command authorisation and registry signing with rotation; verify-only handles) |
| Authority | D-051 (delegation), D-053 (O-22: asymmetric signing with a public trust set; dev HMAC key dev/sim only), D-058 (store seam) |
| Branch | `build/e13-asymmetric-signing` |
| Author | build agent E13 (AI); the run was terminated by the harness usage limit mid-session (RAID O-124) and completed by the Product Owner delegate: test-fixture corrections, ADR-019 and this packet |
| Reviewer | pending — Security Architect (2nd line), MCP Security Agent (`mcp/policies`), Trading Domain Lead + IVA (`services/execution`) |

## 1 Roles

Backend Lead and Security Architect build; the MCP Security Agent owns `mcp/policies` and the tool registry; the Trading Domain Lead owns `services/execution`; the Independent Validation Agent validates evidence. No approval is recorded here: the human Product Owner decides every gate (D-039) and the AI delegate decides delegated matters (D-040).

## 2 Purpose

Replace both symmetric signature checks with an asymmetric one so that the population that verifies cannot forge [Source: 04, 06]. The tool registry was HMAC-SHA256 with the key held by every verifier, including installers and the CLI; the order-command grant was an in-process HMAC whose verifier was a wrapper around the signing secret (R-44, IVA-22) [Committee]. What remains open after this session is key custody at start-up and the ceremony on real infrastructure [Open: O-53, H-20, O-23].

## 3 Decisions and ADRs

ADR-019 (proposed, written with the change): one key pair per purpose; verifiers hold a public `TrustSet` only; algorithm allowlist before any curve operation; domain separation binds purpose and `key_id` into the signed bytes; rotation is overlap-then-retire with `key_id` never reused; validity checked at `authorised_at`; dev/sim keeps the HMAC paths explicitly; the production private key is KMS/HSM-held and non-exportable. Alternatives and consequences are in the ADR, including why `cryptography` was not added to the closure and what the pure-Python implementation costs.

## 4 Proposed RTM row text (docs/REQUIREMENTS_TRACEABILITY.md; the Program Orchestrator edits the ledger)

| Req | Architecture element | Implementation owner | Control | Test IDs (quartet) | Evidence | Gate | Status |
|---|---|---|---|---|---|---|---|
| NFR-SEC-01 | Asymmetric signing (`rtcore.trust` verify-only, `rtcore.signing` signer-only); `PublicKeyCommandVerifier` in the execution gateway; `TrustSet` in the registry loader (ADR-019) | Security Architect | One key pair per purpose with domain separation; algorithm allowlist before any cryptographic operation; verifiers hold no private material (attribute walk asserted); rotation overlap-then-retire, a retired key verifies nothing; HMAC accepted only when `RT_ENV` is dev or sim | TC-SIG-001..004 | TEST_CASES/TC-SIG.md | B/C | dev/sim: Ed25519 in pure Python, key pairs generated in the test process; KMS/HSM signer, ceremony and rotation drill on real infrastructure [Open: O-53, H-20]; ECDSA P-256 not implemented [Open: Q-22-1]; performance of the pure-Python verifier not measured against NFR-PERF [Open: O-125] |
| FR-13 (addition) | Execution gateway command grant verified by `PublicKeyCommandVerifier` over the order-command trust set | Backend Lead | The gateway holds no signer and no private bytes; the key window is checked at `command.authorised_at`; a retired key is refused absolutely | TC-EX-001..011, TC-SIG-001..004 | TEST_CASES/TC-EX.md, TC-SIG.md | C | dev/sim; default path unchanged (in-process HMAC) so no existing outcome moved |
| FR-09 (addition) | Signed tool registry verified through a public trust set; `scripts/sign_tool_registry.py --ed25519-key/--key-id`, `--dev` for the dev HMAC key | MCP Security Agent | Registry envelope binds `rt365.tool-registry.v1` and `key_id`; algorithm confusion refused in both directions; dev key and any HMAC refused outside dev/sim; absent trust set = empty = refuse | TC-AI-005, TC-SIG-001..004 | TEST_CASES/TC-AI.md, TC-SIG.md | B | dev/sim; the committed registry stays dev-HMAC signed until a real key exists [Open: O-22, H-20] |

## 5 Threat-model delta (proposed rows; the Security Architect owns the file and assigns the T-numbers)

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| A holder of the verification key forges a tool registry or a command grant (symmetric key held by every verifier, including installers and operator machines) | B4, B6 | Asymmetric signatures; verifiers hold public keys only; `rtcore.signing` banned from `mcp_servers` | TC-SIG-001, TC-SIG-003, TC-AI-005 | Security Architect |
| Algorithm confusion: an HMAC envelope claims Ed25519, or an Ed25519 envelope claims HMAC, or an unknown algorithm is offered | B4, B5 | Allowlist checked before any cryptographic operation; the public key is never accepted as an HMAC key; HMAC refused outside dev/sim from any source | TC-SIG-003 | MCP Security Agent |
| Cross-purpose replay: a registry signature presented as a command grant, or a signature by key A replayed under key_id B | B5 | `signed_message(purpose, key_id, message)` binds both into the signed bytes | TC-SIG-003 | Security Architect |
| A compromised or retired key keeps verifying because rotation is only a timestamp | B4 | `retire()` sets `revoked` and refuses absolutely, whatever the timestamps say; `key_id` never reused; overlap is explicit | TC-SIG-004 | Security Architect |
| A signing handle is reachable from a component that must not sign (attribute walk from the gateway verifier, the MCP runtime or the registry) | B5, B6 | `PublicKeyCommandVerifier` holds only a trust set; no `sign`, no seed, nothing in `repr`; asserted by walking the object graph | TC-SIG-003 | Backend Lead |
| Clock skew resurrects a key outside its window | B5 | Validity checked at `command.authorised_at`, itself bounded to `COMMAND_MAX_AGE` around now | TC-SIG-002 | Backend Lead |

## 6 Control quartet

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Asymmetric signing and rotation (TC-SIG, NFR-SEC-01) | **TC-SIG-001** RFC 8032 §7.1 vector 1 matches; a command signed by the pipeline signer verifies with a public-key-only verifier and the intent reaches the broker once; an Ed25519-signed registry loads through the trust set with `dev_key_in_use=False`; the committed registry still verifies on the dev HMAC path in dev/sim | **TC-SIG-002** wrong key, altered payload, unknown `key_id`, key outside its validity window and retired key are each refused with the reason; the gateway raises `CommandNotAuthorised` and nothing reaches the broker | **TC-SIG-003** no seed, signer or `sign` reachable from the gateway verifier, the MCP runtime or the registry, and none appears in any `repr`; an HMAC-signed command presented to an Ed25519-only verifier is refused on the algorithm; key A's signature replayed under `key_id` B is refused; malformed encodings never reach the curve; registry algorithm confusion refused in both directions | **TC-SIG-004** rotation: B added (overlap) — both verify; the composition root re-points the signer and audits the rotation; A retired — A-signed commands are refused and the gateway raises, B's still verify; the registry is re-signed under B through the signing script and the file signed by A is refused; the trust set round-trips through its JSON file |

Existing tests: none weakened. TC-AI-005 (the ban on importing the signer inside `mcp_servers`) now also covers `rtcore.signing`.

## 7 Evidence

- `make all` at the committed tree: lint and format clean, mypy `Success: no issues found in 100 source files`, 21 event schemas unchanged, network policies OK, registry OK (`HMAC-SHA256, key_id=dev-key-v0, dev key`), 67 agents match `goals/`, secret scan clean, **207 passed**; `make evidence` wrote 187 records, **22/22 areas with a full quartet**.
- `make security-scan`: bandit clean at `-lll -ii`; pip-audit on `requirements.lock.txt` — no known vulnerabilities (no dependency added).
- New: `libs/core/rtcore/trust.py` (verify-only: Ed25519 verification, `TrustedKey`, `TrustSet`), `libs/core/rtcore/signing.py` (signer only), `test/quartets/test_tc_sig_signing.py`, `security/signing/trust_set.schema.json`, `security/signing/ceremonies/TEMPLATE.md`, `docs/TEST_CASES/TC-SIG.md`, `docs/ADRs/ADR-019.md`.
- Modified: `services/execution/execution_gateway/authorisation.py` (`Ed25519CommandAuthoriser`, `PublicKeyCommandVerifier`), `mcp/servers/mcp_servers/registry.py` (trust-set verification, purpose, `dev_key_in_use`), `apps/web/web_bff/platform.py` (`command_signer`, `command_trust_set`, `rotate_command_signer`), `scripts/sign_tool_registry.py`, `scripts/verify_tool_registry.py`, `scripts/export_test_cases.py` (SIG area), `security/signing/README.md`, `test/quartets/test_tc_ai_mcp.py`.
- Completion note: the build agent's run ended at the harness usage limit before its own packet existed (RAID O-124). The delegate corrected three test-fixture facts — the trust epoch was set after the sim platform's base time, the sim broker fills immediately so `FILLED` is a valid post-state, and two rotation intents were economic duplicates refused by `RK-DUP` — and wrote ADR-019 and this packet. No implementation logic was changed to make a test pass.

## 8 Proposed RAID updates (the author does not edit the ledger)

| ID | Proposed change |
|---|---|
| O-22 | Status → "Decided (D-053) and built in dev/sim (ADR-019, TC-SIG-001..004): Ed25519 with a public trust set, domain separation, overlap-then-retire rotation; the dev HMAC key is refused outside dev/sim. Open: a real KMS/HSM key with its ceremony (H-20), the committed registry re-signed under it, ECDSA P-256 if the chosen KMS lacks Ed25519 (Q-22-1)." |
| O-53 | Add: "the asymmetric path is built (ADR-019); what remains is custody — who hands the composition root its signer at start-up, from which KMS/HSM, and how rotation is triggered. No private key is persisted anywhere in the repository." |
| R-44 | Status → "Remediated by construction (ADR-019): the gateway holds a `PublicKeyCommandVerifier` over public keys; there is no `sign` to reach and no private bytes in the object graph or in any `repr` (TC-SIG-003). The wrapper-based mitigation is superseded." |
| new | Gap: the pure-Python Ed25519 verifier is not measured against the NFR-PERF budgets; before shadow either a KMS signer or a native verifier must be benchmarked (ADR-019 §Consequences). |
| new | Gap: an absent or malformed trust set refuses everything (fail closed by design) but is a new deployment failure mode; `docs/DEPLOYMENT_RUNBOOK.md` must carry the trust-set file, its owner and its review step. |
| new | Open item: the committed `mcp/policies/tool_registry.signed.json` is still dev-HMAC signed under `dev-key-v0`; re-signing it under a real Ed25519 key is blocked on the ceremony (H-20) and is a 2nd-line CODEOWNER change. |

## 9 Definition of Done — self-assessment

- [ ] Reviewer ≠ author; protected paths approved by a 2nd-line CODEOWNER — pending (Security Architect; MCP Security Agent for `mcp/policies`; Trading Domain Lead + IVA for `services/execution`)
- [x] Control quartet passes for the control touched (TC-SIG-001..004); no existing test weakened
- [x] Evidence record written (`docs/TEST_CASES/TC-SIG.md`; reviewer column pending by construction)
- [x] Security scans clean; no dependency added, SBOM unchanged
- [x] Rollback verified in the lowest environment: the asymmetric path is opt-in (`command_signer=`), the default HMAC path and all prior outcomes are unchanged
- [ ] Documentation and RTM updated — ADR-019 written; RTM/RAID/THREAT_MODEL rows proposed above for the ledger owners
- [x] Not promoted beyond the environment the current gate authorises (dev/sim; no market, strategy or autonomy enabled)

## 10 Concerns for the Product Owner

- **C-1 Key custody is not solved, only prepared.** [Open: O-53] `build_sim_platform(command_signer=...)` models the vault/KMS path; nothing persists a private key and no AI/MCP component receives one. Who supplies the signer at start-up, from which KMS, and how a rotation is triggered in a running deployment are open. Recommendation: fold this into the O-53 decision pack rather than a separate one.
- **C-2 The pure-Python Ed25519 is a deliberate trade.** [Committee] `cryptography` is not in the declared closure and the rule is not to add a runtime dependency; RFC 8032 verification handles public inputs only, so constant-time behaviour is not required for the verifier. The signer is dev/sim material. When the KMS client library arrives it brings a vetted implementation anyway, and the swap touches one module. If the Board prefers a vetted library now, that is a dependency decision for the owner.
- **C-3 Performance is unmeasured.** [Open] Roughly two orders of magnitude slower than a native implementation; invisible at dev/sim volumes (207 tests in ~17 s) and untested against the NFR-PERF decision-latency budget. A benchmark is owed before shadow.
- **C-4 The trust set is now a deployment artefact.** [Open] Absent or malformed means refuse everything. Safe, but the runbook, the CODEOWNERS entry and the installer packaging must all carry it, and none of that exists yet.
- **C-5 The committed registry is still dev-signed.** [Open: H-20] It stays HMAC under `dev-key-v0`, refused outside dev/sim. Re-signing it under a real key needs the ceremony (three distinct humans, KMS-held non-exportable key), which is a human act.
- **C-6 ECDSA P-256 is not implemented.** [Open: Q-22-1] D-053 allowed it as the fallback where a KMS lacks Ed25519. If the chosen provider is in that group, one branch is owed in the allowlist and the verifier.
- **C-7 Protected paths were edited.** [Committee] `services/execution/execution_gateway/authorisation.py` and `mcp/servers/mcp_servers/registry.py` plus `mcp/policies` tooling. Each needs its 2nd-line CODEOWNER; the merge is not an approval.
- **C-8 What the tests do not prove.** [Open] Key pairs are generated in the test process, so nothing here evidences a real ceremony, a real KMS, a rotation on running infrastructure, or an operator following the runbook. The rotation drill on real infrastructure remains a Gate C condition.
