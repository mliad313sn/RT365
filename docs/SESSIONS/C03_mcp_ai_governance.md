# Session C3 — MCP & AI Governance (blueprint 04)

**Environment:** dev/sim only. The tool registry is signed with a public dev key; no model provider, hosting or data-processing terms exist [Open: O-05]. Documented by the Program Orchestrator (1st line, recommends, never approves).

## 1 Roles

| Function | Role (line) | Basis |
|---|---|---|
| Accountable | MCP Security Agent (2nd line, controls); Model Risk Lead (2nd line, models) | COMMITTEE_DEEP_DIVE §C3 |
| Consulted | Quant Research Lead, Security Architect, Backend Lead | COMMITTEE_DEEP_DIVE §C3 |
| Builder | Backend Lead (1st line) — `mcp/servers/mcp_servers/*.py`, `libs/core/rtcore/provenance.py`, `services/strategy/strategy_service/*.py`. The MCP Security Agent cannot author MCP servers (roster row 15) and did not. | RACI |
| Challenger (different line) | MCP Security Agent (2nd line) — challenged structural impossibility, signing and revocation; owns `/mcp/policies` as CODEOWNER | Protocol §1.4 rule 4; `.github/CODEOWNERS` |
| Assurance / IVA | Model Risk Committee, Security & Privacy Board, Red-Team Lead (3rd line), Independent Validation Agent | COMMITTEE_DEEP_DIVE §C3 |

Statement: author != reviewer != approver. Backend Lead built; MCP Security Agent challenges and must approve every tool before registration (approval records `MCP-SEC-2026-001..006` are marked "[Committee: pending]" in `mcp/policies/tool_registry.json`); IVA/Red-Team verify. Nothing here is self-certified.

## 2 Purpose

- [Source: 04] Six allowed capabilities (read masked market snapshots, read masked account state, calculate approved indicators, run approved simulations, retrieve strategy documentation, submit a trade intent); forbidden capabilities (direct broker calls, arbitrary code, shell, secret retrieval, risk-policy mutation, audit deletion, unrestricted web, dynamic install in production).
- [Source: 00] AI/MCP may research, analyse, simulate, rank, signal and submit typed trade intents; never credentials, limit changes, self-approval, audit suppression, monitoring disablement, control bypass. Every signal carries thesis code, evidence references and confidence.
- [Committee] Forbidden = structurally impossible: `mcp_servers` imports no execution/broker/vault/kill-switch/policy module (asserted by AST in TC-AI-005), egress allowlist (`mcp/policies/egress.yaml`, `EgressPolicy`), runtime constraints (`runtime.yaml`), signed registry refused when unsigned/tampered, short-lived signed identities, canary tokens, per-tool quota/timeout/payload limits, provenance labels with delimited untrusted text.
- [Open: O-05] providers/hosting; [Open: O-06] evaluation datasets; [Open: O-07] policy numbers (intents in tests use sim fixtures).

## 3 Decisions and ADRs

