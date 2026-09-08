# COUNCIL_2026-09-08_gate_B_security_privacy — Security & Privacy Board decision packs and verdicts for O-05, O-22, O-23 (Gate B)

| Council | Date | Member | Line | Status |
|---|---|---|---|---|
| Security & Privacy Board (advisory; convened by the Product Owner delegate under D-040/D-051) | 2026-09-08 | Board chair (`approve-security-privacy-board-chair`, generated from goals/approvers/A5_security_privacy_board_chair.md; AI) hearing security-architect (presenting), privacy-lead, mcp-security-agent, red-team-pentest-lead; counsel: counsel-ai-safety, counsel-platform-reliability | approver (independent chair, 2nd/3rd-line view) | recommendation, decision pending |

> This packet is a technical approval within the Board's delegated scope (threat model, security plan, residual-risk recommendations, MCP servers and tool registration, secrets and signing keys, DPIA, pen-test scope, agent roster and write-scope guard). It records no Product Owner decision. Nothing in it asserts a vendor's terms, certifications, capabilities or prices; every such point is a question with the source to consult and stays [Open] until the evidence file exists. Nothing here promotes any environment: Gate B authorises development and simulation only [Source: 12]. Profit is an objective, never a promise.

## 0. Scope check, inputs, checks run

### 0.1 Segregation (procedure step 1) [Verified]
| Item | Author | Reviewer | Approver (this packet) | Distinct? |
|---|---|---|---|---|
| ADR-011 (registry signing) | MCP Security Agent presenting / Delivery Orchestrator (AI) | pending (Security Architect per SECURITY_PLAN reviewer column) | Board chair | yes |
| ADR-015 (command authorisation, O-53/R-44) | Delivery Orchestrator (AI) | pending (committee) | Board chair (only the signing-key aspects; ARB owns the rest) | yes |
| ADR-016 (agents, guard, distribution) | Delivery Orchestrator (AI) | pending (MCP Security Agent, Security Architect) | Board chair (agent roster, write-scope guard, signing aspects) | yes |
| goals/decisions/O-05_decision_pack.md; goals/external/model_provider_procurement.md | Model Risk Lead + Privacy Lead (prompt owners) | — | Board chair | yes |
| ci.yml / release.yml / Makefile scan targets | Cloud Architect / Delivery Orchestrator (AI) | pending | Board chair | yes |
The chair authored, reviewed or specified none of the items above; no recusal. The chair's write scope is docs/SESSIONS/, docs/RAID_LOG.md, docs/AUDIT_EVIDENCE_INDEX.md, docs/PO_DECISION_QUEUE.md (roster.json, [Verified]); on the convener's instruction only this file is written — every other edit is proposed below for the owning role.

### 0.2 Read [Verified: file reads 2026-09-08, HEAD d1ccb21 with uncommitted working-tree changes noted in §5.3]
GOAL.md; docs/PRODUCT_OWNER.md; docs/PO_DECISION_QUEUE.md (O-05, O-22, O-23, H-05, H-06, H-20, H-24, gate table); goals/decisions/O-05_decision_pack.md; goals/external/model_provider_procurement.md; docs/ADRs/ADR-011.md, ADR-015.md, ADR-016.md; docs/SECURITY_PLAN.md; docs/THREAT_MODEL.md (T-01..T-13, T-29, T-38..T-51); docs/SBOM.md; security/README.md; security/signing/README.md; security/secret_scan_allowlist.txt; mcp/servers/mcp_servers/registry.py; scripts/sign_tool_registry.py; scripts/verify_tool_registry.py; services/execution/execution_gateway/authorisation.py; .github/workflows/ci.yml; .github/workflows/release.yml; Makefile (`security-scan`, `lock`, `sbom`); installer/README.md, install.sh, install.ps1; mcp/policies/egress.yaml, runtime.yaml; docs/PRIVACY_IMPACT.md; docs/MODEL_CARDS/rule-sma.md; docs/PROMPT_REGISTRY.md; docs/RAID_LOG.md (O-05, O-22, O-23, O-35, O-36, O-53, O-58, R-40, R-44, R-46, R-47, R-48, remediation rows for O-22/O-23/O-35); docs/IMPROVEMENT_REGISTER.md (A-7, A-11, A-18, B-4, B-15, E-1, E-2, E-5); docs/GLOBAL_COMPATIBILITY.md (residency row); docs/DECISION_LOG.md (D-008, D-028..D-051); docs/GATE_REPORTS/GATE_B_2026-09-07.md (IVA-07, IVA-13, IVA-14), REVALIDATION_2026-09-07_0cbc895.md (IVA-07 closed dev/sim); docs/SESSIONS/REVIEW_C3_mcp_security_agent.md (OBJ-2, F-19, F-20, A-C3-1), REVIEW_C5_C1_C9_security_redteam.md (F-14..F-17 via RAID map); apps/cli/rt365_cli/agent_guard.py; .claude/agents/approve-security-privacy-board-chair.md (frontmatter hooks); .claude/settings.json; docs/TEST_CASES/EVIDENCE_REPORT.md rows TC-AI-005/010/011, TC-AGT-001..004, TC-PKG-001..004; docs/AUDIT_EVIDENCE_INDEX.md rows 15, 26, 28.

### 0.3 Checks run (verbatim) [Verified 2026-09-08]
```
$ RT_ENV=sim python scripts/verify_tool_registry.py
NOTE: registry is a sim FIXTURE (approvals pending); it embodies no approval and is refused outside dev/sim
OK: registry 0.1.0 (dev key), 6 tools, policies consistent
exit=0
$ python scripts/verify_tool_registry.py --production
FAIL: dev signing key / fixture registry refused for production: no RT_MCP_REGISTRY_KEY configured and RT_ENV='production' is not a dev/sim environment; refusing the dev key
exit=1
$ RT_ENV=shadow python scripts/verify_tool_registry.py
FAIL: no RT_MCP_REGISTRY_KEY configured and RT_ENV='shadow' is not a dev/sim environment; refusing the dev key
exit=1
$ RT_ENV=production RT_MCP_REGISTRY_KEY=dev-only-registry-key-replace-before-gate-B python scripts/verify_tool_registry.py
FAIL: the published dev key is black-listed outside dev/sim (RT_ENV='production')
exit=1
$ RT_ENV=sim python -m pytest test/quartets/test_tc_ai_mcp.py test/quartets/test_tc_ai_stdio.py test/quartets/test_tc_agt_agent_guard.py test/quartets/test_tc_pkg_cli.py -p no:cacheprovider
23 passed in 1.08s
$ RT_ENV=sim make lint policy-check agents-check secret-scan
All checks passed!
540 files already formatted
OK: network policies satisfy plane invariants (TC-NET)
OK: registry 0.1.0 (dev key), 6 tools, policies consistent
OK: 67 agents in .claude/agents match goals/
OK secret scan: 544 files, no findings
```
The `--production` refusal required by the Board's evidence list holds in all four configurations tried (unset key, non-dev label, dev key supplied explicitly) [Verified]. `make security-scan` was not run as a gate because it cannot fail by construction (`|| true` in the Makefile) [Verified: Makefile lines 44-46]; bandit 1.9.4 and pip-audit 2.10.1 are installed in this environment [Verified].

### 0.4 What the blueprint fixes for all three items [Source]
- [Source: 00] AI/MCP components never hold broker credentials, limit write paths, audit deletion, monitoring disablement or mode changes; only the deterministic Execution Gateway submits orders. This applies to any model provider exactly as to any MCP tool: a provider is an Analytics-plane dependency, never a Control- or Execution-plane one.
- [Source: 04] Tool registry signed; unsigned or tampered registry refused; MCP servers have no secrets mount, read-only filesystem, no shell, egress allowlist; every prompt and model version inventoried (PROMPT_REGISTRY, MODEL_CARDS); provenance labels on untrusted text.
- [Source: 06] Signed artefacts, SBOM, SAST/DAST/SCA and secret scanning gate CI; "unsigned deploy refused"; KMS-managed keys; residency/transfer mapping, DPIA where required, privacy-safe telemetry.
- [Source: 12, 13] Gate B authorises development and simulation only; approvals are recorded by humans; agents never self-certify; author != reviewer != approver.
- [Owner: D-039/D-040] The Product Owner (delegate agent under D-040) decides; this Board recommends. External facts (vendor terms, certificates, licences) stay [Open] until evidenced (PRODUCT_OWNER.md §5).

### 0.5 Council members heard (procedure step 3) [Committee]
No separate member packet was written in this session. The chair records each member's position from the artefacts that role owns and from its prior packets, tagged as such; where a member has not written on a point the chair says so. The Independent Validation finding is quoted from its own reports. Dissent is recorded per item.