| # | Decision | Alternatives compared | Why chosen | Evidence |
|---|---|---|---|---|
| C3-D1 | Signed registry (`tool_registry.signed.json`, HMAC-SHA256 over canonical JSON, `key_id`, `algorithm`) loaded by `load_registry`; unsigned or tampered registries raise `RegistryUnsigned`; `scripts/verify_tool_registry.py` enforces exactly six tools, only `submit_trade_intent` write-class with scope naming the queue, positive quotas, egress and runtime invariants; `--production` refuses the dev key. | (a) Unsigned JSON allowlist reviewed by CODEOWNERS only; (b) asymmetric signature (Ed25519/KMS) from day one; (c) chosen: HMAC with a public dev key now, KMS key before Gate B. | (a) has no runtime refusal path; (b) needs the KMS/HSM that is a human provisioning act (MISSING_ACTIONS H-05). HMAC keeps the refusal path testable now; the dev key is documented as public (`security/signing/README.md`, allowlisted in `security/secret_scan_allowlist.txt`) and CI proves it is refused for production (`test_tool_registry_policy_invariants`). | **Proposed ADR-011** [Committee, pending ARB and Security & Privacy Board]; TC-AI-005 |
| C3-D2 | Runtime call chain in one place (`ToolRuntime.call`): identity -> registry -> revocation -> allowlist -> quota -> payload -> input schema -> handler with deadline -> output schema -> canary -> audit. Handlers can only be registered for tools in the signed registry (`register_handler` raises otherwise). | (a) Per-tool decorators; (b) gateway proxy in front of MCP servers; (c) chosen: single runtime invoked by both the MCP path and the BFF (`app.py` routes agent calls through the runtime). | One enforcement surface for both entry points; each stage has an `error_code` that tests assert. | TC-AI-001..004, `test_handlers_cannot_be_added_outside_registry` |
| C3-D3 | Short-lived workload identity (`IdentityIssuer`, default TTL 5 min) with per-token HMAC secret; every call signed over `token_id|tool|hash(args)`; Kill Switch revokes identities by scope (`revoke_scope`). | (a) Static API key per agent; (b) mTLS client certs; (c) chosen: issued tokens with signatures and scope revocation. | (a) cannot be revoked mid-session; (b) is deployment-bound (ADR-006 mesh pending). | TC-AI-003 (forged signature -> IDENTITY), TC-AI-004 (expiry), TC-KS-001 (revocation) |
| C3-D4 | Provenance enum (`rtcore/provenance.py`) with `SIMULATED` marked dev/sim only; `delimit_untrusted` neutralises nested delimiters; only `licensed_feed`/`simulated` are `TRUSTED_FOR_DECISIONS` (risk engine `RK-FRESH-PROV`). | (a) Prompt-level instruction "ignore instructions in data"; (b) chosen: structural labelling + trust set consulted by the deterministic engine. | (a) is not a control; (b) is enforced by code that does not call a model. | TC-AI-002, TC-RK-010 |
| C3-D5 | Explainability contract: `Signal.evidence_refs` (min 1) and `data_provenance` (min 1) are required; `TradeIntent` carries `evidence_refs`, `thesis_code`, `confidence`; `IntentQueue` rejects unknown fields, hallucinated or delisted symbols before any engine runs. | (a) Optional explanation field; (b) chosen: schema-required. | [Source: 00] a signal without evidence references is schema-invalid. | `test_signal_without_evidence_is_schema_invalid`, TC-AI-002 |

ADR references: ADR-001 (analytics plane), ADR-005 (`strategy.signal.v1` schema exported by `scripts/export_event_schemas.py`). Model lifecycle decisions are in P2 (proposed ADR-018).

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| FR-09 | `ToolRuntime`, `ToolRegistry`, `TenantAllowlist`, `build_tools` | Backend Lead | Allowlisted tools, schema validation, masking, quota, payload | TC-AI-001..004, TC-E2E-SCHEMA | `test/quartets/test_tc_ai_mcp.py`, `test/e2e/test_journeys_and_bff.py` | D |
| FR-09 (explainability) | `Signal`, `TradeIntent.evidence_refs` | Backend Lead | Evidence refs required | `test_signal_without_evidence_is_schema_invalid` | `test/integration/test_backtest_single_code_path.py` | D |
| NFR-SEC-01 (no secrets in agent context) | `EgressPolicy`, `runtime.yaml` (`secrets_mount: none`), AST import ban | Backend Lead / MCP Security Agent | Structural impossibility | TC-AI-005, TC-NET-003 | `mcp/policies/*`, `scripts/verify_tool_registry.py` | B |
| FR-07 (sandbox isolation) | `mcp-servers.yaml` egress; `run_simulation` tool runs `run_sim_backtest` on a fresh sim platform | Backend Lead | No vault/broker route from the sandbox | TC-NET-003, TC-AI-005 | `infra/kubernetes/network-policies/mcp-servers.yaml` | B |
| FR-17 (agent token revocation on Kill Switch) | `KillSwitchHooks.revoke_agent_identities` -> `IdentityIssuer.revoke_scope` | Backend Lead | Tokens revoked at activation | TC-KS-001 | `test/quartets/test_tc_ks_killswitch.py` | C |
| NFR-AUD-01 (tool calls audited) | `mcp.tool.called/denied/revoked` audit actions | Backend Lead | Tamper-evident log of every call | TC-AI-001, TC-AI-003, TC-AI-004 | `services/audit/audit_service/store.py` | C |

## 5 Threat-model delta

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| T-01 Prompt/tool injection | B6 | Provenance delimiting; strict intent schema (`extra="forbid"`); symbol validation at the queue | TC-AI-002 | MCP Security Agent |
| T-02 Excessive agency | B3, B6 | Only `submit_trade_intent` is write-class and targets `intent-queue.control` only; broker submissions stay 0 in TC-AI-001 | TC-AI-001, TC-AI-003, TC-AI-005 | MCP Security Agent |
| T-13 Data exfiltration | B6 | Canary tokens in input and output; masked account state (`account_ref` prefix, rounded balances); egress allowlist | TC-AI-003 (canary), TC-AI-001 (masking) | Security Architect |
| T-04 Model supply chain | B8 | Registry signature; model_id/model_version on every signal and intent | TC-AI-005 (partial) | Model Risk Lead |
| NEW T-18 Registry key compromise (dev key is public by design) | B8 | `--production` refusal; KMS key required before Gate B | `test_tool_registry_policy_invariants` | MCP Security Agent (O-27) |
| NEW T-19 Quota exhaustion as denial of service against the intent queue | B3 | Per-tool quota (`submit_trade_intent` 10/min in sim) and `IntentQueue.max_depth` | TC-AI-003 (quota) | SRE Lead |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Tool allowlist & registry | TC-AI-001 `test_allowlisted_tools_work_with_masking` | TC-AI-003 (`NOT_ALLOWLISTED` for research-only strategy) | TC-AI-003 `test_non_allowlisted_tool_denied_and_alerted` (`TOOL_NOT_REGISTERED`, forged signature, oversize payload, canary) | TC-AI-004 `test_revocation_mid_session_and_registry_revocation` (restore registry) |
| Injection defence | TC-AI-002 (benign delimited text passes as data) | TC-AI-002 (unknown field, hallucinated symbol, wrong scope, empty provenance rejected) | TC-AI-003 (canary in input -> `CANARY_DETECTED`) | GAP — no test that a poisoned tool output is rejected by output-schema validation after a handler is compromised |
| Structural impossibility | TC-AI-005 (egress allows intent-queue) | TC-AI-005 (AST import ban) | TC-AI-005 (tampered registry adds `cancel_order` -> `RegistryUnsigned`) | TC-NET-004 (policy restore) |
| Agent identity | TC-AI-001 (signed call accepted) | TC-AI-004 (expired token -> `IDENTITY`) | TC-AI-003 (forged signature -> `IDENTITY`) | TC-KS-004 (`restore_scope` after Kill Switch) |

## 7 Evidence list

- `docs/MCP_TOOL_CATALOG.md`, `docs/PROMPT_REGISTRY.md`, `docs/MODEL_CARDS/TEMPLATE.md` (no model card exists yet), `docs/RED_TEAM_PLAN.md`
- `mcp/policies/{README.md,tool_registry.json,tool_registry.signed.json,allowlist.tenant-sim.yaml,egress.yaml,runtime.yaml}`; `scripts/sign_tool_registry.py`, `scripts/verify_tool_registry.py`
- `mcp/servers/mcp_servers/{registry.py,runtime.py,identity.py,allowlist.py,egress.py,tools.py}`; `libs/core/rtcore/provenance.py`; `services/strategy/strategy_service/{signals.py,registry.py}`
- `test/quartets/test_tc_ai_mcp.py` (TC-AI-001..005), `test/contract/test_openapi_alignment.py::test_tool_registry_policy_invariants`, `test/evidence/evidence_index.json`

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Gate |
|---|---|---|---|---|
| O-27 | Dependency | KMS/HSM-managed registry signing key replaces `DEV_KEY` (`mcp_servers/registry.py:16`); until then the registry is publicly forgeable (T-18) | MCP Security Agent, Security Architect | B |
| O-28 | Gap | Tool approval records `MCP-SEC-2026-001..006` are placeholders; MCP Security Agent review and signature per tool not yet performed | MCP Security Agent | D |
| O-29 | Gap | Prompt-injection evidence is a single delimited string (TC-AI-002); the red-team corpus and hallucination/adversarial evaluation datasets do not exist (O-06) | Red-Team Lead, Model Risk Lead | D |
| R-08 | Risk | `run_simulation` builds a fresh in-process platform per call (quota 6/min, timeout 60 s); in a shared MCP server this is a resource-exhaustion vector (T-19) | SRE Lead, Backend Lead | D |

Assumptions: one sim tenant allowlist (`allowlist.tenant-sim.yaml`); no LLM is called anywhere in the build (the sample strategy is a rule); provenance `simulated` never appears outside dev/sim.

Confidence: **high** for allowlist, revocation, identity and structural-impossibility controls (tests read and assertions traced to code); **low** for model governance (no provider, no model card, no evaluation dataset).

Provenance: [Source: 00, 04] capabilities, prohibitions, explainability; [Committee] ADR-011 proposal, runtime chain, canary design; [Open] O-05, O-06, O-27..O-29. Evidence cited by path; IVA and MCP Security Agent sign-off pending.