| Member | Line | Source of the position heard |
|---|---|---|
| security-architect (presenting) | 2nd | SECURITY_PLAN.md, THREAT_MODEL.md, security/README.md, security/signing/README.md, ADR-011 threat delta |
| privacy-lead | 2nd | PRIVACY_IMPACT.md (AI-context row, residency, retention), GLOBAL_COMPATIBILITY.md residency row (F-7), RAID O-09/O-10 |
| mcp-security-agent | 2nd | REVIEW_C3_mcp_security_agent.md (OBJ-2 registry trust root; F-19/F-20 egress; A-C3-1 no LLM wired), mcp/policies/*, ADR-011 (presenter) |
| red-team-pentest-lead | 3rd | REVIEW_C5 findings F-14..F-17 (SBOM, CI scanners, unpinned dependencies, compose secret) as mapped in RAID_LOG; RED_TEAM_PLAN items RT-01 (O-36) |
| counsel-ai-safety | counsel | GOAL.md posture; MODEL_CARDS/rule-sma.md prohibited use; PROMPT_REGISTRY rules |
| counsel-platform-reliability | counsel | release.yml smoke tests; TC-PKG quartet; ADR-016 §4 |
| Independent Validation Agent | 3rd | GATE_B_2026-09-07 IVA-07, IVA-13, IVA-14; REVALIDATION_2026-09-07_0cbc895 (IVA-07 CLOSED dev/sim, O-22 open); COUNCIL_2026-09-08_gate_A_iva |

---

## 1. O-05 — Model providers, hosting and data-processing terms

### 1.1 What the blueprint fixes and what it leaves open
Fixed [Source: 00, 04, 06]: a model provider is an Analytics-plane dependency; it may receive only masked, provenance-labelled context and returns text or typed signals that go through schema validation, eligibility, deterministic risk and the gateway before anything is executed; it never receives secrets, broker routes, limit write paths, audit-delete or mode-change capabilities (the "never" list of GOAL.md). Every model and prompt version is registered and evaluated before promotion (MODEL_CARDS, PROMPT_REGISTRY). Residency and transfer mapping, retention and DPIA belong to the Privacy Lead per jurisdiction.
Open [Source: O-05 pack]: which provider(s); API versus self-hosted; residency and retention terms per region; fallback provider; cost.
Verified state of the build [Verified]: no LLM is wired (REVIEW_C3 A-C3-1; MODEL_CARDS/rule-sma.md is a deterministic fixture; PROMPT_REGISTRY rows P-STRAT-SIGNAL and P-RESEARCH-SUMM carry `Model: [Open: O-05]`); `mcp/policies/egress.yaml` lists four cluster-local hosts only; `verify_tool_registry.py` refuses any egress host containing `vault`, `execution` or `broker` or a wildcard; PRIVACY_IMPACT "AI context" row: purpose analytics, residency per cell, retention short, "masked account state only". The in-process `EgressPolicy` is loaded but not called on any path (REVIEW_C3 F-20) [Committee], so today the only egress control is the NetworkPolicy plus the registry check.

### 1.2 The invariant every option must satisfy (Board rule, non-negotiable) [Source: 00, 04; Committee]
**No model provider — API or self-hosted — ever receives a secret, a broker route, a limit write path, an audit-delete path or a mode-change path.** Concretely:
1. Provider calls originate only from the Analytics plane through one provider gateway service; the gateway's identity holds no vault token (`runtime.yaml secrets_mount: none`), and the provider API key is injected into the gateway process by the platform secret store, never into an agent context, prompt, tool output or log (T-05, T-13).
2. The provider host appears in `mcp/policies/egress.yaml` only as the gateway's cluster-local name (for example `llm-gateway.analytics.svc.cluster.local`); the gateway's own egress allowlist names the provider endpoint(s) per region; NetworkPolicy denies every other destination (T-20, T-21).
3. Context sent to a provider is the masked account state and provenance-labelled text already defined for MCP tools (`masking` per tool, `delimit_untrusted`), never raw identifiers, credentials, IBANs, IPs or audit payloads (T-24 redaction patterns apply at the gateway boundary as well).
4. Provider output is untrusted text: it can only become a `strategy.signal.v1` or a research summary through schema validation; it can never call a tool outside the six registered ones, never write to anything but the intent queue, and never reach the Control or Execution planes (T-01, T-02; TC-NET-003).
5. Outage or refusal of the provider fails closed to Observe (no signals, no intents); a fallback provider is used only under identical terms and the same gateway.

### 1.3 Data-processing and residency questions per region (Privacy Lead, for counsel and the vendor) [Open]
The platform must be *capable* in every country while *enabled* per cell (D-050). For a provider decision the questions below are asked once per provider and answered per region before that region's DPIA (O-10). None of these lines asserts that a law applies to the operating entity; applicability is a counsel question (H-04). Sources to consult: the provider's data-processing addendum, its trust/data-residency documentation, its sub-processor list, its security attestations and audit reports, and external counsel per cell.

| # | Question (per provider) | Regions where it is asked first (first-cell hypothesis D-043 fixes the country later, Q-11-1) | Source to consult |
|---|---|---|---|
| Q-05-1 | Does the provider offer a contractual "no training on customer data" and zero (or bounded) retention of prompts and outputs? What is the retention period for abuse monitoring and can it be reduced or waived? | all | provider DPA / enterprise terms; provider trust documentation |
| Q-05-2 | Which processing regions does the provider offer as a contractual commitment (not a best effort), and can the gateway pin a region per tenant `residency_region`? | EU/EEA, UK, Switzerland, US, Canada, Brazil, Japan, Singapore, Australia, India, UAE/KSA, South Africa, Korea, China/Hong Kong (each [Open]) | provider residency documentation; DPA annex |
| Q-05-3 | What transfer mechanism does the provider rely on for cross-border processing and does it fit the tenant's cell (for example adequacy decision, standard contractual clauses, UK addendum/IDTA, Swiss addendum, Brazil LGPD transfer clauses, other local mechanisms)? Is a transfer impact assessment needed? | EU/EEA, UK, CH, BR, and any cell whose law restricts transfers [Open: counsel per cell] | DPA transfer annex; external counsel (H-04) |
| Q-05-4 | Is the provider a processor or an independent controller for any purpose (abuse monitoring, service improvement, legal compliance)? | all | DPA role clause |
| Q-05-5 | Sub-processor list, notice period for changes, and objection right; are sub-processors located outside the pinned region? | all | provider sub-processor list |
| Q-05-6 | Which independent attestations or certifications does the provider hold, for which scope and date, and will it share the reports under NDA? (Names of frameworks are questions, not assertions.) | all | provider trust portal; audit reports |
| Q-05-7 | Does the provider offer a data-residency-bound deployment (dedicated region, private endpoint, customer-managed keys) and at what cost model (per token, per hour, committed capacity)? | regions with localisation expectations [Open: counsel] | provider pricing page and enterprise sales; input to the cost model O-13 (H-05) |
| Q-05-8 | Does any data localisation or sectoral rule in the cell prohibit sending financial-account-derived context abroad even when masked? | cells such as China, India, Russia, KSA, Indonesia, Vietnam are commonly cited in this respect — treat as questions, not facts | external counsel per cell (Q-J series, H-04) |
| Q-05-9 | Are financial-services outsourcing or third-party-risk expectations in the cell (for example notification, audit rights, exit plan) triggered by using a model provider, and does the DPA grant audit and exit rights? | every cell with a regulated entity (first cell after Q-11-1) | external counsel; regulator guidance |
| Q-05-10 | Data-subject rights: can the provider delete on request within the retention window, and does it log access to stored prompts? | all | DPA rights clause; O-09 |
| Q-05-11 | Security: encryption in transit and at rest, key custody, incident-notification time, penetration-test evidence, vulnerability disclosure | all | provider security documentation; SECURITY_PLAN "Encryption" row |
| Q-05-12 | Model governance: version pinning with a deprecation notice period; change log; evaluation reproducibility; will a pinned version remain available long enough for the champion/challenger cycle (PROMPT_REGISTRY rules)? | all | provider model lifecycle policy |
| Q-05-13 | Rate limits, SLAs, and regional failover behaviour — does failover ever leave the pinned region? | all | provider SLA |
| Q-05-14 | Prohibited-use and financial-advice clauses in the provider's usage policy: does the intended use (signal generation for a supervised, control-enveloped trading workflow; no personalised advice to retail) fit? | all | provider usage policy; counsel-ai-safety |

### 1.4 Options
| Option | Description | Pros | Cons | Cost | Risk | Reversibility | Controls / tests affected |
|---|---|---|---|---|---|---|---|
| 0 (baseline, not recommended as the end state) | No LLM until Gate D; rule-based fixtures only; decide providers with the Model Risk Committee at Gate D | nothing to secure now; zero vendor exposure | every LLM-dependent story (E03/E04 strategy agents, research summarisation, O-36 injection corpus against a real model) stays blocked; Gate D would open with an untested provider path | none now | schedule risk; the injection and model-test suites (C10 §5) cannot start | trivial | none |
| A | One external API provider (enterprise tier), called directly from the strategy service | fastest to wire; one contract | vendor lock-in; no fallback; the provider endpoint would sit in the strategy service's egress; residency depends on one vendor's regions | [Open: Q-05-7] per-token pricing — question to Finance with the vendor's price list | single point of failure; a provider outage stalls analytics; terms may not fit every region | medium (prompts and evaluation harness are vendor-specific) | egress.yaml; T-13; TC-AI-004; PROMPT_REGISTRY |
| **B (recommended)** | Provider-agnostic **model gateway** service in the Analytics plane: primary external API provider plus a second provider as fallback, both under the terms of §1.3; region pinned per tenant `residency_region`; provider adapters behind one interface; self-hosted open-weights adapter as a later option for cells where §1.3 answers require it | keeps every §1.2 invariant in one place (secrets, egress, masking, provenance, fail-closed); provider swap without touching strategy code; residency enforced by the gateway not by each caller; fallback under identical terms | one more service; two contracts to negotiate; evaluation harness must run per provider/version | two enterprise agreements [Open: Q-05-7, H-05]; gateway build effort M (E03/E13) | provider terms may still not fit a given region → that region stays without LLM features (fail closed to Observe), which is acceptable under D-050 capability-not-availability | high (adapters are replaceable; self-host adapter is the exit path) | new NetworkPolicy for the gateway; egress.yaml (gateway host); T-01, T-05, T-13, T-20, T-21, T-24; TC-AI-002/003/004; new quartet TC-AI-016..019 (§1.7); PRIVACY_IMPACT AI-context row; MODEL_CARDS per model; PROMPT_REGISTRY model column |
| C | Self-hosted open-weights models in the tenant's region from day one (own GPU capacity or a managed-inference platform) | strongest residency and retention control (no third-party processor for prompts); no per-token vendor terms | capacity cost and operations [Open: H-05]; model quality and safety evaluations become the platform's own burden; managed-inference platforms reintroduce a processor and the same §1.3 questions; the capacity model (O-13) does not exist yet | highest fixed cost [Open] | operational risk (GPU supply, patching, model updates); Model Risk workload | medium (models are swappable; infrastructure is not) | same as B plus SECURITY_PLAN "Encryption" and DR rows; SBOM must inventory model weights (T-04) |

### 1.5 Council positions heard [Committee]
- security-architect: B — the gateway is the only design in which the provider secret, the egress allowlist and the redaction boundary are one enforcement point that the existing checker (`verify_tool_registry.py` egress rule) and NetworkPolicy checker can test; A places a provider endpoint in a service that also holds strategy state.
- privacy-lead: B with the §1.3 questions answered per region before any region is enabled; the PRIVACY_IMPACT "AI context" row must gain a "processor" column and a per-region transfer mechanism; C is the fallback for any region where Q-05-2/Q-05-3/Q-05-8 cannot be satisfied.
- mcp-security-agent: B, on condition that the gateway is not an MCP tool and cannot be called by an agent identity directly (it is an internal dependency of the strategy/research services), and that the in-process `EgressPolicy` (F-20) is wired on the gateway's call path so the allowlist is enforced in code as well as by NetworkPolicy.
- red-team-pentest-lead: whichever option, RT-01 (prompt injection against the real prompt and model, O-36) must run against the chosen provider before Gate D; the injection corpus must include exfiltration attempts through the provider (canary tokens seeded into context, F-11).
- counsel-ai-safety: the provider's usage policy must be checked against the intended use (Q-05-14); model output must keep the "no advice to retail" posture of D-045 (Retail Supervised OFF).
- counsel-platform-reliability: B's fallback must be tested as a recovery case (provider outage → fallback → both down → Observe), never as a silent switch of region.
- Different-line challenge (red-team-pentest-lead, 3rd line): "Why not Option 0 — nothing forces a vendor before Gate D?" Answer heard: the injection, hallucination and unsafe-tool-selection suites (C10 §5) need a real model to exist before Gate D, and building them against an unpinned provider at Gate D is the higher risk; B decides the *shape* now and lets the *vendor* stay [Open] until H-06. Dissent: none recorded; the challenge is accepted as a condition (no vendor wiring before the §1.3 answers and H-06).
- Independent Validation: no finding on O-05 beyond IVA-13 ("needed by Gate B and open"); IVA notes no LLM is wired, so all existing evidence is model-independent [Source: GATE_B_2026-09-07 IVA-13; REVIEW_C3 A-C3-1].

### 1.6 Recommendation and confidence
**Option B.** Confidence: **medium-high** on the posture and architecture (it follows directly from [Source: 00, 04, 06] and the existing controls); **none** on any vendor fact — provider names, regions, retention terms, certifications and prices are all [Open: Q-05-1..14, H-06, H-05]. Provenance: [Source: 00, 04, 06] / [Committee: this packet, REVIEW_C3, PRIVACY_IMPACT] / [Open: vendor facts].

### 1.7 Draft DECISION_LOG line (for the delegate to record; number provisional)
`| D-052 | 2026-09-08 | O-05: model providers — adopt the provider-agnostic model gateway posture (Option B): every LLM/ML provider is an Analytics-plane dependency reached only through one gateway service that holds the provider credential, pins the processing region per tenant residency_region, applies masking and provenance labels, enforces the egress allowlist in code and by NetworkPolicy, and fails closed to Observe on outage; primary plus fallback provider under identical data-processing terms (no training, bounded retention, contractual region, processor role, sub-processor notice, audit and exit rights); no provider ever receives a secret, broker route, limit write path, audit-delete or mode-change path; self-hosted adapter as the exit path for regions whose answers to Q-05-1..14 do not fit. Provider names, terms and prices stay [Open] until H-06/H-05 evidence exists; no provider is wired before the Security & Privacy Board sees the signed terms and the region mapping. | Product Owner agent under D-040 · Council: Security & Privacy Board COUNCIL_2026-09-08_gate_B_security_privacy §1 (APPROVE WITH CONDITIONS) · Dissent: none (3rd-line challenge "defer to Gate D" accepted as a condition) | Option 0 defer entirely (rejected: model-test suites need a real model before Gate D); Option A single direct provider (rejected: no fallback, credential and egress spread into the strategy service); Option C self-host first (deferred: no capacity model O-13, kept as exit path) | [Source: 00, 04, 06] / [Committee] / [Open: Q-05-1..14, H-05, H-06] | this packet; PRIVACY_IMPACT AI-context row; PROMPT_REGISTRY; MODEL_CARDS |`

### 1.8 Artefact edits implied (proposed to the owning roles; not made here)
| Artefact | Owner | Edit |
|---|---|---|
| docs/ADRs/ADR-018 (new) "Model gateway: provider-agnostic, region-pinned, fail-closed" | Enterprise Architect / Security Architect | context, decision (§1.2 invariants), alternatives (§1.4), threat delta (T-01, T-05, T-13, T-20, T-21, T-24 rows gain the gateway boundary; new boundary B9 gateway↔provider), tests TC-AI-016..019 |
| docs/THREAT_MODEL.md | Security Architect | add boundary B9 "model gateway↔provider" and row T-52 "Provider-side retention or training on masked context; region drift on failover; credential exposure through prompt/log" → control = gateway-only credential, region pin, redaction at boundary, no-training terms → test TC-AI-016..019 |
| docs/SECURITY_PLAN.md | Security Architect | new row "Model provider boundary — gateway-only credential, per-region endpoint, egress allowlist in code and NetworkPolicy, redaction at the boundary; verified by TC-AI-016..019 and pen-test (Gate D)" |
| docs/PRIVACY_IMPACT.md | Privacy Lead | AI-context row: add processor (provider, role), transfer mechanism per region, retention at the provider, and "[Open: Q-05-1..14]"; DPIA input for O-10 |
| mcp/policies/egress.yaml (protected path) | MCP Security Agent, 2nd-line CODEOWNER | add `llm-gateway.analytics.svc.cluster.local` only when the gateway exists; the provider's public endpoint never appears here |
| docs/PROMPT_REGISTRY.md, docs/MODEL_CARDS/ | Model Risk Lead | model column filled per registered provider/version after H-06; evaluation results before any promotion |
| docs/TEST_CASES/TC-AI.md | QA / Backend Lead | quartet TC-AI-016 (positive: masked, labelled context reaches the gateway; output only via schema), TC-AI-017 (negative: provider host outside the gateway allowlist refused; unpinned region refused), TC-AI-018 (abuse: canary token or secret pattern in outbound context blocked and alerted; agent identity calling the gateway directly refused), TC-AI-019 (recovery: primary outage → fallback same region; both down → Observe, no intents) |
| docs/RED_TEAM_PLAN.md | Red-Team Lead | RT-01 against the real prompt and model (O-36) scheduled before Gate D |
| docs/MISSING_ACTIONS.md / PO_DECISION_QUEUE §B | delegate | H-06 reworded: "answer Q-05-1..14 per provider and region, then sign terms and DPA"; H-05 budget input |

### 1.9 Human actions required
- H-06 (Gate B, sign terms/DPA): before signing, obtain the provider's answers to Q-05-1..14 and file them under docs/EXTERNAL/ (evidence file), Privacy Lead review, Board review of the region mapping [Open].
- H-05 (budget): cost inputs from Q-05-7 for the cost model O-13 [Open].
- H-04 (counsel): Q-05-3, Q-05-8, Q-05-9 per cell once Q-11-1 names the country [Open].
- Real provider credentials go only into the platform secret store by a human (D-040 residual human act); never into a repository, agent context or CI variable of the dev/sim workflows.

### 1.10 Board verdict O-05
**APPROVE WITH CONDITIONS** (technical approval of the posture; provider selection stays a Product Owner decision after H-06):
- C-05-1 No provider endpoint, credential or SDK enters the repository, the CI workflows or any `mcp/policies` file before H-06 evidence and the Board's review of the region mapping. Owner: Security Architect; check: `make policy-check` egress rule plus secret scan; due: continuous.
- C-05-2 The model gateway is designed with ADR-018 and the TC-AI-016..019 quartet written first (tests before code), and `EgressPolicy` (REVIEW_C3 F-20) is wired on its call path. Owner: Backend Lead / Security Architect; due: before the first provider call in sim.
- C-05-3 PRIVACY_IMPACT gains the processor/transfer columns and the DPIA input (O-10) references Q-05-1..14 per region. Owner: Privacy Lead; due: Gate B sign-off for the columns, Gate D for the DPIA.
- C-05-4 RT-01 (O-36) runs against the chosen provider before Gate D; results filed. Owner: Red-Team Lead.
- C-05-5 Model output never carries a claim of expected return; the explainability contract (thesis, evidence refs, confidence) is schema-enforced for provider-backed signals as it is for rule-sma. Owner: Model Risk Lead.

---

## 2. O-22 — Registry signing key: dev HMAC → KMS/HSM asymmetric

### 2.1 What the blueprint fixes and what it leaves open
Fixed [Source: 04, 06]: the registry is signed and every MCP server refuses an unsigned or tampered registry; keys are KMS-managed; revocation is a runtime action drilled quarterly (`runtime.yaml revocation`). Fixed by decision [D-008, ADR-011]: HMAC-SHA256 over a canonical envelope for dev/sim; the dev key is a documented non-secret refused for production; asymmetric signing is the target.
Open: algorithm and key type; where the private key lives; who may sign; ceremony; rotation and revocation of keys (as distinct from revocation of a registry); which verify-only handles the code must keep; extension to the risk-policy artefact (R-29) and to command authorisation (O-53).
Verified state [Verified: registry.py, sign_tool_registry.py, verify_tool_registry.py, §0.3]: `signing_key()` returns the configured key or the dev key only when `RT_ENV ∈ {dev, sim}`; the dev key is black-listed outside dev/sim however supplied (R-40 IVA-07 closed dev/sim); the envelope covers registry, key_id, algorithm, environment_tag, registry_version, signed_at, fixture; `environment_tag` must equal `RT_ENV` (dev may load sim); a registry with pending approval records can only be signed as a sim fixture and a fixture is refused outside dev/sim (O-35); `verify_tool_registry.py --production` fails today. Weaknesses that remain by construction of a symmetric scheme [Committee: ADR-011 alternatives; GATE_B IVA-07]: every verifier holds the signing key, so any process able to load the registry can also forge one; the `algorithm` field is signed but not checked against an allowlist by the verifier (a verifier will accept whatever `algorithm` string the envelope carries as long as the HMAC matches); `key_id` is a free string; there is no trust set, so rotation requires a redeploy and there is no overlap window.
`CommandAuthoriser` / `CommandVerifier` (ADR-015, R-44): the gateway holds a verify-only object, but with HMAC the verify-only object still contains the key; the real boundary is a separate gateway process holding only verification material — which only an asymmetric scheme can provide [Verified: authorisation.py docstrings].

### 2.2 Options
| Option | Description | Pros | Cons | Cost | Risk | Reversibility | Controls / tests affected |
|---|---|---|---|---|---|---|---|
| A | Keep HMAC-SHA256; move the key into the KMS as a symmetric key; verifiers fetch it at start | smallest code change; satisfies "KMS-managed" literally | verifiers still hold forging capability; every MCP server pod needs a KMS read grant for the key (widens the secret surface that `runtime.yaml secrets_mount: none` is meant to shut); no offline verification; rotation still a redeploy | low | does not remove the trust-root weakness found by REVIEW_C3 OBJ-2 / IVA-07; R-44 stays open | high | TC-AI-005/010/011 unchanged |
| **B (recommended)** | **Ed25519 (or ECDSA P-256 if the chosen KMS does not offer Ed25519 — [Open: Q-22-1, KMS product documentation]) asymmetric signature**; private key generated non-exportable in the KMS/HSM; **public keys** pinned in the resource bundle as a trust set keyed by `key_id`; verifier checks `algorithm` against an allowlist and `key_id` against the trust set; HMAC accepted only for `RT_ENV ∈ {dev, sim}` with the dev key (existing black-list kept) | verifiers hold no secret — MCP servers, installers and the CLI verify offline with public material; forging requires the KMS sign permission; rotation by trust-set overlap without redeploying verifiers' secrets; same design reusable for command authorisation (O-53) and the risk-policy artefact (R-29) with separate keys | key ceremony and custody process; signing job needs a KMS sign grant with a workload identity; trust-set distribution must itself be integrity-protected (bundle marker check plus artefact signing O-23) | KMS/HSM key cost [Open: H-05, cloud price list]; build effort M (B-4) | wrong trust-set distribution could pin a forged public key → mitigated by O-23 artefact signing and the ceremony record | medium (keys are replaceable; the envelope format is stable) | registry.py verifier; sign_tool_registry.py signer; verify_tool_registry.py; TC-AI-005/010/011 kept; new TC-AI-020..023 (§2.6); THREAT_MODEL T-29; SECURITY_PLAN "Encryption" row; security/signing/README |
| C | Sigstore/cosign signing of the registry artefact (keyless with the CI OIDC identity, or with a KMS key) and a transparency log | transparency log gives tamper-evident history; unifies with artefact signing (O-23) | verification then depends on certificate identity policy and, for keyless, on public infrastructure (or a private Sigstore deployment) at every MCP server start — an availability and egress dependency the MCP runtime must not have (`egress.yaml`); a signature is bound to a CI identity, not to the MCP Security Agent's approval act | low tooling cost; private Sigstore infrastructure [Open] if required | verification-path availability; identity-policy mistakes | medium | same as B plus egress |

### 2.3 Design of Option B (what the code must keep and what it must add) [Committee]
**Verify-only handles the code must keep (non-negotiable):**
1. `mcp_servers.registry.load_registry` verifies only; it must import no signing capability and hold no private material (`TC-AI-005` import ban extended to any KMS client library).
2. The `--production` refusal stays exactly as today: `verify_tool_registry.py --production` must FAIL while the dev key or a fixture is in use [Verified today, §0.3]; it must additionally FAIL when `algorithm` is `HMAC-SHA256` outside dev/sim and when `key_id` is not in the trust set.
3. `signing_key()` becomes `trust_set(env)`: outside dev/sim it returns public keys only (from `mcp/policies/trust/registry_keys.json` in the bundle, covered by the bundle marker check T-49); inside dev/sim it may add the dev HMAC key, still black-listed elsewhere (R-40 test TC-AI-011 kept).
4. Algorithm allowlist checked by the verifier before any cryptographic operation: `{"Ed25519"}` (or the ECDSA variant chosen) outside dev/sim; `{"HMAC-SHA256"}` accepted only with the dev key in dev/sim. This closes the algorithm-confusion path (an envelope claiming HMAC with the public key as the MAC key).
5. `key_id` must match a trust-set entry with a `valid_from`, `valid_until` (overlap window) and `revoked` flag; a revoked key fails closed even inside its window.
6. `CommandVerifier` (ADR-015) keeps its no-sign shape and, under O-53, becomes a public-key verifier with a *different* key pair — never the registry key (one key, one purpose).
7. The envelope stays as today (registry, key_id, algorithm, environment_tag, registry_version, signed_at, fixture) so TC-AI-010's environment and fixture rules are unchanged.
8. The runtime `revoke_registry` flag (registry revocation) stays separate from key revocation (trust set); both are drilled (`runtime.yaml revocation: drill quarterly`).

**Key ceremony (human act H-20; Board-witnessed) [Committee]:**
- Participants: Security Architect (operator), Cloud Architect (KMS administrator), Product Owner or the named deputy (witness; the Product Owner may witness but never holds a sign or export grant). Three distinct humans; recorded by name in the ceremony record.
- Steps: create the key non-exportable in the KMS/HSM of the security namespace; record key_id, algorithm, public key, fingerprint, creation time, KMS resource name and the IAM policy; verify the public key by signing a known test envelope and verifying it with the repository verifier from a clean checkout; commit only the public key and the ceremony record (security/signing/ceremonies/<key_id>.md, public key file) under 2nd-line CODEOWNER review; AUDIT_EVIDENCE_INDEX row with the two signatures (operator, witness).
- Nothing private is ever committed (security/README rule); the secret scanner allowlist entry for the dev key remains the only allowed key literal.

**Custody [Committee]:**
- Sign permission: exactly one workload identity — the MCP Security Agent's signing job (a CI job or an operator-run job under the MCP Security Agent's review), granted `sign` and nothing else; it runs only after a DECISION_LOG reference for the registry version exists (O-35: no signing with pending approval records outside the sim fixture path, already enforced by `sign_registry`).
- No human holds sign or export; break-glass sign by two humans (Security Architect + deputy) with a RAID entry and audit event.
- Verify material is public; distributed in the resource bundle and, from O-23, inside signed artefacts.
- Command-authorisation key (O-53) and risk-policy signing key (R-29): separate key pairs, same ceremony, separate sign grants (the pipeline identity signs commands; the Chief Risk Agent's policy job signs policies).

**Rotation and revocation [Committee; policy values are proposals for the Product Owner, not external facts]:**
- Scheduled rotation: proposal 12 months per key, or immediately on suspected compromise, on departure of a ceremony participant with any KMS role, or when the KMS reports a key-material event.
- Overlap: new key added to the trust set (`valid_from` = ceremony time), registry re-signed under the new key, old key kept valid for a proposed 30-day overlap for installed artefacts, then `revoked: true`; a registry signed under a revoked key fails closed.
- Emergency: `revoked: true` on the compromised key plus a re-signed registry under a fresh key; MCP servers refuse at the next load (`revoke_registry` drill covers the runtime path).
- Every rotation is a ceremony record and an AUDIT_EVIDENCE_INDEX row.

### 2.4 Council positions heard [Committee]
- security-architect (presenting): B; A does not remove the forging capability from verifiers; C's verification-time dependency is incompatible with the MCP runtime's egress posture. Notes that the trust set becomes the new root and must be protected by the bundle marker (T-49) and by O-23 signing of the bundle.
- mcp-security-agent: B; insists on the algorithm allowlist (item 4) and on the import ban extension (item 1); confirms that `sign_registry`'s refusal to sign pending approvals as non-fixture must survive the change (O-35).
- red-team-pentest-lead: B; asks for the abuse cases: algorithm confusion, `key_id` substitution to a revoked or foreign key, public key swap in the bundle, signing job identity spoof; these become TC-AI-022 and a pen-test item (H-10).
- privacy-lead: no privacy impact; ceremony records contain names of participants — keep them in the audit index with the standard retention.
- counsel-platform-reliability: rotation overlap must be tested as a recovery case on an installed executable (TC-PKG interplay: the frozen bundle carries the trust set; a release is needed to ship a new public key — hence the 30-day overlap proposal).
- Different-line challenge (red-team-pentest-lead): "Gate B authorises dev/sim, where the dev key is permitted by design; why decide now?" Answer: the *code path* (trust set, algorithm allowlist, verify-only handles) must exist and be tested in dev/sim before any non-sim environment, and the ceremony must be scheduled before Gate C (H-20); deciding the design at Gate B is what makes H-20 executable. Dissent: none.
- Independent Validation: IVA-07 CLOSED (dev/sim) for the dev-key black-list; "O-22 symmetric HMAC open" — the IVA's own words [Source: REVALIDATION_2026-09-07_0cbc895 §IVA-07]; GATE_B IVA-07: "Symmetric HMAC means any key-string holder can self-sign an 'approved' registry. Resolve with O-22" [Source: GATE_B_2026-09-07].

### 2.5 Recommendation and confidence
**Option B**, with the environment-ladder reading that the dev HMAC key remains lawful in dev/sim only, the asymmetric code path is a Gate B build condition (B-4, in dev/sim with a test key pair generated in the test process — never committed), and the production key ceremony (H-20) is a Gate C entry condition. Confidence: **high** on the design (standard public-key practice; matches ADR-011's own target), **medium** on schedule (depends on KMS availability, H-05). Provenance: [Source: 04, 06] / [Committee: ADR-011, REVIEW_C3 OBJ-2, GATE_B IVA-07, this packet] / [Open: Q-22-1 KMS algorithm support, H-20, H-05].

### 2.6 Draft DECISION_LOG line
`| D-053 | 2026-09-08 | O-22: registry signing moves to an asymmetric signature (Ed25519, or ECDSA P-256 if the selected KMS lacks Ed25519 [Open: Q-22-1]) with a non-exportable KMS/HSM private key held in the security namespace and a public-key trust set (key_id, valid_from, valid_until, revoked) pinned in the resource bundle; verifiers hold no secret; algorithm allowlist and key_id trust-set check before verification; the documented dev HMAC key stays accepted only in RT_ENV dev/sim and black-listed elsewhere; sign grant to the MCP Security Agent's signing job only, after a DECISION_LOG reference per registry version; ceremony with three distinct humans (operator, KMS administrator, witness) recorded in security/signing/ceremonies and the audit index; rotation proposal 12 months with 30-day overlap, immediate on compromise; one key per purpose (registry; command authorisation O-53; risk policy R-29). Code path and quartet TC-AI-020..023 are a Gate B build condition in dev/sim; the production ceremony H-20 is a Gate C entry condition. | Product Owner agent under D-040 · Council: Security & Privacy Board COUNCIL_2026-09-08_gate_B_security_privacy §2 (APPROVE WITH CONDITIONS) · Dissent: none | A symmetric key in KMS (rejected: verifiers keep forging capability, IVA-07); C Sigstore on the registry (rejected for the MCP verification path: verification-time egress/availability dependency; kept for artefacts under O-23) | [Source: 04, 06] / [Committee: ADR-011, IVA-07] / [Open: Q-22-1, H-20, H-05] | ADR-011 amendment; registry.py; TC-AI-020..023; security/signing/README |`

### 2.7 Artefact edits implied (proposed; not made here)
| Artefact | Owner | Edit |
|---|---|---|
| docs/ADRs/ADR-011.md | MCP Security Agent (author) → amend to "Accepted with amendment": decision section gains §2.3 items 1-8; status stays Proposed until the Product Owner records D-053 | |
| docs/ADRs/ADR-015.md | Backend Lead / Security Architect | addendum: O-53 uses the same trust-set design with a separate key pair; `CommandVerifier` becomes public-key based |
| mcp/servers/mcp_servers/registry.py, scripts/sign_tool_registry.py, scripts/verify_tool_registry.py (protected: mcp/) | Backend Lead (build B-4), 2nd-line CODEOWNER review by MCP Security Agent | trust set, algorithm allowlist, key_id check, verify-only import surface; `--production` extra failure modes |
| mcp/policies/trust/registry_keys.json (new, protected) | Security Architect | public keys only; dev entry `dev-key-v0` with `environments: [dev, sim]` |
| docs/TEST_CASES/TC-AI.md | QA / Backend Lead | TC-AI-020 positive (Ed25519-signed registry with trusted key_id loads in a non-dev label using a test key pair generated in-test), TC-AI-021 negative (untrusted key_id, expired window, revoked key, HMAC algorithm outside dev/sim → refused), TC-AI-022 abuse (algorithm confusion with the public key as MAC key; key_id substitution; trust-set file swapped in the bundle → marker/signature mismatch refused; signing job identity without DECISION_LOG reference refused by `sign_registry`), TC-AI-023 recovery (rotation overlap: registry re-signed under key N+1 loads while N is valid; N revoked → old registry refused; `revoke_registry` drill) |
| docs/THREAT_MODEL.md T-29 | Security Architect | control column: "asymmetric trust set, algorithm allowlist, ceremony record; KMS key [Open: H-20]"; test column adds TC-AI-020..023 |
| docs/SECURITY_PLAN.md | Security Architect | "Encryption, tokenisation" row gains "signing keys: KMS/HSM non-exportable, one key per purpose, ceremony and rotation per COUNCIL_2026-09-08_gate_B_security_privacy §2.3"; new row "Key ceremony and custody" verified by Board witness record |
| security/signing/README.md | Security Architect | ceremony, custody, rotation text of §2.3; ceremonies/ directory |
| docs/MISSING_ACTIONS.md H-20 | delegate | scope: registry key + command key + policy key, three-person ceremony, due Gate C entry |
| docs/RAID_LOG.md O-22, O-53, R-44 | delegate | O-22 → "Decided (D-053) — build B-4 open"; O-53 references D-053 design; R-44 closure path = separate gateway process with public verifier |

### 2.8 Human actions required
- H-20 (Gate C entry): provision the KMS/HSM keys by ceremony (§2.3) — requires H-05 cloud spend and a named deputy (D-047) as witness if the Product Owner is not present [Open].
- Q-22-1: confirm the selected KMS's supported asymmetric algorithms and non-exportable key options — source: the KMS product documentation of the cloud chosen under H-05 [Open].
- Name the three ceremony participants (H-01 seats) [Open].

### 2.9 Board verdict O-22
**APPROVE WITH CONDITIONS** (design and custody model; the key itself is a Gate C human act):
- C-22-1 The asymmetric verify path, algorithm allowlist, trust set and TC-AI-020..023 are built tests-first in dev/sim, reviewed by the MCP Security Agent (2nd line), before Gate B sign-off; `verify_tool_registry.py --production` must keep failing until a ceremony key exists. Owner: Backend Lead / Security Architect.
- C-22-2 No private key material, test key pair or KMS credential is committed or placed in CI variables; test keys are generated in-process. Check: secret scan; allowlist unchanged. Owner: Security Architect.
- C-22-3 The dev HMAC key literal is renamed to state its real boundary (for example `dev-only-registry-key-dev-sim-only`) so the name no longer implies replacement at Gate B; the secret-scan allowlist entry is updated in the same change. Owner: MCP Security Agent.
- C-22-4 The ceremony record template and the trust-set schema are added to security/signing/ before H-20 is scheduled. Owner: Security Architect.
- C-22-5 Gate C entry requires the ceremony record for the registry key and the command-authorisation key (O-53) with three named humans; the Board reviews the record before recommending Gate C. Owner: Board chair (review), Product Owner (decision).

---

## 3. O-23 — Gating SAST/DAST/SCA and artefact signing

### 3.1 What the blueprint fixes and what it leaves open
Fixed [Source: 06]: signed artefacts, SBOM, SAST/DAST/SCA and secret scanning are CI gates; "unsigned deploy refused"; SCA blocks known-critical vulnerabilities (SBOM.md policy). Fixed by decision [D-038, ADR-016]: wheel/sdist and one-file executables built by `release.yml` with SHA-256 per artefact, unsigned until O-23; installers verify SHA-256 only.
Open: which scanners gate; severity thresholds; false-positive and risk-acceptance process; signing tooling and verification in installers; DAST target and timing; hash-pinned installs; action pinning.
Verified state [Verified: ci.yml, release.yml, Makefile, installer/*]: `make security-scan` runs bandit and pip-audit with `|| true` (cannot fail); `make lock` freezes the ambient environment (uncommitted change replaces it with `scripts/lock_requirements.py`, §5.3); secret scan gates; SBOM generated (CycloneDX) but unsigned; the production-refusal check gates; GitHub actions are referenced by major tag (`@v4`, `@v5`, `@v2`), not by commit SHA; release artefacts get a `.sha256` file computed in the same job that produced the binary and are attached to the release unsigned; `install.sh` / `install.ps1` verify the SHA-256 only; no DAST; no image build in CI (compose images are local); SBOM.md "Signed by: release key" is aspirational — no release key exists [Verified: SBOM.md, security/signing/README.md]. The Gate A report carries GA-C8: "H-24/O-23 ... before Gate B sign-off" [Source: GATE_A_2026-09-08 §6].

### 3.2 Options
| Option | Description | Pros | Cons | Cost | Risk | Reversibility | Controls / tests affected |
|---|---|---|---|---|---|---|---|
| **A (recommended)** | **Gate with the tools already in the toolchain plus Sigstore signing and build provenance:** bandit gates at severity HIGH with confidence MEDIUM or higher; pip-audit gates on any vulnerability with a fix available and on any vulnerability marked critical in its advisory, run against a hash-pinned lock file (`--require-hashes`); ZAP baseline (DAST) against the BFF in sim, advisory at Gate B and gating on High alerts from Gate C; cosign keyless signing (GitHub OIDC, `id-token: write`) of wheel, sdist, each executable and the SBOM (attestation), plus SLSA build provenance from the release workflow; installers verify the cosign signature against the workflow identity of this repository and the SHA-256; GitHub actions pinned by commit SHA; exceptions file with expiry | no licence dependency; everything runs in the existing workflows; open verification tooling for operators; provenance ties artefacts to the workflow run (H-24 evidence becomes machine-verifiable) | keyless verification needs the public Sigstore infrastructure at install time (operators verify, not the MCP runtime — acceptable); OS-native code signing (Windows Authenticode, macOS notarisation) still needs certificates → separate human act; bandit is Python-only (the web bundle needs its own SAST once apps/web has non-trivial JS) | tooling free; engineering effort M (B-15); certificates [Open: Q-23-3] | false-positive fatigue if thresholds are too low → mitigated by the exceptions process (§3.4); keyless identity policy mistakes → tested by TC-SC-002 abuse case | high | ci.yml, release.yml, Makefile, installer/*, security/scan_exceptions.yaml (new), SBOM.md, SECURITY_PLAN rows, T-04, T-10, T-49, T-50; new quartets TC-SC-001..003 |
| B | Hosted code-security platform (repository-native code scanning, dependency alerts, secret scanning) as the gating source | integrated PR blocking; broader language coverage; dependency review on PRs | availability and licensing for this repository's visibility are vendor terms [Open: Q-23-1, source: the platform's product documentation and pricing]; scanner results live outside the repository's evidence tree unless exported; does not sign artefacts by itself | [Open: Q-23-1] | vendor dependence for a gate of record; evidence export needed for the audit index | medium | same rows; CI configuration |
| C | Keep advisory scanning; gate only on secret scan and SBOM diff; sign nothing; rely on SHA-256 | no change | violates [Source: 06] "unsigned deploy refused"; IVA-14 stays open; GA-C8 unmet; a SHA-256 computed by the same job that built the binary proves integrity of download only, not provenance | none | supply-chain exposure (T-04, T-10) unaddressed | — | none |

Recommendation: **A now; B as an addition if Q-23-1 is answered favourably**, never as a replacement for the in-repository gates (the audit index needs the evidence in the tree).

### 3.3 Gating specification (Option A) [Committee; thresholds are policy proposals for the Product Owner]
| Scanner | Scope | Gates on | Reports only | Evidence file | TC |
|---|---|---|---|---|---|
| Secret scan (`scripts/secret_scan.py`) | whole tree | any finding (as today) | — | CI log | existing |
| SAST — bandit | libs, services, mcp, connectors, observability, apps (not test) | severity HIGH with confidence MEDIUM or HIGH | MEDIUM severity; LOW | `security/scans/bandit.json` uploaded with the evidence artefact | TC-SC-003 |
| SCA — pip-audit | hash-pinned lock (`requirements.lock.txt` with hashes, generated by `pip-compile --generate-hashes` or `scripts/lock_requirements.py` producing hashes) and the build extras | any vulnerability with a fix available; any vulnerability whose advisory severity is critical, fixed or not; any unpinned or hash-less requirement | vulnerabilities without a fix below critical → RAID row, re-checked weekly | `security/scans/pip-audit.json` | TC-SC-001 |
| Install integrity | CI and release | `pip install --require-hashes -r requirements.lock.txt`; actions pinned by full commit SHA with a version comment | — | workflow file | TC-SC-001 (abuse) |
| DAST — ZAP baseline | BFF (`create_app`) in `RT_ENV=sim` with the fixture tenant | Gate B: advisory (report uploaded); from Gate C: High alerts fail; Medium warn | Low/Informational | `security/scans/zap-baseline.html/json` | TC-SC-004 (Gate C) |
| SBOM | CycloneDX from the declared closure (`scripts/generate_sbom.py`) | gate: SBOM generation fails or the SBOM component set differs from the lock file | — | `security/sbom/sbom.cdx.json` + cosign attestation | TC-SC-002 |
| Container images | none built in CI today; when images are built (Gate C infrastructure), image scanning with the same SCA threshold and cosign image signing with the same identity policy | — | — | — | TC-SC-002 extension |
Severity mapping rule: where a tool reports CVSS, "critical" = CVSS 9.0 or higher, "high" = 7.0 to 8.9 (a policy choice for the Product Owner, not an external fact); where it reports only categorical severity, the tool's own categories are used.

### 3.4 False positives and risk acceptance [Committee]
- One exceptions file, `security/scan_exceptions.yaml` (protected path, 2nd-line CODEOWNER): entries with `id`, `tool`, `rule_or_vuln_id`, `path_or_package`, `justification`, `owner`, `recommended_by` (Board chair or Security Architect), `accepted_by` (Product Owner decision reference D-nnn), `raid_ref`, `created`, `expires` (at most 90 days; renewal is a new entry with a new decision reference).
- CI reads the file: an entry suppresses exactly one finding; an expired entry fails the build; an entry without a decision reference fails the build. Inline `# nosec` and `--ignore-vuln` on the command line are forbidden by a CI grep (TC-SC-003 abuse case).
- A true positive that cannot be fixed before a gate is a risk acceptance: RAID row (R-nnn) + Board recommendation + Product Owner decision in DECISION_LOG (D-039 §4 model). A false positive is an exception with a justification the 2nd-line reviewer can verify from the code.
- The Board reviews the exceptions file at every gate; entries older than one gate are challenged.

### 3.5 Artefact signing and verification [Committee]
- Sign: in `release.yml`, after the smoke tests, `cosign sign-blob` (keyless, GitHub OIDC; job `permissions: id-token: write, contents: write, attestations: write`) for each wheel, sdist and executable, producing `.sig` and `.pem`/bundle files; `cosign attest-blob` with the CycloneDX SBOM as predicate; SLSA build-provenance attestation for the same artefacts. The signing identity is the release workflow of this repository at a tag ref; the identity string and OIDC issuer are recorded in `security/signing/README.md` and in the installer.
- Verify: `install.sh` / `install.ps1` verify (1) the cosign signature against the recorded certificate identity and issuer, (2) the SHA-256, and refuse when either fails or when the signature files are missing (`--allow-unsigned` exists only for dev/sim with `RT_ENV` explicitly set and prints a warning); `rt365 check` reports whether the running bundle's signature was verified at install time (a marker written by the installer, itself covered by the resource marker check T-49).
- OS-native signing: Windows Authenticode and Apple notarisation require a code-signing certificate and an Apple developer identity — procurement questions [Open: Q-23-3], human act (proposed H-30); until then the cosign signature is the artefact signature of record and the OS may warn on unsigned binaries (documented in installer/README). E-5 is closed only when both cosign and the OS-native signature are verified by the installer.
- Registry trust set and any public key file ship inside the signed bundle (ties O-22 to O-23).
- Verification never happens inside the MCP runtime (no egress from MCP servers); it happens at install time and in CI.

### 3.6 Council positions heard [Committee]
- security-architect (presenting): A; the Sigstore identity policy must name the repository and workflow path exactly (abuse case: an artefact signed by a fork's workflow must fail); SHA-256 stays as a second check.
- mcp-security-agent: A; insists the MCP runtime never performs signature verification against a network service; the trust set for O-22 must ship inside the signed bundle.
- red-team-pentest-lead (3rd line, source of F-14..F-17): A; challenge — "thresholds at HIGH let MEDIUM SAST findings accumulate": accepted with the reporting column and a Board review per gate; asks for the abuse cases in TC-SC-001..003 (tampered lock hash, unpinned action, exception without decision reference, fork-signed artefact).
- counsel-platform-reliability: A; keyless verification at install time requires operator network access to the transparency log — document the offline fallback (bundle verification with a pinned root) for air-gapped installs [Open: Q-23-2, Sigstore documentation].
- privacy-lead: no personal data in scan outputs; ZAP runs against the fixture tenant only.
- Different-line challenge (red-team-pentest-lead): "Why not B, the hosted platform, which blocks PRs natively?" Answer: its availability for this repository and its cost are vendor facts [Open: Q-23-1]; the evidence of record must live in the tree; B is welcome as an addition. Dissent: none.
- Independent Validation: IVA-14 "CI SAST/SCA advisory only (`|| true`); SBOM unsigned; no image/artefact signing (O-23)" [Source: GATE_B_2026-09-07 IVA-14]; Gate A condition GA-C8 requires H-24/O-23 before Gate B sign-off [Source: GATE_A_2026-09-08].

### 3.7 Recommendation and confidence
**Option A** with the phasing: SAST/SCA gating, hash-pinned installs, SHA-pinned actions, exceptions file and cosign/provenance signing of release artefacts before Gate B sign-off (GA-C8); DAST gating and OS-native signing by Gate C entry; image signing when images are first built. Confidence: **high** on the gating design and thresholds as policy proposals; **medium** on the signing integration (keyless identity policy and installer verification need the TC-SC-002 quartet to prove them); **none** on Q-23-1..3 vendor facts. Provenance: [Source: 06] / [Committee: REVIEW_C5 F-14..F-17, GATE_B IVA-14, GA-C8, this packet] / [Open: Q-23-1..3, H-24, H-30].

### 3.8 Draft DECISION_LOG line
`| D-054 | 2026-09-08 | O-23: CI gates and artefact signing — Option A: bandit gates at HIGH severity / MEDIUM+ confidence; pip-audit gates on any fixable vulnerability and any critical advisory, run against a hash-pinned lock installed with --require-hashes; GitHub actions pinned by commit SHA; one exceptions file security/scan_exceptions.yaml with owner, justification, Product Owner decision reference and expiry ≤ 90 days (expired or unreferenced entries fail CI; inline suppressions forbidden); ZAP baseline against the sim BFF advisory at Gate B and gating on High from Gate C; release artefacts (wheel, sdist, executables) and the CycloneDX SBOM signed keyless with cosign under the release workflow's OIDC identity with SLSA build provenance; installers verify the cosign signature against the recorded identity and the SHA-256 and refuse otherwise; OS-native code signing (Authenticode, notarisation) as human act H-30 by Gate C; image scanning and signing when images are first built; the MCP runtime never verifies against a network service. Quartets TC-SC-001..003 before the change, TC-SC-004 at Gate C. | Product Owner agent under D-040 · Council: Security & Privacy Board COUNCIL_2026-09-08_gate_B_security_privacy §3 (APPROVE WITH CONDITIONS); ARB view pending on the CI change (O-23 is a joint item) · Dissent: none (3rd-line challenge on threshold accepted as reporting plus per-gate review) | B hosted code-security platform (deferred as an addition [Open: Q-23-1]); C keep advisory (rejected: [Source: 06] unsigned deploy refused; IVA-14; GA-C8) | [Source: 06] / [Committee] / [Open: Q-23-1..3, H-24, H-30] | ci.yml; release.yml; installer/; security/scan_exceptions.yaml; TC-SC-001..003; SBOM.md; SECURITY_PLAN rows |`

### 3.9 Artefact edits implied (proposed; not made here)
| Artefact | Owner | Edit |
|---|---|---|
| .github/workflows/ci.yml | Cloud Architect (build B-15) | remove `|| true` path by calling new targets `make sast-gate`, `make sca-gate` (Makefile); `pip install --require-hashes`; upload `security/scans/*`; pin actions by SHA; add exceptions-file validation step; ZAP baseline job (advisory) |
| .github/workflows/release.yml | Cloud Architect / SRE Lead | `permissions: id-token: write, attestations: write`; cosign sign-blob and attest-blob steps; SLSA provenance; attach `.sig`/bundle files; release body states the verification command and identity |
| Makefile | Cloud Architect | `sast-gate`, `sca-gate`, `dast-baseline`, `verify-artefacts` targets; `lock` produces hashes |
| installer/install.sh, install.ps1, installer/README.md | SRE Lead | cosign verification against the recorded identity; refuse unsigned unless `--allow-unsigned` with `RT_ENV=sim`; document OS warnings until H-30 |
| security/scan_exceptions.yaml (new, protected), security/signing/README.md, security/scans/ (CI output) | Security Architect | schema of §3.4; identity strings of §3.5 |
| docs/SBOM.md | Security Architect | "Signed by" column: cosign keyless (release workflow identity) instead of "release key"; last SCA result linked to `security/scans/pip-audit.json` |
| docs/SECURITY_PLAN.md | Security Architect | "Signed artefacts, SBOM, SAST/DAST/SCA, secret scanning" row: implementation = §3.3-3.5 with thresholds; "Fail-closed distribution" row: "cosign + SHA-256 verified by installer (signing [Open: O-23] → D-054)" |
| docs/THREAT_MODEL.md T-04, T-10, T-49, T-50 | Security Architect | control and test columns updated with TC-SC-001..003 |
| docs/TEST_CASES/TC-SC.md (new) | QA / Cloud Architect | TC-SC-001 SCA gate quartet (positive: clean lock passes; negative: a pinned package with a known fixable advisory fails; abuse: tampered hash, unpinned action, `--ignore-vuln` on the command line → fail; recovery: exception with decision reference and future expiry passes, expired fails); TC-SC-002 signing quartet (positive: release artefact verifies against the identity; negative: missing signature refused by installer; abuse: artefact signed by another repository/workflow identity refused, SHA-256 mismatch refused; recovery: re-signed artefact after a workflow rename verifies with the updated identity); TC-SC-003 SAST gate quartet (positive: clean tree passes; negative: injected HIGH finding fails; abuse: inline `# nosec` fails the grep; recovery: exception file entry with expiry) |
| docs/RAID_LOG.md O-23, R-46 n/a | delegate | O-23 → "Decided (D-054) — build B-15 open; DAST and H-30 at Gate C" |
| docs/MISSING_ACTIONS.md | delegate | H-24 keep (Windows evidence + confirm the identity string); new H-30 "Procure code-signing certificate (Windows) and developer identity (macOS) for OS-native signing; store in the platform secret store; Gate C" |

### 3.10 Human actions required
- H-24 (Gate B): confirm the release-run evidence on a Windows machine and, once D-054 is executed, verify one signed artefact with the documented command; sign the audit-index row [Open].
- H-30 (proposed, Gate C): certificate and developer identity procurement — questions Q-23-3: which certificate authority, validity, HSM-backed key requirement, cost — source: the CA's and the OS vendors' developer documentation [Open].
- Q-23-1: availability and cost of a hosted code-security platform for this repository — source: the platform's product documentation [Open].
- Q-23-2: offline verification path for air-gapped operators — source: Sigstore documentation [Open].
- Thresholds of §3.3 and the 90-day exception expiry are Product Owner policy choices to confirm in D-054.

### 3.11 Board verdict O-23
**APPROVE WITH CONDITIONS** (the design; the CI change itself is a build item reviewed by the ARB and a 2nd-line CODEOWNER):
- C-23-1 TC-SC-001..003 written before the workflow change; `make all` green; the first gated run's scan outputs filed under security/scans/ and indexed. Owner: Cloud Architect; due: before Gate B sign-off (GA-C8).
- C-23-2 No suppression without an entry in security/scan_exceptions.yaml carrying a Product Owner decision reference and an expiry; CI enforces it. Owner: Security Architect.
- C-23-3 Signing identity strings recorded in security/signing/README.md and the installer; TC-SC-002 abuse case (foreign identity) passes. Owner: SRE Lead.
- C-23-4 Actions pinned by commit SHA and installs hash-pinned in the same change. Owner: Cloud Architect.
- C-23-5 DAST gating and OS-native signing (H-30) are Gate C entry conditions; image signing when the first image is built. Owner: Cloud Architect / Security Architect.

---

## 4. Position on E-1 / E-2 — agent write-scope guard, harness hooks (O-58) and the Bash bypass (R-46)

### 4.1 Facts [Verified 2026-09-08]
- The generated agent frontmatter carries a `hooks: PreToolUse` matcher for `Edit|Write|MultiEdit|NotebookEdit` calling `scripts/agent_guard.py --agent <name>`; the guard denies writes outside `roster.json`, fails closed on unknown agent, missing roster or missing file path, and always denies `.github/CODEOWNERS` (TC-AGT-001..004 pass, 23 tests in the run above).
- The guard does not match the `Bash` tool. In this very session the harness instructed the chair to "make file changes with sed, heredocs, or short scripts, rather than using the dedicated Read, Edit, or Write tools" — so the ordinary write path of an agent in this harness mode is exactly the path the hook does not see. R-46 is therefore not a corner case; it is the default path under that instruction.
- Uncommitted working-tree changes (another agent's in-flight work, not reviewed here): `.claude/settings.json` adds a project-level `PreToolUse` hook for the same matchers calling `scripts/agent_guard.py` without `--agent`; `agent_guard.py` reads the agent name from the hook payload (`agent_name`, `agent_type`, `subagent_type`, `agent`) and **returns 0 (allow) when no agent name is present** ("main session or a harness that does not identify the sub-agent: the roster is advisory (O-58)"). That is a deliberate fail-open for the unidentified case.
- Whether this harness honours frontmatter `hooks:` at all is not evidenced in the tree (O-58, E-2). The chair cannot verify it from inside the session without writing outside its scope, so it stays [Open].

### 4.2 Position [Committee]
1. The guard is, and must be documented as, a **guard rail** for the delivery kit, never a security control of record. SECURITY_PLAN, security/README and ADR-016 already say so; the Board holds them to it. Nothing in the gate evidence may cite TC-AGT as proof that segregation is enforced at runtime; TC-AGT proves that the roster is consistent and that the Edit/Write path is guarded.
2. **E-1 — enforce beyond Edit/Write.** Extending the hook to `Bash` by parsing commands is a heuristic (redirections, `sed -i`, `tee`, `python -c`, git plumbing all write); the Board does not object to a best-effort Bash matcher as defence in depth but rejects any claim that it closes R-46. The closure path for R-46 is **branch-level enforcement in CI**: a `scripts/check_authorship.py` step that reads the author identity of each commit or PR (the `Claude-Session`/agent trailer that commits already carry, or the PR's declared agent) and fails when changed paths fall outside that agent's roster entry, combined with CODEOWNERS mapped to real reviewers and branch protection (O-20, H-01). With that in place R-46 can move from "mitigated, not closed" to "closed by CI + branch protection"; without it R-46 stays open through Gate B and is accepted only for dev/sim.
3. **E-2 — harness support (O-58).** Verify with a probe: a throw-away generated agent whose only owned path is a scratch file, instructed to write elsewhere through Edit; the denial (exit 2) in the transcript is the evidence; then repeat through Bash to document the bypass. Record the result in TC-AGT.md as an environment fact with the harness version. If frontmatter hooks are not honoured, the project-level hook is the right relocation — but its **fail-open branch for an unidentified agent must be recorded as a known limit in TC-AGT-003 (abuse) and in O-58**, and the roster must be marked "advisory" in AGENT_ROSTER.md for that harness. The Board would prefer fail-closed (deny when the agent cannot be identified) for every path under `services/risk`, `services/compliance`, `services/execution`, `mcp/policies`, `security`, `contracts` (the protected paths of pyproject.toml), and advisory elsewhere; that is a proposal for the MCP Security Agent, not a condition, because the harness behaviour is unknown.
4. Segregation of *record* remains: author != reviewer != approver is checked by the IVA on authorship (GA-C3/H-27 asks for one human-authored merge) and by the reviewer/approver columns of AUDIT_EVIDENCE_INDEX; the Board reads those columns, not the hook.

### 4.3 Verdict on the agent roster and write-scope guard (within scope) — **APPROVE WITH CONDITIONS**
- C-AGT-1 Roster approved as generated (67 agents match goals/, [Verified]); the chair's own scope (docs/SESSIONS/, RAID, AUDIT_EVIDENCE_INDEX, PO_DECISION_QUEUE) is correct for an approver.
- C-AGT-2 R-46 stays open until `check_authorship.py` (or an equivalent branch-level check) gates CI and CODEOWNERS/branch protection are active (O-20); no artefact may describe the hook as a control. Owner: Product Owner delegate / MCP Security Agent; due: Gate B sign-off for the CI check, Gate C for branch protection (needs H-01 teams).
- C-AGT-3 The project-level hook's fail-open for unidentified agents, if committed, is documented in TC-AGT-003, O-58 and AGENT_ROSTER.md in the same change, with the E-2 probe result. Owner: MCP Security Agent (2nd-line review of the uncommitted change).
- C-AGT-4 The `--agent` argument path (frontmatter hooks) is kept so a harness that does honour frontmatter gets the identified, fail-closed behaviour. Owner: Delivery Orchestrator (generator).

---

## 5. Consolidated record

### 5.1 Verdicts
| Item | Board verdict | Conditions | Human decision requested |
|---|---|---|---|
| O-05 | APPROVE WITH CONDITIONS (posture Option B; vendor facts [Open]) | C-05-1..5 | Adopt the model-gateway posture (D-052 draft); answer/obtain Q-05-1..14 per provider and region before H-06 |
| O-22 | APPROVE WITH CONDITIONS (asymmetric trust-set design, ceremony, custody, rotation) | C-22-1..5 | Adopt D-053 draft; schedule H-20 ceremony with three named humans at Gate C entry; confirm rotation values |
| O-23 | APPROVE WITH CONDITIONS (gating thresholds, exceptions process, cosign/provenance signing, installer verification) | C-23-1..5 | Adopt D-054 draft; confirm thresholds and the 90-day exception expiry; open H-30 |
| Agent roster and write-scope guard (E-1/E-2, R-46, O-58) | APPROVE WITH CONDITIONS (roster; guard as guard rail only) | C-AGT-1..4 | Accept R-46 for dev/sim only until the CI authorship check exists |
No item is REJECTED; no item is approved without conditions because in each case a control quartet is not yet written (TC-AI-016..023, TC-SC-001..003) and a threat row lacks its test (T-29 asymmetric path; T-04/T-10 signing) — the Board's own rule.

### 5.2 Proposed RAID entries (for the delegate to record; the chair may write RAID_LOG but the convener restricted this session to one file)
| ID (proposed) | Type | Text | Owner | Gate |
|---|---|---|---|---|
| O-79 | Gap | Model gateway (ADR-018) and quartet TC-AI-016..019 do not exist; no provider may be wired before them (C-05-2) | Backend Lead, Security Architect | B (design) / D (provider live) |
| O-80 | Gap | Q-05-1..14 per provider and region unanswered; PRIVACY_IMPACT lacks processor/transfer columns (C-05-3) | Privacy Lead | B (columns) / D (DPIA) |
| O-81 | Gap | Asymmetric registry verification path, trust set, algorithm allowlist, TC-AI-020..023 (C-22-1); dev key literal rename (C-22-3) | Backend Lead, MCP Security Agent | B |
| O-82 | Gap | Ceremony record template and trust-set schema in security/signing/ (C-22-4) | Security Architect | B |
| O-83 | Gap | TC-SC-001..003, gating SAST/SCA, hash-pinned installs, SHA-pinned actions, exceptions file, cosign/provenance signing, installer verification (C-23-1..4) | Cloud Architect, SRE Lead | B |
| O-84 | Gap | DAST gating, OS-native code signing (H-30), image signing (C-23-5) | Cloud Architect, Security Architect | C |
| O-85 | Gap | CI authorship check `scripts/check_authorship.py` against roster.json; branch protection (O-20) (C-AGT-2) | Product Owner delegate, MCP Security Agent | B / C |
| R-50 | Risk | The verifier accepts any `algorithm` string in the envelope as long as the HMAC matches (no allowlist) — harmless with a single symmetric key, an algorithm-confusion path once public keys exist; closed by C-22-1 | Security Architect | B |
| R-51 | Risk | Project-level agent guard fails open when the harness does not identify the sub-agent (uncommitted change); acceptable only as a guard rail; documented per C-AGT-3 | MCP Security Agent | B |
| H-30 | Human act | Procure code-signing certificate (Windows) and developer identity (macOS); keys in the platform secret store | Security Architect + Finance | C |
| Q-05-1..14, Q-22-1, Q-23-1..3 | Questions | as listed | Privacy Lead / Security Architect / Cloud Architect | B–D |

### 5.3 Observations outside the three items (for the owning roles)
- Uncommitted working tree at the time of this session: `.claude/settings.json`, `apps/cli/rt365_cli/agent_guard.py`, `Makefile` (`lock` → `scripts/lock_requirements.py`), `requirements.lock.txt`, several docs/TEST_CASES headers, RAID and queue rows. None of it was reviewed as evidence here; the packet's checks ran on that tree and passed. The MCP Security Agent should review the guard change before it is committed (C-AGT-3).
- SBOM.md's "Signed by: release key" and security/signing/README's "Production keys live in the KMS/HSM" describe a target, not a state; both should read [Open: O-22/O-23 → D-053/D-054] until the ceremony and the signing step exist.
- The Board has not approved the THREAT_MODEL or SECURITY_PLAN as documents in this session (their "Draft v1.0" status stands); the rows named above are amendments the Board expects before it does.

### 5.4 Proposed AUDIT_EVIDENCE_INDEX rows (reviewer column: "Security & Privacy Board chair — agent approval, human PO decision pending")
| # (proposed) | Gate | Evidence | Type | Location | Reviewer |
|---|---|---|---|---|---|
| 36 | B | Security & Privacy Board decision packs and verdicts for O-05, O-22, O-23 and the agent guard position | council packet | docs/SESSIONS/COUNCIL_2026-09-08_gate_B_security_privacy.md | Board chair (agent approval — human PO decision pending); IVA review requested |
| 36a | B | `verify_tool_registry.py --production` refusal in four configurations; TC-AI/TC-AGT/TC-PKG 23 passed; lint, policy-check, agents-check, secret-scan OK at HEAD d1ccb21 (+ uncommitted tree) | verbatim command output | this packet §0.3 | Board chair (agent approval — human PO decision pending) |

### 5.5 Decision requests for docs/PO_DECISION_QUEUE.md (one line each; proposed text for the delegate)
- O-05: "Adopt the provider-agnostic model-gateway posture (Option B, D-052 draft) — no provider ever receives secrets, broker routes or limit write paths; vendor choice after Q-05-1..14 and H-06?" — Board: APPROVE WITH CONDITIONS C-05-1..5.
- O-22: "Adopt asymmetric registry signing with a KMS/HSM key, public trust set, three-person ceremony and rotation (D-053 draft); code path at Gate B, ceremony H-20 at Gate C entry?" — Board: APPROVE WITH CONDITIONS C-22-1..5.
- O-23: "Adopt gating SAST/SCA at the §3.3 thresholds, hash-pinned installs, exceptions with expiry, cosign/provenance signing and installer verification (D-054 draft); DAST gating and OS-native signing (H-30) at Gate C?" — Board: APPROVE WITH CONDITIONS C-23-1..5.
- R-46/O-58: "Accept the agent write-scope guard as a guard rail only, with R-46 open until a CI authorship check and branch protection exist?" — Board: APPROVE WITH CONDITIONS C-AGT-1..4.

### 5.6 Assumptions, confidence, provenance
- Assumption A-1: the delegate will convene the ARB for the CI change (O-23 is a joint item) and the Model Risk Committee for the provider evaluation harness (O-05 joint item); this packet covers the Security & Privacy view only [Committee].
- Assumption A-2: KMS/HSM availability follows H-05 cloud spend; without it the dev/sim posture continues and no non-sim environment is entered (environment ladder) [Source: 12].
- Confidence: O-05 medium-high (posture) / none (vendor facts); O-22 high (design) / medium (schedule); O-23 high (gating) / medium (signing integration) / none (vendor facts); E-1/E-2 high on the position, [Open] on harness behaviour.
- Provenance: every [Verified] statement is a file read or a command run on 2026-09-08 in /home/user/RT365 at HEAD d1ccb21 with the uncommitted changes listed in §5.3; every vendor, regulatory or price statement is [Open]; nothing in this packet is a Product Owner decision.
