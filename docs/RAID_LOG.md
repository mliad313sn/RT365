# RAID_LOG

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB | A–F | Draft v1.0 |

| ID | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| O-01 | Assumption | Persona × mode policy per jurisdiction | Compliance & Legal Committee (advisory) | Gate A | Decided 2026-09-08 (D-045): global floor, autonomy OFF by default; persona→CustomerType mapping [Open: Q-01-1] |
| O-02 | Gap | Pricing and billing scope (E14) | Product Director, Finance | Gate A | Decided 2026-09-08 (D-046): meter from D, invoice from F, subscription hypothesis; prices/tax/provider [Open] |
| O-03 | Dependency | Numeric freshness/latency thresholds after baselines | SRE Lead | Gate E | Open |
| O-04 | Decision | Service framework choice | ARB | Gate B | Open |
| O-05 | Gap | Model providers, hosting, data-processing terms | Model Risk Lead, Privacy Lead | Gate B | Open |
| O-06 | Gap | Evaluation dataset ownership/licensing | Model Risk Lead | Gate D | Open |
| O-07 | Gap | Numeric risk thresholds per asset class/jurisdiction | Trading Risk Committee | Gate C | Open |
| O-08 | Gap | Liquidation policy content | Trading Risk Committee | Gate E | Open |
| O-09 | Risk | Deletion right vs record retention (legal hold) | Legal Agent, Privacy Lead | Gate D | Open |
| O-10 | Dependency | DPIA per launch jurisdiction | Privacy Lead | Gate D | Open |
| O-11 | Gap | First launch jurisdiction hypothesis | Product Director, Compliance Agent | Gate A | Decided as hypothesis 2026-09-08 (D-043): first-party pilot cell; country fact [Open: Q-11-1, owner]; legal basis [Open: H-04] |
| O-12 | Dependency | Data licensing for derived/redistributed data | Legal Agent, Data Architect | Gate C | Open |
| O-13 | Decision | Time-series/snapshot storage cost model | Data Architect, Finance | Gate B | Open |
| O-14 | Decision | Launch locales | Product Director | Gate F | Open |
| O-15 | Gap | On-call model and support hours per market | SRE Lead, Support Lead | Gate F | Open |
| O-16 | Gap | Measurable outcome targets for Gate A | Product Council | Gate A | Decided 2026-09-08 (D-044): four definitional targets; time-to-halt ceiling [Open: Q-16-1, first drill] |
| O-17 | Gap | Roadmap dates after capacity model | Executive Steering | Gate B | Open |
| O-18 | Gap | RPO/RTO per cell | Cloud Architect | Gate E | Open |
| O-19 | Gap | Named deputies for emergency authority | Program Orchestrator | Gate C | Open |
| R-01 | Risk | Non-deterministic path in risk/eligibility | Chief Risk Agent | continuous | Open |
| R-02 | Risk | Duplicate orders during executor failover | Integration Architect | Gate C | Open |
| R-03 | Risk | Look-ahead/leakage inflating backtests | Model Risk Lead | Gate D | Open |
| R-04 | Risk | Marketing/UI language implying guaranteed returns | GTM Lead, Compliance Agent | Gate F | Open |
| O-20 | Gap | CODEOWNERS team handles map to real reviewers; branch protection enabled | Program Orchestrator | Gate B | Open |
| O-21 | Gap | Surveillance detector parameters (wash/spoof/close windows) approved by Compliance & Legal | Compliance Agent | Gate D | Open |
| O-22 | Decision | Asymmetric (Ed25519/KMS) signing of the tool registry and artefacts; dev HMAC key retired | Security Architect, MCP Security Agent | Gate B | Open |
| O-23 | Gap | SAST/DAST/SCA scanners and artefact signing wired into CI (currently lint, typecheck, secret scan, SBOM only) | Cloud Architect | Gate B | Open |
| O-24 | Gap | Accessibility (WCAG 2.2 AA) pass on the operator console; PWA build (E10) | Frontend Lead, Accessibility Lead | Gate F | Open |
| O-25 | Decision | Trailing-stop and conditional order semantics per broker (schema accepts; sim broker rejects) | Trading Domain Lead | Gate C | Open |
| R-05 | Risk | Dev/sim stores are in-memory: durability, exactly-once under real redelivery and lease consistency are unproven on the deployed topology | Enterprise Architect | Gate C | Open |
| R-06 | Risk | BFF dev authentication (client-asserted headers) must be replaced by IdP/MFA sessions before any shared environment | Backend Lead, Security Architect | Gate B | Open |
| R-07 | Risk | Sim risk-policy fixture values could be mistaken for approved thresholds; `approved_for_production=false` guards it | Chief Risk Agent | Gate C | Open |
| R-08 | Risk | Set/dict ordering non-determinism in engine code (one instance found and fixed by the replica test TC-RK-001) | Backend Lead | continuous | Mitigated (replica test in CI) |
| O-26 | Decision | ADR-003 rev.2 / ADR-014: a policy re-evaluation of an intent that already has a live order never creates a second order; the gateway per-intent invariant is defence in depth (REVIEW_C2 OBJ-1) | ARB, Chief Risk Agent | Gate C | Open — ADR-014 Proposed; invariant implemented (D-015) |
| O-27 | Gap | Broker adapter contract: `query_order` (delivered), `StatementOrder.status`/`OrderStatus.status` enum, venue-side cancel/expiry event, capabilities consulted by the gateway before submit, certification in both dedupe modes (REVIEW_C2 O-21, F-23, F-24, A-01) | Integration Architect, Broker-Connector Lead | Gate C | Partially remediated — Open |
| O-28 | Gap | Executor lease policy: TTL/heartbeat/submit-timeout baselines, lease held by the executor process, preempt authorised to the Kill Switch identity only, CP-store failover test (REVIEW_C2 O-22, F-02, F-03) | SRE Lead, Backend Lead | Gate C (design) / Gate E (numbers) | Open — `LeaseStore.renew` exists, nothing calls it |
| O-29 | Gap | Reconciliation cash/price tolerances and fee/accrual model per broker and currency; severity policy hook for the Trading Risk Committee (REVIEW_C2 O-23, F-16) | Trading Risk Committee, Broker-Connector Lead | Gate C | Open |
| O-30 | Gap | EVENT_CATALOG v1.1 (producers, state enums, market_ts on execution events, reconciliation/halt events on the bus) and OpenAPI parity with every BFF route; emitted-event validation in CI (REVIEW_C2 O-24, F-19, F-30, F-31) | Integration Architect (author), Backend Lead (review), ARB (approve) | Gate B re-confirmation / Gate C | Partially remediated — Open |
| O-31 | Gap | Sample strategy sizing vs strategy cap; backtest report to expose the reason-code distribution; exploratory runs labelled (REVIEW_C2 O-25, F-27, F-28) | Quant Research Lead, Model Risk Lead | Gate C | Partially remediated — Open |
| O-32 | Dependency | Broker certification evidence: review of `docs/BROKER_CERTIFICATIONS/sim-broker.md` by the Trading Domain Lead; harness vs the 10-row checklist (order-type behaviour, cancel/fill race, executed reconciliation match, time advance); simulated-broker realism limits stated on the certification and backtest report (REVIEW_C2 D-01, F-21, F-22) | Broker-Connector Lead, Trading Domain Lead | Gate C | Open |
| O-33 | Gap | Order/intent state machines completed for venue outcomes: REPLACED/DONE_FOR_DAY, cancel/replace key derivation, RECONCILED/ARCHIVED driven by `reconcile()`, asynchronous ack mapped to the intent (REVIEW_C2 F-06, F-11, F-13, F-15) | Backend Lead, Trading Domain Lead | Gate C | Partially remediated — Open |
| O-34 | Gap | Ledger valuation model: stale-mark fallback, margin/buying power, per-trade PnL, multi-currency, financing/borrow costs, settlement (REVIEW_C2 F-18, F-25 residual) | Backend Lead, Model Risk Lead | Gate D | Open |
| O-35 | Gap | Tool approval records `MCP-SEC-2026-001..006` are placeholders; the registry is signed only as a sim fixture; per-tool MCP Security Agent signature after a DECISION_LOG entry (REVIEW_C3 OBJ-2 item 4; 1st-line packet C03 local "O-28") | MCP Security Agent, Security & Privacy Board | Gate B | Open — fixture-only signing enforced in code |
| O-36 | Gap | Prompt-injection corpus (`test/corpus/injection/`), unicode/homoglyph/zero-width variants, RT-01 against the real prompt and model once O-05 is decided (REVIEW_C3 F-12; C03 local "O-29"; O-06) | Red-Team Lead, Backend Lead, MCP Security Agent | Gate D | Open |
| O-37 | Gap | Where account state is served to the `analytics-account` MCP server in deployment; egress route plus threat-model delta signed by the Security Architect (REVIEW_C3 O-30) | Backend Lead, Cloud Architect, Security Architect | Gate B | Open |
| O-38 | Gap | `read_account_state` masking policy: keyed pseudonym, currency-aware bucketing, minimum bucket count, contract test (REVIEW_C3 O-31, F-16) | MCP Security Agent, Privacy Lead | Gate D | Partially remediated — Open |
| O-39 | Gap | Agent token issuance (maker-checker, audited), transport to external agents, `Principal` view without the secret (REVIEW_C3 O-32, F-07 residual, F-08) | Backend Lead, Security Architect | Gate D | Partially remediated — Open |
| O-40 | Gap | MCP_TOOL_CATALOG re-issue after remediation: quota per (tenant, account, strategy, tool) plus tenant ceiling (delivered), "queued" simulation, per-tool status (REVIEW_C3 O-33, F-06, F-23) | MCP Security Agent (catalog), Backend Lead | Gate C | Partially remediated — Open |
| O-41 | Decision | Requested: "monitoring-state integrity after every allowed tool call" becomes a standing TC-AI abuse case (TC-AI-006 exists) and a tool-registration precondition (REVIEW_C3 O-34) | MCP Security Agent → Security & Privacy Board | Gate B | Requested — pending |
| O-42 | Assumption | Kubernetes NetworkPolicy semantics are additive (allow-union) on the target CNI; verified by reading only (REVIEW_C3 A-C3-2; REVIEW_C5 F-11 confidence note) | Cloud Architect | Gate B | Open — confirm on the cluster (H-05) |
| O-43 | Assumption | REVIEW_C5 was authored by one agent holding a 1st-line (Security Architect) and a 3rd-line (Red-Team Lead) role; its findings and residual risks must be ratified by the Security & Privacy Board and IVA before any item is accepted or closed (REVIEW_C5 A-SEC-00) | Security & Privacy Board, Independent Validation Agent | Gate B | Open |
| O-44 | Gap | Canary tokens seeded per tenant into masked account state and strategy docs; match list held outside the repository; matching on egress and model output, not only tool I/O (REVIEW_C3 F-11) | Security Architect, MCP Security Agent | Gate D | Open |
| O-45 | Gap | In-process `EgressPolicy` wired to every outbound client used by MCP servers; the TC-AI-005 AST scan extended to every module defining a registered handler; `enter(Plane.CONTROL/EXECUTION)` forbidden in handler modules (REVIEW_C3 F-20) | Backend Lead | Gate B | Open |
| O-46 | Decision | RISK_POLICY change: risk-reducing order rule and open-order projection semantics; reservation between decision and fill (REVIEW_C4 §5.2, local "D-01") | Trading Risk Committee (Chief Risk Agent proposes, does not approve) | Gate C | Open — implemented behind a policy flag (D-022); TRC approval pending |
| O-47 | Decision | Decision contract names decision time as the fifth input (delivered in `decision_id`); RISK_POLICY "all checks always evaluated" wording; LIMIT_MATRIX rows for volatility regime, correlated group, runtime thresholds, loss-% base, freshness placement; dead knobs `concentration_action`/`complex_asset_classes` wired or deleted (REVIEW_C4 local "D-02", F-06, F-08, F-19, F-21, F-23) | Trading Risk Committee | Gate C | Open |
| O-48 | Decision | Cooling-period asymmetry: tighten immediately with two persons, loosen after cooling (REVIEW_C4 local "D-03", F-24) | Trading Risk Committee | Gate C | Open |
| O-49 | Gap | Additional pre-trade controls: protective-stop distance (`RK-PROT-DIST`), SELL_SHORT/BUY_TO_COVER margin, MARKET-order collar/spread bound, undefined envelope in autonomous mode → HALT, intent-age budget (REVIEW_C4 F-09, F-10, F-14, F-15, F-16) | Backend Lead, Trading Risk Committee | Gate C | Open — `RK-FRESH-INTENT` (market_ts not ahead of now) exists; an age budget does not |
| O-50 | Issue | Secret scan: scans the working tree when `git ls-files` is empty and fails on zero files (delivered); AKIA/ghp_/JWT/AIza patterns added; bare PKCS8 `BEGIN PRIVATE KEY`, Slack webhooks and unquoted long secrets still unmatched (REVIEW_C5 I-SEC-11, F-13) | Security Architect | Gate B | Partially remediated — Open |
| O-51 | Issue | `/v1/intents/{id}/process` drains and discards non-matching queued intents behind `VIEW_DASHBOARD`; `/healthz` exposes `audit_length` unauthenticated (REVIEW_C5 I-SEC-12, F-04, F-07) | Backend Lead | Gate C | Open |
| O-52 | Dependency | External pen-test and red team (RT-01..RT-06 retest after remediation) before Gate D — MISSING_ACTIONS H-10 (REVIEW_C5 D-SEC-13) | Procurement, Security Architect | Gate D | Open |
| O-53 | Open item | Command authorisation uses a shared HMAC key held by the composition root (dev/sim); Gate C target is an asymmetric signature with an HSM/KMS-held private key and key rotation (IVA V-C2 remediation, ADR-015) | Security Architect, Backend Lead | Gate C | Open |
| O-54 | Open item | External anchoring of the audit `ChainHead`: `seal()` anchors are produced in-process (IVA-09); a WORM/replica anchor store written by a different principal is needed before Gate C | SRE Lead, Internal Audit | Gate C | Open (with R-05) |
| O-55 | Open item | Durable token and nonce store for agent identities: the nonce journal is a JSONL file and identities are restored via `IdentityIssuer.adopt()` (IVA-08); replicated store before shadow (R-05) | Backend Lead | Gate C | Open |
| O-56 | Open item | IVA re-validation of the remediation commit for V-C1, V-C2, IVA-03..IVA-08 (gate reports GATE_A/B/C_2026-09-07 refer to 09a6e71; their conditions are remediated in dev/sim only) | Independent Validation Agent | next Committee convening | Open |
| O-57 | Open item | Ratification of the Product Owner appointment (acting) and mapping of the seat to a named person and deputy (D-035, H-23, O-19) | Product Owner | Gate A | Closed 2026-09-08 for the appointment and authority (owner declaration, D-039); deputy still open under O-19 |
| O-58 | Dependency | Agent write-scope guard relies on the agent harness honouring `hooks:` in sub-agent frontmatter; where unsupported, the roster is advisory and CODEOWNERS/branch protection remain the only enforcement (they are the controls of record in any case) | Product Owner, MCP Security Agent | Gate B | Open |
| O-59 | Dependency | The Windows `rt365.exe` is produced only by the release workflow on a `windows-latest` runner (no Windows build host in the dev environment); its first successful run and checksum must be recorded in AUDIT_EVIDENCE_INDEX (H-24); artefact signing pending O-23 | SRE Lead, Security Architect | Gate B | Open |
| O-60 | Issue | Gate prompts contradicted themselves on the IVA-veto override (COUNCIL_2026-09-08_gate_A_iva IVA-A-01) | Program Orchestrator / Product Owner | before Gate A re-convening | Closed 2026-09-08 — PROHIBITIONS now forbid only a *silent* override; written override with risk acceptance per D-039 |
| O-61 | Gap | Decision packs for O-01, O-02, O-11, O-16 were prompt templates; option analyses produced by the Gate A council on 2026-09-08 (SESSIONS/COUNCIL_2026-09-08_gate_A_*.md) and transcribed into PO_DECISION_QUEUE.md | product-owner delegate, Product Director | before Gate A re-convening | Closed 2026-09-08 — decided D-043..D-046 |
| O-62 | Gap | D-039 (decision authority) recorded by the AI delegate from the owner's in-session instruction; the owner's explicit confirmation on a committed tree is the evidence of authorship (IVA-A-03) | Product Owner | before Gate A re-convening | Reopened per GA-C3: the owner reaffirmed and delegated in session (D-040, D-041) but commits are authored by the AI delegate; evidence of owner authorship = an owner-authored commit/merge (for example merging the PR) or a signed line (H-27) | Gate B |
| O-63 | Issue | H-01 'blocks A' vs O-19 'Gate C' for deputies; AEI row 25 stale after H-23 closure (IVA-A-04/05) | Program Orchestrator | before Gate A re-convening | Closed 2026-09-08 — deputy required by Gate C (first two-person act on real infrastructure, H-19); H-01 keeps Gate A for the roles themselves; AEI row 25 updated |
| O-64 | Gap | No timed Kill Switch activation record; 'operator time-to-halt' has no measurement path until the drill (H-19) | SRE Lead | Gate D (target set at A) | Partially closed 2026-09-08 — activation records `engaged_at`/`halt_elapsed_ms`, metric `killswitch.time_to_halt_s`, SLI `time_to_halt_s`, TC-KS-009 block-rate assertion (GA-C7 build part); operator-action → engaged needs the drill (H-19); ceiling Q-16-1 open |
| O-65 | Risk | Evidence generated against a moving working tree; evidence headers embed the base commit, not the tested commit (IVA-A-06/07) | QA Lead, Product Owner | Gate B | Open — gate decisions must cite the commit CI evidenced; CI regenerates evidence at the pushed commit |
| O-66 | Gap | Q-11-1 country fact (ISO 3166-1 alpha-2 of the operating entity) open in both matrix rows (GA-C1) | Product Owner (human fact) | Gate B | Open |
| O-67 | Issue | AEI rows 1/1b reviewer column = deciding agent, not a 2nd-line role (GA-C2) | Program Orchestrator | Gate B | Open |
| O-68 | Issue | RACI.md wording 'never approves a gate' stale vs D-039; PERSONAS row tag; SCOPE status (GA-C4) | Program Orchestrator, Product Director | Gate B | Closed 2026-09-08 — RACI wording, PERSONAS row and SCOPE status updated; Support & Training Lead and Legal Agent reviews pending on the rows |
| O-69 | Gap | Counsel question lists not yet adopted as the H-04 scope; counsel of record unnamed (GA-C5; H-25) | Legal Agent | Gate B (scope) / D (answers) | Open |
| O-70 | Gap | Dual-key hands rule not yet written as policy; the two humans unnamed (GA-C6; H-26) | Product Owner | Gate B (rule) / D (names) | Rule recorded 2026-09-08 in PRODUCT_OWNER.md §Deviation (c) and JURISDICTION_MATRIX; names open |
| O-71 | Gap | Global RAID IDs for legal-record integrity (`legal_record_ref` unverified string, council P-2) and surveillance wiring at registration | Program Orchestrator | Gate B | Open — P-2 tracked here; surveillance wiring under E06 P9 |
| O-72 | Observation | D-040 wording vs goals/00_product_owner.md harmonised (R-10) | Program Orchestrator | Gate B | Closed 2026-09-08 |
| O-73 | Dependency | Meridian first-run defects (in-memory book without PGLITE_DIR; data dir mkdir not recursive; dev server without a built client answers 404) — documented workaround in docs/PMO.md §2; upstream improvement I-1 | Program Orchestrator | Gate B | Open — proposed upstream |
| O-74 | Dependency | Meridian's public API is read-only; the sync uses undocumented session routes and encodes identity in titles (no external id); pin the Meridian commit (77c4b49) until a write API exists (I-2) | Program Orchestrator | Gate B | Open — proposed upstream |
| O-75 | Risk | Meridian scaffolds its own four gates on every project; our six gates are milestones beside them; a reader could take Meridian's phase as the authorised environment | Product Owner | Gate B | Mitigated — docs/PMO.md §3 rule 5 (authorisation only by our gates); improvement I-3 proposed |
| O-76 | Dependency | Operating Meridian for real: PostgreSQL, restore-tested backup, second instance, written security policy, demo credentials changed (its SECURITY.md); dates placeholders until O-17 | SRE Lead | Gate C (before shadow) | Open — H-28 |
| R-09 | Risk | SUBMITTED-but-unacked order was un-cancellable, un-expirable and invisible to reconciliation; Kill Switch "cancel open orders" not guaranteed (REVIEW_C2 OBJ-2, F-11; local "R-05") | Backend Lead, Trading Domain Lead | Gate C | Remediated in dev/sim — IVA verification pending; scheduled re-driver on real infra Open |
| R-10 | Risk | Reconciliation compared quantities only: internal CANCELLED vs broker OPEN reconciled clean; no fee model; recurring breaks minted new tickets; same-line resolvers accepted (REVIEW_C2 OBJ-3, F-16, F-17, F-19, F-20; local "R-06") | Backend Lead, Chief Risk Agent | Gate C | Remediated in dev/sim — IVA verification pending; tolerances/fee model O-29 Open |
| R-11 | Risk | STRATEGY-level Kill Switch cancelled every open order platform-wide and every level preempted every account's lease (cross-tenant fencing side-effect) (REVIEW_C2 F-01; local "R-07") | Backend Lead, SRE Lead | Gate C | Remediated in dev/sim — IVA verification pending |
| R-12 | Risk | Backtest applied costs outside the pipeline while PAPER charged none — backtest ≠ paper on costs (ADR-008 breach) (REVIEW_C2 F-25, F-26; local "R-09") | Backend Lead, Model Risk Lead | Gate C | Partially remediated — Open (fees inside the ledger; financing/borrow, slippage-in-price, settlement in O-34) |
| R-13 | Risk | Execution Gateway emitted `order.command.v1` with an `OrderEvent` payload that violated the registered schema — two producers, one name, two shapes (REVIEW_C2 F-29; local "R-10") | Integration Architect, Backend Lead | Gate B/C | Remediated — emitted-event validation in CI Open (O-30) |
| R-14 | Risk | Execution-path failure handling: gateway never consults the Kill Switch; cancel rejections not alerted; late/over fills raised and aborted the poll loop; broker-unavailable on poll silent; `order.command.v1` published before the lease is acquired (REVIEW_C2 F-04, F-05, F-07, F-08, F-10, F-14) | Backend Lead | Gate C | Partially remediated — Open |
| R-15 | Risk | Replay/duplicate intents: a signed tool call replayed for the token TTL; re-submitting an `intent_id` reset a FILLED intent to CREATED; an economically identical intent with a new id evaded RK-DUP (REVIEW_C3 F-01 local "R-11"; REVIEW_C2 F-12; REVIEW_C4 F-11; T-08) | Backend Lead, Integration Architect | Gate C | Remediated in dev/sim — IVA verification pending; nonce cache in-memory (R-05) |
| R-16 | Risk | Agent-callable `run_simulation` mutated the process-global PlaneGuard: it disabled S1 plane-deny alerting and wiped deny evidence; template/strategy/version were ignored; a full platform incl. a broker adapter was built inside the analytics process (REVIEW_C3 OBJ-1, F-17; local "R-09") | Backend Lead (fix), MCP Security Agent (accept), IVA (verify) | Gate B (private guard) / Gate D (worker isolation) | Remediated for the Gate B condition (ADR-013) — worker isolation and resource bounds Open |
| R-17 | Risk | Revocation model: a research-only agent revoked `submit_trade_intent` tenant-wide; three S1 auto-actions revoked agent "unknown" silently; denials bypassed quota (alert storm); all revocation state was lost on restart; no drill artefact (REVIEW_C3 OBJ-3; local "R-10") | Backend Lead, SRE Lead, MCP Security Agent | Gate D | Partially remediated — Open (`agent` missing from `plane.deny`/`killswitch.agent_attempt`/`risk.integrity_violation` payloads; drill H-19) |
| R-18 | Risk | NetworkPolicy allow-union let MCP pods inherit the namespace-wide analytics egress; the checker inspected policies in isolation (REVIEW_C3 F-19; REVIEW_C5 F-11; local "R-12"/"R-SEC-05") | Cloud Architect, Security Architect | Gate B | Remediated in manifests and checker — cluster verification Open (H-05, O-42) |
| R-19 | Risk | Provenance labelling was never applied on any tool-output path; `get_strategy_docs` returned 1st-line free text undelimited (REVIEW_C3 F-13; local "R-13") | Backend Lead, Model Risk Lead | Gate D | Remediated in code — no TC asserts it; corpus O-36 Open |
| R-20 | Risk | Post-hoc handler timeout: a hung handler blocked the BFF event loop including `/v1/killswitch`; unbounded request body; unbounded indicator reads (REVIEW_C3 F-05, F-09, F-18; local "R-14") | Backend Lead, SRE Lead | Gate C | Partially remediated — Open (pre-emptive deadline and executor delivered; body cap and isolated Kill Switch listener not) |
| R-21 | Risk | Handler `ControlDenied` relabelled `IDENTITY` (misrouted credential-compromise runbook); non-RTError exceptions escaped with no audit row; raw denial details logged (REVIEW_C3 F-02, F-03, F-15; local "R-15") | Backend Lead | Gate C | Remediated in dev/sim — IVA verification pending |
| R-22 | Risk | Tenant isolation: allowlists are a single hard-coded dict; BFF read paths carry no tenant predicate and tenant is not an authenticated claim; STRATEGY/INSTRUMENT limits leaked across tenants; no TC-TEN quartet (REVIEW_C3 F-14; REVIEW_C5 F-08 "R-SEC-04"; REVIEW_C4 F-13; NFR-TEN-01; RT-03) | Backend Lead | Gate B/C | Partially remediated — Open (limit leak fixed; reads and allowlist store not) |
| R-23 | Risk | Kill Switch engagement was not fail-closed: side effects ran before the activation was stored; a failing hook left the switch un-engaged with no audit; non-ACCOUNT levels vanish on restart (REVIEW_C4 Objection 1, F-18; local "R-09") | Backend Lead (fix), Independent Validation Agent (verify) | Gate C | Remediated in dev/sim (persist-first) — durable store (R-05), engine-side unknown-state HALT, restart survival of non-ACCOUNT levels, pending-deactivation TTL and PIR gate Open |
| R-24 | Risk | Fail-open defaults on the approval→execution path: missing snapshot at approval routed to LIVE; unknown mode defaulted to LIVE; account-snapshot staleness and tenant mismatch unchecked; negative NAV passed ratio checks; engine exceptions unrecorded (REVIEW_C4 Objection 2, F-07, F-17; local "R-10") | Backend Lead | Gate C | Remediated in dev/sim — IVA verification pending; `KillSwitchFlags` cannot express "unknown"; LIVE not gated by `environment_tag`/`approved_for_production` (R-07) Open |
| R-25 | Risk | Cross-instrument order splitting evaded gross/concentration/leverage/correlated caps; an over-limit book could not be reduced; correlation groups sit outside maker-checker (REVIEW_C4 Objection 3, F-12; local "R-11") | Backend Lead, Trading Risk Committee | Gate C | Remediated in dev/sim (open orders projected, risk-reducing exemption) — reservation between decision and fill and groups-in-policy Open (O-46) |
| R-26 | Risk | RT-DRIFT/RT-VENUE halts targeted "*" and blocked nothing; runtime loss/drawdown halts were skipped when limits were undefined; hard-coded `RuntimeThresholds` (REVIEW_C4 Objection 3, F-05; local "R-12") | Backend Lead, SRE Lead | Gate C | Partially remediated — Open (concrete targets and fail-closed UNDEFINED halts delivered; blocking of each code untested; thresholds still in code, O-03) |
| R-27 | Risk | Liquidation path was executable with any non-empty `liquidation_policy_ref`; emergency-policy fields are not under maker-checker (REVIEW_C4 F-01; local "R-13"; O-08) | Backend Lead, Trading Risk Committee | Gate C (disable) / Gate E (enable) | Partially remediated — Open (approved-policy registry gate delivered; maker-checker on the fields not) |
| R-28 | Risk | Halt/restore defaulted to SUPERVISED (promotion without Gate D); an AGENT could set trading status and, carrying a human role, halt an account (REVIEW_C4 F-02, F-03; local "R-14") | Backend Lead | Gate C | Remediated in dev/sim — abuse tests for agent status/halt Open |
| R-29 | Risk | Limit maker-checker was disconnected from the policy store; unsigned YAML was the real write path; `approved_for_production`/`environment_tag`/`cooling_period_end` unenforced; a 3rd-line checker was accepted at the service layer (REVIEW_C4 F-04; local "R-15") | Backend Lead, MCP Security Agent (signing), Chief Risk Agent (change log) | Gate C | Partially remediated — Open (apply path delivered; signed policy artefact O-22, in-service role checks, LIMIT_MATRIX change log not) |
| R-30 | Risk | Two-person, maker-checker and different-line rules compare `actor_id`/`line` derived from client-asserted headers; one human with two header identities satisfies them (REVIEW_C5 OBJ-2; local "R-SEC-02"; depends on R-06) | Backend Lead, Chief Risk Agent, Security Architect | Gate B | Open |
| R-31 | Risk | Audit chain could not detect tail truncation; the store list is mutable in-process; caller-supplied `ts` allowed backdating; no external WORM anchor (REVIEW_C5 OBJ-3; local "R-SEC-03") | SRE Lead, Security Architect | Gate B/C | Partially remediated — Open (seal/anchor and monotonic ts delivered; off-box anchor publication and append-only interface not) |
| R-32 | Risk | Execution-plane egress was `0.0.0.0/0:443` minus RFC1918 (exfiltration from the plane holding broker credentials); edge reads the execution plane on :8444; DNS egress unmonitored (REVIEW_C5 F-12; local "R-SEC-05" part) | Cloud Architect, Security Architect | Gate B | Partially remediated — Open (documentation-range placeholder CIDR and checker rule delivered; per-adapter CIDRs H-07, DNS monitoring, edge→execution route review not) |
| R-33 | Risk | `disable_flag` accepted an AGENT actor (market access switched off by an agent); `ActorKind` is caller-declared with no credential binding (REVIEW_C5 F-09, F-10; local "R-SEC-07") | Compliance Agent, MCP Security Agent, Backend Lead | Gate C | Partially remediated — Open (human/role check on `disable_flag` delivered, untested by a TC; kind→credential binding depends on R-06) |
| R-34 | Risk | Stored XSS and log injection via `X-Actor-Id` and free-text reasons rendered with `innerHTML`; no CSP; control characters not stripped before logging (REVIEW_C5 F-05; local "R-SEC-09") | Frontend Lead, Backend Lead | Gate B | Partially remediated — Open (output encoding in the console delivered; CSP header and control-character stripping not) |
| R-35 | Risk | Redaction missed account/customer ids, IBANs, IPs, JWTs, payloads and free-text reasons; no per-principal rate limit — 200 malformed intents wrote 414 audit events (REVIEW_C5 F-06, F-19; local "R-SEC-10"; T-11) | SRE Lead, Privacy Lead | Gate C | Partially remediated — Open (id/IBAN/IP patterns added, not asserted by a TC; structured-field redaction and rate limiting not) |
| R-36 | Risk | Execution gateway executed an authorised command after an ACCOUNT Kill Switch / halt when the command arrived by the bus rather than the synchronous pipeline (IVA V-C1; T-38) | Backend Lead, Chief Risk Agent | Gate C | Remediated in dev/sim — gateway `execution_permitted` oracle at submit and retry (TC-EX-009); IVA verification pending (O-56) |
| R-37 | Risk | Gateway accepted unauthenticated or forged `OrderCommand`s from any caller inside the Control plane; `decision_id` was never checked (IVA V-C2; T-39) | Backend Lead, Security Architect | Gate C | Remediated in dev/sim — `CommandAuthoriser` HMAC + decision-provenance check (TC-EX-009); asymmetric key O-53; IVA verification pending |
| R-38 | Risk | `max_position_per_instrument` ignored resting orders: a flat book reached 2x the cap by splitting (IVA-03; T-40) | Backend Lead | Gate C | Remediated in dev/sim — committed position includes open orders (TC-RK-021) |
| R-39 | Risk | Strategy owner could approve an intent of their own strategy because the pipeline never passed `strategy_owner_id` (IVA-04; T-41) | Backend Lead | Gate C | Remediated in dev/sim — pipeline resolves the owner from the strategy registry (TC-AP-005) |
| R-40 | Risk | Fail-open corners: `MakerChecker.reject()` accepted an AGENT actor (IVA-05); BFF header auth treated an unset `RT_ENV` as sim (IVA-06); the published dev registry key was accepted when supplied via `RT_MCP_REGISTRY_KEY` (IVA-07); nonce store was process-local (IVA-08) (T-42, T-43) | Backend Lead, Security Architect | Gate B | Remediated in dev/sim — TC-ID-005, TC-E2E-AUTH, TC-AI-011 |
| R-41 | Risk | `retry_submit` adopted a broker-known live order as ACKNOWLEDGED without consulting the permission oracle or cancelling: an order could stay live at the broker under an active Kill Switch whose cancel hook had failed (REVALIDATION IVA-19, High; T-44) | Backend Lead, Chief Risk Agent | Gate C | Remediated in dev/sim — adopted live orders are cancelled at the broker when execution is blocked; S1 `execution.live_under_block` → killswitch_account if the cancel fails (TC-EX-010 recovery); IVA verification pending (O-56) |
| R-42 | Risk | Command authorisation was neither one-shot nor time-bounded: a cancelled command replayed after a gateway restart, or days later, executed (REVALIDATION IVA-21; T-45) | Backend Lead | Gate C | Remediated in dev/sim — five-minute authorisation age, one-shot MAC, one order per decision ever, intent-state check in the oracle (TC-EX-010 abuse); durable consumed-set [Open: R-05] |
| R-43 | Risk | `authorised_digest()` was non-injective (`k=v` joined with `|`): two distinct commands could share a MAC (REVALIDATION IVA-20) | Backend Lead | Gate B | Remediated — canonical JSON digest (TC-EX-010 positive) |
| R-44 | Risk | Signer reachable by attribute walk from `platform.runtime` in-process; `verify_command=authoriser.verify` exposed `sign` via `__self__` (REVALIDATION IVA-22) | Security Architect | Gate C | Partially remediated — verify-only `CommandVerifier` handle; in-process Python has no isolation boundary, the deployment boundary is a separate gateway process with verification material only [Open: O-53] |
| R-45 | Risk | Auto Kill Switch on `execution.unauthorised_command` used the attacker-chosen `account_id` (halting primitive, REVALIDATION IVA-23); unknown `account_id` raised `KeyError` in the pipeline (IVA-24); inbox dedupe answered before the MAC check (IVA-25) | Backend Lead | Gate B | Remediated — auto-action `none` (S1 page) for unauthorised commands; input providers fail closed to HALTED with audit `eligibility.inputs_unavailable`; MAC verified before the inbox (TC-EX-010 negative) |
| R-46 | Risk | The agent guard can be bypassed by an agent that edits files through Bash (sed, heredocs) instead of Edit/Write; a 2nd- or 3rd-line agent could then author code it reviews (T-48) | Product Owner, MCP Security Agent | Gate B | Mitigated, not closed — guard is a harness guard rail; CODEOWNERS + branch protection (H-01/O-20 team mapping) + IVA review of authorship are the controls; TC-AGT documents the limit |
| R-47 | Risk | `rt365 mcp-serve` issues an 8-hour agent identity (default TTL 5 minutes) so an interactive host session does not expire mid-work; a captured token is usable for the session on the sim tenant (T-47) | Backend Lead, MCP Security Agent | Gate D | Accepted for sim only — sim identity, fixture registry, no broker route; before any non-sim use the TTL and a refresh flow are decided with tool registration (O-35) |
| R-48 | Risk (accepted) | All human approval authority concentrated in one person (D-039): loss of the independent second approver of blueprint 13; an unchallenged decision can pass a gate | Product Owner | Gate A | Accepted by the owner 2026-09-08 with compensating controls: council recommendation and dissent attached to every decision; written override records for any IVA veto; runtime two-person controls unchanged (deputy O-19 required); agents segregated (TC-AGT) and never approving |
| R-49 | Risk | Dual key satisfiable by two Compliance hands: `record_legal` accepted a Compliance Agent as the legal signer (COUNCIL_2026-09-08_gate_A_compliance_legal F-1/P-1; T-51) | Backend Lead, Compliance Agent | Gate D | Remediated in dev/sim 2026-09-08 — legal record requires a human Legal Agent; flag activation requires a human Compliance role; TC-CP-007 (abuse); Compliance Agent review due Gate B (AEI #31) |

## Remediation and evidence for committee review items (2026-09-07)

Scope: commit `09a6e716d50ac9b89a26a9f295fa54509b4492c3` ("Remediate committee review findings (Gate B/C conditions)"). Every claim below was checked against the working tree and `test/quartets/` on 2026-09-07 by the Delivery Orchestrator (AI); test IDs are the `pytest.mark.tc` markers that exist. "Remediated in dev/sim" means the control exists and its test passes in the in-process build — it is not IVA-verified and closes nothing [Source: 00 no self-certification]. Existing IDs are annotated here rather than renumbered.

| ID | Remediation / evidence (commit 09a6e71) — or what is still needed |
|---|---|
| R-02 (existing) | Re-rated Critical by REVIEW_C2 (reproduced without failover). Gateway keeps a `_by_intent` index; `submit()` refuses a command whose intent already has a live order with `DuplicateIntentOrder`, audits `order.command.duplicate_intent_rejected` and raises S1 `execution.duplicate_order` (`services/execution/execution_gateway/gateway.py`); reconciliation groups live orders by `intent_id` → DUPLICATE S1 (`services/reconciliation/reconciliation_service/reconcile.py`); `retry_submit` queries the broker first (R-09). Tests: TC-EX-007, TC-EX-008, TC-RC-003. Still needed: ARB decision O-26/ADR-014; durable index (R-05); a TC for intent-level DUPLICATE from a statement (proposed TC-RC-008 not implemented). |
| R-05 (existing) | No code change. The reviews add to the in-memory list: gateway `_by_intent`, nonce cache, `RevocationList` (JSONL only), Kill Switch activations, audit anchor (REVIEW_C2 F-09, REVIEW_C3 OBJ-3d, REVIEW_C4 F-18, REVIEW_C5 OBJ-3). RTM rows FR-13/NFR-CON-01 now state that dev/sim evidence is labelled "dev". |
| R-06 (existing) | `human()` refuses `strategy_agent`/`runtime_monitor`/`system` roles with a `plane.deny` alert; `create_app` refuses to start when `RT_ENV != sim` (`apps/web/web_bff/app.py`). Test: TC-E2E-AUTH. Still needed: IdP/OIDC session, mTLS, removal of the hard-coded `mfa_enrolled=True`/`privileged_until=+1y` in `require()`, separate agent and human listeners (REVIEW_C3 F-04, REVIEW_C5 OBJ-1). |
| R-07 (existing) | REVIEW_C4 F-04 confirms `approved_for_production`, `environment_tag` and `cooling_period_end` are consumed by no code path; the guard named in R-07 is not yet a guard. Open. |
| R-08 (existing) | REVIEW_C4 F-20/F-22 add: `age_seconds` returns float, decimal context not pinned inside `decide()`, `ENGINE_BUILD_HASH` covers `risk_engine/*.py` only, `correlation_groups.items()` order comes from the builder. Not changed in 09a6e71. |
| O-09 (existing) | `holds_for(*scopes)` matches any enclosing scope; missing schedule → `SUPPRESSED_NO_SCHEDULE`; `release_hold` requires a human Legal/Compliance actor (`services/compliance/compliance_engine/retention.py`; D-025). Test: TC-CP-006 (customer + account scopes; human release). Still needed: TC for the no-schedule outcome and for a tenant-scope hold vs customer deletion (proposed TC-CP-008); two-person release; DPIA (O-10). |
| O-22 (existing) | `load_registry` accepts the dev key only when `RT_ENV ∈ {dev, sim}`; the signature covers an envelope (registry, key_id, algorithm, environment_tag, registry_version, signed_at, fixture); `environment_tag` must equal `RT_ENV`; CI asserts that `verify_tool_registry.py --production` FAILS on the fixture; docker-compose requires the key variable (`mcp/servers/mcp_servers/registry.py`, `scripts/sign_tool_registry.py`, `scripts/verify_tool_registry.py`, `.github/workflows/ci.yml`, `infra/docker-compose.yml`). Test: TC-AI-010. Still needed: the asymmetric KMS key itself; extension to the risk-policy artefact (REVIEW_C4 F-04, R-29). |
| O-23 (existing) | bandit (SAST) and pip-audit (SCA) run advisory-only (shell `or true`) against a generated `requirements.lock.txt`; the SBOM walks the declared dependency closure instead of the ambient environment (`Makefile`, `.github/workflows/ci.yml`, `scripts/generate_sbom.py`). Still needed: gating scanners, DAST, image signing/verification, signed SBOM, hash-pinned installs, TC-SC-001/002 (REVIEW_C5 F-14..F-17). |
| O-27 | `BrokerAdapter.query_order` → `OrderStatus` delivered (`connectors/brokers/broker_adapters/base.py`, `simulated.py`). Still needed: status enum on `StatementOrder`/`OrderStatus`; venue-side cancel/expiry event; gateway consults `Capabilities.supports()` before submit (TC-EX-006 still passes because the broker rejects); certification run in both dedupe modes. |
| O-28 | `LeaseStore.renew` exists (`services/execution/execution_gateway/lease.py`); no caller; `preempt` still unauthenticated. Open as stated. |
| O-30 | `killswitch.activated.v1`/`deactivated.v1` are now published on the outbox and their contracts carry `hook_failures` (`contracts/events/killswitch.*.v1.json`; `apps/web/web_bff/platform.py` `ks_audit`); `reconciliation.break.v1` schema updated; reconciliation events remain audit-only. OpenAPI/BFF parity edits are present in the working tree, uncommitted (`contracts/api/API_OPENAPI.yaml`, `test/contract/test_openapi_alignment.py`) — not part of 09a6e71 and not counted here. |
| O-31 | `target_pct_nav` 5 → 4 % (`services/strategy/strategy_service/signals.py`). Reason-code distribution and exploratory labelling Open. |
| O-32 | `docs/BROKER_CERTIFICATIONS/sim-broker.md` exists (reviewer pending). Harness gaps Open. |
| O-33 | Intent machine gains FILLED/CANCELLED/BROKER_REJECTED → RECONCILED → ARCHIVED; order machine gains SUBMITTED→CANCELLED/EXPIRED and ACKNOWLEDGED→EXPIRED (`services/oms/oms/lifecycle.py`, `gateway.py`). Nothing calls the RECONCILED transition yet; REPLACED and async ack mapping Open. |
| O-35 | `sign_registry` refuses to sign a registry with pending approvals unless `--sim-fixture`; the loader refuses a fixture outside dev/sim; `tool_registry.signed.json` carries `fixture: true` (`registry.py`, `scripts/sign_tool_registry.py`). Test: TC-AI-010. The approval records themselves are still pending. |
| O-38 | Keyed pseudonym for `account_ref` (`mcp/servers/mcp_servers/tools.py`); TC-AI-001 asserts the raw account id is absent from the output. Masking policy document Open. |
| O-39 | `strategy_version` is part of `AgentIdentity` and enforced on submit and simulation (`identity.py`, `tools.py`); handlers receive a `Principal` without the secret (`runtime.py`). Test: TC-AI-010. Issuance/transport Open. |
| O-40 | Quota keyed per (tenant, account, strategy, tool) plus a tenant ceiling; denials consume a deny bucket; clock injected via `quota_clock` (`runtime.py`). Test: TC-AI-003. Catalog re-issue Open. |
| O-46 | `risk_reducing_orders_exempt_exposure_caps: true` in `services/risk/policies/sim-policy-v0.1.yaml` marked "[Committee] pending Trading Risk Committee"; D-022. TRC decision Open. |
| O-47 | `decision_id` now includes `now.isoformat()` (`services/risk/risk_engine/engine.py`). Wording, LIMIT_MATRIX rows and dead knobs Open. |
| O-49 | `RK-FRESH-INTENT` (intent `market_ts` not ahead of `now`) exists in `engine.py`; the other controls do not. Open. |
| O-50 | `scripts/secret_scan.py`: rglob fallback, fail on zero files, four new patterns. Remaining pattern gaps Open. |
| R-09 | `query_order`/`OrderStatus` (`base.py`, `simulated.py`); SUBMITTED→CANCELLED/EXPIRED transitions; `cancel()` of a SUBMITTED order queries the broker and cancels locally with reason "never reached broker" when unknown; `expire_unacked` and `sync_statuses` in `gateway.py`. Tests: TC-EX-008 (retry adopts the existing order on a non-deduping broker), TC-RC-005 (broker-side IOC cancel adopted). Still needed: a scheduled re-driver/expiry job on real infra; a TC for the orphan-expiry path (proposed TC-EX-010). |
| R-10 | `BreakType.STATUS` S1 for internal terminal vs broker open and vice versa, carrying the order's correlation id (`reconcile.py`); `Fill.fee` and `AccountBook.fees_paid` (`libs/core/rtcore/schemas/order.py`, `services/portfolio/portfolio_service/ledger.py`); one open ticket per (account, type, instrument); second resolver must sit in a different line (`services/reconciliation/reconciliation_service/tickets.py`). Tests: TC-RC-005, TC-RC-004. Still needed: fee/accrual model and tolerances (O-29); clean-run-before-restore rule; reconciliation events on the outbox (O-30); TCs for a fee-bearing statement and ticket dedupe (proposed TC-RC-005 fee case, TC-RC-009). |
| R-11 | `OrderCommand.strategy_id` (`libs/core/rtcore/schemas/order.py`); `cancel_all`/`affected_accounts` filter by account, tenant, strategy, instrument, venue; platform `cancel_open` preempts only the affected accounts' leases (`apps/web/web_bff/platform.py`, `gateway.py`). Test: TC-KS-008. Still needed: per-level drill evidence (H-19). |
| R-12 | `Fill.fee` flows through `Ledger.apply_fill`; `run_sim_backtest` sets the simulated broker's `fee_bps`/`spread_bps` so costs are charged inside the pipeline (`platform.py`). Tests: TC-BT-001..003 (existing, not re-scoped). Still needed: a TC proving paper = backtest fees (proposed TC-BT-005); financing/borrow, slippage in price, settlement (O-34). |
| R-13 | The gateway saves `order.created` without publishing, so `order.command.v1` has one producer (`oms.pipeline`) (`gateway.py` `_save(rec, "order.created", now, publish=False)`; `services/oms/oms/pipeline.py`). Test: TC-AUD-001 (one `order.command.v1` per correlation). Still needed: emitted-event validation in CI (O-30). |
| R-14 | `apply_fill` records late/over-fills as `order.fill.unexpected` with alert `execution.unexpected_fill` instead of raising (`gateway.py`). Still needed: gateway consults Kill Switch state before submit; cancel REJECTED acks alerted/audited (today ALREADY_FILLED triggers a poll, other rejections return silently); broker-unavailable on poll alerted; lease acquired before `order.command.v1` is published (`pipeline.py` `_authorise_and_execute`); `(record, deduped)` return. No TC. |
| R-15 | `CallSignature(nonce, issued_at, signature)`, per-token nonce cache, `CALL_MAX_AGE` (`mcp/servers/mcp_servers/identity.py`); the BFF agent path reads `X-Call-Nonce`/`X-Call-Issued-At` (`apps/web/web_bff/app.py`); `IntentQueue.submit` refuses a tracked `intent_id` and `IntentTracker.create` raises (`services/oms/oms/intent_queue.py`, `lifecycle.py`); economic duplicate via `recent_order_signatures` (`engine.py`, `ledger.py`, `libs/core/rtcore/schemas/account.py`). Tests: TC-AI-009, TC-RK-015. Still needed: nonce-cache durability (R-05). |
| R-16 | `build_sim_platform` constructs a private `PlaneGuard` and injects it into the gateway (`ExecutionGateway(guard=...)`); `run_sim` builds a throwaway BACKTEST platform; `run_simulation` validates the template against `APPROVED_SIMULATION_TEMPLATES` and the strategy/version against the identity and registry status (`mcp/servers/mcp_servers/tools.py`, `apps/web/web_bff/platform.py`, `libs/core/rtcore/planes.py`). Test: TC-AI-006. ADR-013, D-027. Still needed: worker-process isolation with resource limits (option B) or removal (option C) before Gate D; TC-AI-005 scan extended to handler modules (O-45). |
| R-17 | Auto-action `revoke_tool_for_scope` revokes the (tenant, account, strategy, tool) grant only (`allowlist.py` `revoke_grant`; `platform.py` `revoke_grant_for_scope` bound with `required=`); `RevocationList` persisted to JSONL and read at start-up (`mcp/servers/mcp_servers/revocation.py`); `AlertRouter.on(required=...)` raises S1 `alert.autoaction_failed` instead of a silent no-op (`observability/rtobs/alerts.py`, `observability/alerts.yaml`); denials consume a deny bucket before the allowlist check (`runtime.py`). Tests: TC-AI-003, TC-AI-008, TC-OB-005. Still needed: `agent` in the payloads of `plane.deny`, `killswitch.agent_attempt`, `risk.integrity_violation` so the revocation actually happens (today they fail loudly, not silently); replicated revocation head; revocation drill (H-19); two-person tenant-wide revocation path. |
| R-18 | `analytics-allow-intent-queue` podSelector `NotIn component=mcp-server`, ports on every rule (`infra/kubernetes/network-policies/analytics.yaml`, `mcp-servers.yaml`); `scripts/check_network_policies.py` computes the effective egress union per pod label set and refuses `0.0.0.0/0`. Test: TC-NET-003 (existing static check). Still needed: cluster conformance test (H-05); O-37. |
| R-19 | `ToolRuntime.call` delimits every string field of an output whose provenance is not in `TRUSTED_FOR_DECISIONS` (`runtime.py` `_delimit_strings`). Test: none asserts delimiting of `get_strategy_docs` output (proposed TC-AI-002b). Still needed: that test; corpus O-36. |
| R-20 | Handler runs under `future.result(timeout=spec.timeout_s)` → `TIMEOUT` with `mcp.handler_timeout`; the BFF calls the runtime via `run_in_executor` (`runtime.py`, `app.py`); `calculate_indicator` reads are bounded (`tools.py`). Test: none for the timeout (TC-AI-010 covers handler error only). Still needed: body-size cap on the agent listener; Kill Switch endpoint on an isolated path/process; proposed TC-SEC-MCP. |
| R-21 | Identity verified in its own `try` (`IDENTITY`); handler `ControlDenied` → `HANDLER_DENIED`; any other exception → `HANDLER_ERROR` with audit `mcp.tool.denied` and alert `mcp.handler_error`; deny rows carry `detail_hash` and actor `agent:<id>` (`runtime.py`). Test: TC-AI-010. |
| R-22 | STRATEGY/INSTRUMENT limits are tenant-qualified and unqualified ones are ignored below tenant level (`services/risk/risk_engine/policy.py`); `RK-AUTH-TENANT` (`engine.py`). Test: TC-RK-018. Still needed: tenant predicate on BFF reads (`get_decision`, `account`, `audit_search`/`audit_export`), tenant as an authenticated claim, versioned per-tenant allowlist store, TC-TEN quartet (RT-03). |
| R-23 | `activate()` stores the `Activation` and audits `killswitch.engaged` before any hook; each hook runs in `attempt()` with `hook_failures` recorded and S1 `killswitch.hook_failed` (`services/killswitch/killswitch_service/service.py`). Test: TC-KS-007. D-020. Still needed: durable activation store (R-05); `KillSwitchFlags.as_of`/`state_known` and `RK-HALT-KS-UNKNOWN`; restart survival of non-ACCOUNT levels (the proposed restart TC is not implemented — the delivered TC-KS-008 covers cancel scope); pending-deactivation TTL; PIR reference for PLATFORM/TENANT deactivation. |
| R-24 | `TARGET_FOR_MODE` is an explicit map and an unknown mode raises `ControlDenied`; `on_approval` re-runs `decide()` on fresh snapshots, audits `risk.redecided.v1` and halts/rejects on change (`services/oms/oms/pipeline.py`); `RK-AUTH-TENANT`, account-snapshot age vs freshness budget → `RK-HALT-INPUT`, `RK-NAV`, pre-trade `RK-LOSS`, engine exception → `RK-HALT-INPUT` (`engine.py`; `docs/REASON_CODES.md`). Tests: TC-RK-018, TC-RK-019. Still needed: `KillSwitchFlags` unknown state; LIVE gated by `environment_tag`/`approved_for_production` (R-07); a TC-AP case for a missing snapshot at approval. |
| R-25 | `_projected_positions` includes open-order notional; same-side open aggregation; `_cap_check(current=...)` passes a risk-reducing order when the metric does not worsen, including correlated groups (`engine.py`; flag in `sim-policy-v0.1.yaml`). Test: TC-RK-017. D-022. Still needed: TRC decision O-46; reservation or serialisation between decision and fill; correlation groups in the policy artefact. |
| R-26 | Monitors halt per concrete strategy id (or the ACCOUNT when none is named) and per concrete venue (or the ACCOUNT); undefined loss/drawdown limits → `RT-*-UNDEFINED` ACCOUNT halt (`services/risk/risk_engine/monitors.py`; `docs/REASON_CODES.md`). Test: TC-RK-016 (events exist). D-023. Still needed: a test that each of the ten codes blocks the next intent (only RT-LOSS-DAILY in TC-KS-006); `RuntimeThresholds` defaults removed and sourced from policy (O-03); monitor heartbeat/dead-man's switch. |
| R-27 | `KillSwitchService.approved_liquidation_policies`; an unapproved or absent ref falls back to CANCEL_ONLY and the fallback is recorded (`service.py`). Test: `test_emergency_policy_reduce_without_liquidation_policy_falls_back` (no TC id). Still needed: maker-checker on `emergency_policy`/`liquidation_policy_ref`; O-08 registry with versions and effective dates; a TC id. |
| R-28 | `restore_from_halt` ceiling = `enabled_feature` capped at SUPERVISED; BOUNDED_AUTONOMOUS/HALTED refused as targets; human + `MODE_CHANGERS` required; `set_trading_status` restricted to authorised human roles; `halt()` refuses AGENT (`services/identity/identity_service/accounts.py`). Test: TC-KS-004 (default restore target = enabled feature PAPER). D-021. Still needed: abuse tests for agent `set_trading_status`/`halt` and for a restore above the ceiling. |
| R-29 | `apply_change` produces a new policy version `<base>+<change_id>`; `SimPlatform.apply_effective_limits` applies EFFECTIVE changes after cooling; `limit.changed.v1` audited (`policy.py`, `platform.py`). Test: TC-RK-020. Still needed: signed policy artefact and `RK-HALT-POLICY` (O-22); role checks inside `MakerChecker` (3rd-line checker denied); LIMIT_MATRIX change log; `approved_for_production`/`environment_tag` enforcement (R-07); TC for an unsigned policy (proposed TC-RK-023). |
| R-30 | Not remediated. The human path refuses non-human roles (R-06) but `actor_id`/`line` remain header-derived. Still needed: authenticated subject (IdP `sub`) plus session compared by every two-person/maker-checker check; abuse tests (proposed TC-ID-007, TC-AP-005). |
| R-31 | `AuditStore.seal()` → `ChainHead(length, head_hash, sealed_at)`; `verify(anchor=)` reports "chain truncated" / "sealed head does not match"; `append(ts=)` clamps to the previous event's timestamp (`services/audit/audit_service/store.py`). Test: TC-AUD-005. D-024. Still needed: anchor published off-box (WORM bucket/replica per DR_PLAN); `_events` behind an interface without pop/slice; server-received timestamp recorded alongside the event timestamp. |
| R-32 | Execution egress uses the RFC 5737 documentation range as a sim placeholder with a per-adapter comment; checker rule 7 refuses `0.0.0.0/0` (`infra/kubernetes/network-policies/execution.yaml`, `scripts/check_network_policies.py`). Still needed: real broker CIDRs from certified adapters (H-07); DNS egress monitoring; threat-model treatment of the `EDGE→EXECUTION api_read` route. |
| R-33 | `disable_flag` requires a human Compliance/Legal role (`services/compliance/compliance_engine/jurisdiction.py`). Test: none (proposed TC-CP-007). Still needed: that abuse test; kind→credential binding at the control boundary (depends on R-06). |
| R-34 | `esc()` output-encoding for every interpolated value in `apps/web/static/index.html`. Still needed: CSP header; control-character stripping in `observability/rtobs/logging.py`; error bodies must not echo the role header; proposed TC-SEC-003. |
| R-35 | Redaction patterns for `acct-`/`cust-`/`tenant-` ids, IBAN and IPv4 (`observability/rtobs/logging.py`). Test: TC-OB-002 was not extended (the new TC-OB-005 covers alert auto-actions, not redaction). Still needed: structured field-level redaction, payload/reason redaction, per-principal rate limit, no audit of pre-validation floods (proposed TC-PERF-004). |
| R-36..R-40 (IVA cycle 1) | IVA remediation commit (2026-09-07, branch claude/attachment-solution-dev-52k8u0, after 09a6e71): `services/execution/execution_gateway/authorisation.py` (CommandAuthoriser), `gateway.py` (`_assert_authorised`, `_assert_executable` at submit and retry; alerts `execution.unauthorised_command` S1 → killswitch_account, `execution.blocked_at_gateway` S1; audit `order.command.unauthorised` / `order.command.blocked`), `apps/web/web_bff/platform.py` (`execution_permitted` oracle: Kill Switch > halt/status > mode/target > decision provenance; authorisation key created in the composition root and handed only to the pipeline and gateway), `services/risk/risk_engine/engine.py` (`chk_caps` committed position includes open orders), `services/oms/oms/pipeline.py` (`strategy_owner` resolver, `sign_command`), `services/identity/identity_service/makerchecker.py` (`reject` human-only, pending-only), `apps/web/web_bff/app.py` (`RT_ENV` must equal `sim`), `mcp/servers/mcp_servers/registry.py` (dev key black-listed outside dev/sim from any source), `mcp/servers/mcp_servers/identity.py` (per-agent nonce journal, `adopt()`). Tests: TC-EX-009 (positive/negative/abuse/recovery), TC-RK-021, TC-AP-005, TC-ID-005, TC-AI-011, TC-E2E-AUTH. Still needed: O-53, O-54, O-55, O-56. |
| R-41..R-45 (IVA re-validation) | re-validation remediation commit (2026-09-07, after c0bb1fb): `gateway.py` (`COMMAND_MAX_AGE`, `_consumed_authorisations`, `_by_decision`, `_cancel_if_blocked` on retry adoption, MAC before inbox), `authorisation.py` (`CommandVerifier`), `order.py` (`canonical_json` digest), `platform.py` (oracle intent-state check; `nonce_path` wired), `pipeline.py` (inputs fail closed), `observability/alerts.yaml` (`execution.unauthorised_command` auto-action none; `execution.live_under_block`). Tests: TC-EX-010 (positive/negative/abuse/recovery). Still needed: O-53, O-55 (journal compaction), O-56 re-validation. |

## Review ID renumbering map (2026-09-07)

Four independent committee reviews (docs/SESSIONS/REVIEW_C2_P1_P6_trading_integration.md, REVIEW_C3_mcp_security_agent.md, REVIEW_C4_P4_chief_risk_agent.md, REVIEW_C5_C1_C9_security_redteam.md) each allocated local RAID/risk/threat/test IDs that collide with each other and with this log. The reviewers' texts are unchanged; this map is the only authority for global IDs. Rules applied: nothing already in the master logs was renumbered; new open items start at O-26, new risks at R-09, new decisions at D-015, new ADRs at ADR-013, new threats at T-14; an item that duplicates an existing master item maps to the existing ID; a finding that was fully remediated with no residual maps to the decision (D-nnn) that records the remediation. "Local ID" quotes the reviewer's own label. Compiled by the Delivery Orchestrator (AI); reviewer: pending (Independent Validation Agent); approver: pending (CAB).

| Review | Local ID | Global ID | Title |
|---|---|---|---|
| C2 | OBJ-1 | R-02 (re-rated Critical), O-26, ADR-014, T-26, D-015 | Nothing enforces one live broker order per intent; ADR-003 makes a second one legitimate |
| C2 | OBJ-2 | R-02, R-09, O-27, T-27, D-016 | SUBMITTED-but-unacked path unsafe on both branches (duplicate on non-deduping broker; permanent orphan) |
| C2 | OBJ-3 | R-10, O-29, D-017 | Reconciliation compares quantities only, never order status or fees |
| C2 | F-01 | R-11 | STRATEGY-level Kill Switch cancels platform-wide; every level preempts every account's lease |
| C2 | F-02 | O-28 | Lease TTL 30 s, renewal only on submit, no heartbeat |
| C2 | F-03 | O-28 | Lease acquired by the Control-plane coordinator; `preempt` unauthenticated; CP store untested |
| C2 | F-04 | R-14 | Execution Gateway does not consult the Kill Switch |
| C2 | F-05 | R-14 | `cancel()` swallows non-CANCELLED acks; evidence under-reports live exposure |
| C2 | F-06 | O-33 | No cancel/replace path in the gateway |
| C2 | F-07 | R-14 (this part remediated) | Duplicate/late fill handling raised instead of recording |
| C2 | F-08 | R-14 | Broker-unavailable on poll swallowed silently |
| C2 | F-09 | R-05 | Outbox/inbox/gateway index neither durable nor transactional |
| C2 | F-10 | R-14 | Deduped vs new command indistinguishable to the caller |
| C2 | F-11 | R-09, O-33 | Order machine incomplete for real venue behaviour |
| C2 | F-12 | R-15 (remediated) | `IntentTracker.create` not idempotent; resubmission reset a FILLED intent |
| C2 | F-13 | O-33 | RECONCILED/ARCHIVED unreachable; EXPIRED semantics half-implemented |
| C2 | F-14 | R-14 | `order.command.v1` published and intent AUTHORISED before the lease is acquired |
| C2 | F-15 | O-33 | Asynchronous ack never reaches the intent |
| C2 | F-16 | R-10, O-29 | Severity mapping; "DUPLICATE" used for phantom orders; tolerances are fixtures |
| C2 | F-17 | R-10 (remediated for STATUS breaks) | Correlation IDs on breaks are coarse |
| C2 | F-18 | O-34, R-12 | Ledger gaps: mark fallback, buying power, fee, per-trade PnL, multi-currency |
| C2 | F-19 | O-30 | Reconciliation events never published on the outbox |
| C2 | F-20 | R-10 | Ticket correlation fallback, unstructured resolution, unindexed tickets |
| C2 | F-21 | O-32 | Certification harness vs the 10-row checklist |
| C2 | F-22 | O-32 | Simulated broker realism limits must be stated |
| C2 | F-23 | O-27 | `Capabilities` half-consumed; rejection happens at the broker, not before submit |
| C2 | F-24 | O-27 | `StatementOrder.status` is a free string |
| C2 | F-25 | R-12 | Costs applied outside the pipeline; BACKTEST ≠ PAPER |
| C2 | F-26 | R-12 | Decision time one bar newer than the signal; NAV between bars at cost |
| C2 | F-27 | O-31 | Sample strategy sizing blind to the limit matrix |
| C2 | F-28 | O-31 | Exploratory backtest reports not labelled |
| C2 | F-29 | R-13 (remediated) | Gateway `order.command.v1` payload violates the registered schema |
| C2 | F-30 | O-30 | Catalog ↔ code drift (producers, state enums, market_ts, audit-only events) |
| C2 | F-31 | O-30 | OpenAPI ↔ BFF drift |
| C2 | R-02 (existing) | R-02 | Duplicate orders — re-rated Critical |
| C2 | R-05 (new, local) | R-09 | SUBMITTED-but-unacked orphan |
| C2 | R-06 (new, local) | R-10 | Reconciliation blind to order status and fees |
| C2 | R-07 (new, local) | R-11 | Kill Switch STRATEGY level cancels platform-wide |
| C2 | R-08 (new, local) | R-05 | In-memory stores presented as Gate C evidence |
| C2 | R-09 (new, local) | R-12 | Backtest ≠ paper on costs |
| C2 | R-10 (new, local) | R-13 | Gateway payload violates schema |
| C2 | A-01 (new, local) | O-27 | Assumption that brokers dedupe `client_order_id` |
| C2 | O-20 (new, local) | O-26 | ADR-003 rev.2 decision |
| C2 | O-21 (new, local) | O-27 | Adapter contract: `query_order`, status enum, venue-side events |
| C2 | O-22 (new, local) | O-28 | Lease TTL, heartbeat, submit timeout, re-drive cadence |
| C2 | O-23 (new, local) | O-29 | Reconciliation tolerances and fee model |
| C2 | O-24 (new, local) | O-30 | EVENT_CATALOG v1.1; OpenAPI parity |
| C2 | O-25 (new, local) | O-31 | Strategy sizing; reason-code distribution; exploratory labels |
| C2 | D-01 (new, local) | O-32 | `sim-broker.md` never generated (now exists; review pending) |
| C2 | §7 RTM FR-13a–d, FR-14a–c, FR-17a | RTM rows FR-13, FR-14, FR-17 (Notes) | Proposed RTM sub-rows folded into the existing rows' Notes |
| C2 | §7 RTM FR-02a, FR-08a, NFR-CON-01 (Gate D), NFR-CON-03, API-01 | O-27, O-34, R-05, O-30 | Proposed rows not added; tracked as open items |
| C2 | TC-EX-007 (proposed) | TC-EX-007 | Second command for the same intent under a new policy version → refused |
| C2 | TC-EX-008 (proposed: lease expiry mid-flight) | not implemented (O-28) | The delivered TC-EX-008 is the local TC-EX-009 case |
| C2 | TC-EX-009 (proposed) | TC-EX-008 | Ack lost, non-deduping broker → one broker order |
| C2 | TC-EX-010, TC-EX-011, TC-EX-012 (proposed) | not implemented (R-09, R-05, R-14) | Orphan cleared; durable inbox restart; late-fill recorded |
| C2 | TC-RC-005 (proposed: fee-bearing statement) | not implemented (O-29) | The delivered TC-RC-005 is the local TC-RC-006/007 case |
| C2 | TC-RC-006, TC-RC-007 (proposed) | TC-RC-005 | STATUS break S1; broker-side cancel adopted |
| C2 | TC-RC-008 (proposed) | not implemented (R-02) | Two broker orders for one intent → DUPLICATE (code exists in `reconcile.py`, untested) |
| C2 | TC-RC-009 (proposed) | TC-RC-004 (different line only) | Different-line resolver; clean run before restore; ticket dedupe; RECONCILED |
| C2 | TC-KS-007 (proposed: cancel scope) | TC-KS-008 | The delivered TC-KS-007 is the C4 hook-failure case |
| C2 | TC-BR-006..010 (proposed) | not implemented (O-27, O-32) | Capability rejection before submit; cancel/fill race; non-deduping resubmission; executed reconcile; DAY expiry |
| C3 | OBJ-1 | R-16, ADR-013, T-28, D-027 | `run_simulation` disables the S1 plane-deny alert and destroys deny evidence |
| C3 | OBJ-2 | O-22, O-35, T-29 | Registry trust root: public symmetric key with silent fallback; forged registry accepted |
| C3 | OBJ-3 | R-17, T-30, D-018 | Tenant-wide revocation by a low-privilege agent; no-op auto-actions; restart un-revokes |
| C3 | F-01 | R-15, T-31, D-019 | Replay of a signed call |
| C3 | F-02 | R-21 (remediated) | Handler `ControlDenied` relabelled `IDENTITY` |
| C3 | F-03 | R-21 (remediated) | Non-RTError exceptions escape without audit |
| C3 | F-04 | R-06 | Header forgery reaches limits, Kill Switch, audit export |
| C3 | F-05 | R-20 | Post-hoc timeout; hung handler blocks the BFF |
| C3 | F-06 | O-40 (quota part remediated) | Quota semantics differ from the catalog |
| C3 | F-07 | O-39 (`strategy_version` remediated) | Identity scoping incomplete |
| C3 | F-08 | O-39 | Identity issuance unauthenticated and unaudited |
| C3 | F-09 | R-20 | Payload limits checked after an unbounded body is parsed |
| C3 | F-10 | D-026 (remediated) | Output-schema validation shallow |
| C3 | F-11 | O-44 | Canary tokens are not canaries |
| C3 | F-12 | O-36 | Injection corpus is one hard-coded string |
| C3 | F-13 | R-19 | Provenance labelling offered, not applied |
| C3 | F-14 | R-22 | Tenant isolation of allowlists is a single hard-coded dict |
| C3 | F-15 | R-21 (remediated) | Runtime logs raw denial details into the chain |
| C3 | F-16 | O-38 | `read_account_state` masking undefined and weak |
| C3 | F-17 | R-16 (residual) | `run_simulation` resource bounds |
| C3 | F-18 | R-20 (remediated) | `calculate_indicator` unbounded read |
| C3 | F-19 | R-18, T-20 | NetworkPolicy union defeats MCP egress restriction |
| C3 | F-20 | O-45 | In-process egress guard decorative; AST scan scope |
| C3 | F-21 | O-22 (remediated) | Registry loading strictness; env-tag check |
| C3 | F-22 | D-014 / AUDIT_EVIDENCE_INDEX | Evidence records self-attested (reviewer signature pending by design) |
| C3 | F-23 | O-40 | Catalog "Proposed" while registry signed; claims not true in code |
| C3 | R-09 (local) | R-16 | `run_simulation` mutates the global plane guard |
| C3 | "O-22 / O-27 (existing)" (O-27 exists only in the 1st-line packet C03) | O-22 | Registry trust root; KMS key; fail-closed load |
| C3 | "O-28 (existing)" (1st-line packet C03) | O-35 | Approval-record placeholders; no signing while pending |
| C3 | R-10 (local) | R-17 | Revocation/auto-action model |
| C3 | R-11 (local) | R-15 | Replay of a signed tool call |
| C3 | R-06 (existing) | R-06 | BFF client-asserted headers (evidence added) |
| C3 | R-12 (local) | R-18 | NetworkPolicy allow-union |
| C3 | R-13 (local); C03 "O-29" | R-19; O-36 | Provenance labelling never applied; corpus absent |
| C3 | R-14 (local) | R-20 | Hung handler blocks the BFF |
| C3 | R-15 (local) | R-21 | Misrouted denials; unaudited exceptions |
| C3 | O-30 (local) | O-37 | Account-state route for `analytics-account` |
| C3 | O-31 (local) | O-38 | Masking policy |
| C3 | O-32 (local) | O-39 | Token issuance and transport |
| C3 | O-33 (local) | O-40 | Quota keyed per scope; denials counted; clock injected |
| C3 | O-34 (local) | O-41 | Monitoring-state integrity as a standing abuse case |
| C3 | A-C3-1 | O-05 (note) | No LLM wired; findings model-independent |
| C3 | A-C3-2 | O-42 | NetworkPolicy additive semantics unverified on a cluster |
| C3 | C03 packet "T-18" (registry key compromise) | T-29 | Confirmed and severity raised by C3 |
| C3 | C03 packet "T-19" (quota exhaustion) | T-30 | Confirmed and widened by C3 |
| C3 | TC-AI-006 (proposed) | TC-AI-006 | Monitoring integrity after `run_simulation` |
| C3 | TC-AI-007 (proposed) | covered inside TC-AI-003 (no TC-AI-007 marker exists) | Per-strategy revocation scope |
| C3 | TC-AI-008 (proposed) | TC-AI-008 | Revocation survives restart |
| C3 | TC-AI-009 (proposed) | TC-AI-009 | Replay |
| C3 | TC-AI-010 (proposed) | TC-AI-010 | Registry key/environment fail-closed |
| C3 | TC-AI-011, TC-AI-002b, TC-TEN-MCP, TC-SEC-MCP, TC-NET-003b/005 (proposed) | not implemented (O-38, R-19, R-22, R-20, R-18) | Masking; delimited docs; cross-tenant allowlist; hung handler; policy union |
| C3 | TC-ID-005 (proposed) | TC-E2E-AUTH (partial) | Forged non-human role headers refused; non-sim start refused |
| C3 | §7 RTM FR-09 rows; NFR-SEC-01; NFR-PRIV (new) | RTM row FR-09 (Notes); O-38 | Proposed rows folded into FR-09; NFR-PRIV tracked as O-38 |
| C4 | Objection 1 | R-23, T-32, D-020 | Kill Switch engagement not fail-closed |
| C4 | Objection 2 | R-24, T-33 | Fail-open defaults on the execution path |
| C4 | Objection 3 | R-25, R-26, T-34, D-022, D-023 | Order splitting across instruments; trapped over-limit book; runtime controls that block nothing |
| C4 | F-01 | R-27, T-37 | Liquidation gated only by a non-empty string |
| C4 | F-02 | R-28, T-36, D-021 | `restore_from_halt` defaults to SUPERVISED |
| C4 | F-03 | R-28, T-36 | `set_trading_status`/`halt` accept agents |
| C4 | F-04 | R-29 | Limit maker-checker disconnected from the policy store |
| C4 | F-05 | R-26, O-03 | `RuntimeThresholds` numeric defaults in code |
| C4 | F-06 | O-47 (`decision_id` part remediated) | `decision_id` ignores decision time |
| C4 | F-07 | R-24 (remediated) | Negative NAV passes ratio checks |
| C4 | F-08 | O-47 | `concentration_action` and `complex_asset_classes` dead |
| C4 | F-09 | O-49 | Protective stop not bounded |
| C4 | F-10 | O-49 | SELL_SHORT bypasses buying power |
| C4 | F-11 | R-15 (remediated) | Economic duplicate with a new id evades RK-DUP |
| C4 | F-12 | R-25 | Correlation groups outside policy |
| C4 | F-13 | R-22 (remediated) | STRATEGY/INSTRUMENT limits leak across tenants |
| C4 | F-14 | O-49 (partial) | Intent age not budgeted |
| C4 | F-15 | O-49 | MARKET orders bypass the collar |
| C4 | F-16 | O-49 | Undefined envelope degrades to supervised instead of halting |
| C4 | F-17 | R-24 (remediated) | `decide()` not wrapped; exceptions unrecorded |
| C4 | F-18 | R-23, R-05 | Kill-switch state in memory; non-ACCOUNT levels vanish on restart |
| C4 | F-19 | O-47 | RISK_POLICY "fail-fast" wording |
| C4 | F-20 | R-08 | Float age; decimal context; build-hash scope |
| C4 | F-21 | O-47 | Loss % base undefined |
| C4 | F-22 | R-08 | Correlation group iteration order |
| C4 | F-23 | O-47 | LIMIT_MATRIX missing rows |
| C4 | F-24 | O-48 | Cooling period symmetric |
| C4 | R-09 (local) | R-23 | Kill Switch engagement not fail-closed |
| C4 | R-10 (local) | R-24 | Fail-open defaults |
| C4 | R-11 (local) | R-25 | Cross-instrument splitting |
| C4 | R-12 (local) | R-26 | Runtime halts that block nothing |
| C4 | R-13 (local) | R-27 | Liquidation path |
| C4 | R-14 (local) | R-28 | Halt/restore promotion; agent status changes |
| C4 | R-15 (local) | R-29 | Maker-checker disconnected |
| C4 | D-01 (local) | O-46 | Risk-reducing rule and projection semantics (TRC) |
| C4 | D-02 (local) | O-47 | Decision contract, wording, LIMIT_MATRIX rows (TRC) |
| C4 | D-03 (local) | O-48 | Cooling asymmetry (TRC) |
| C4 | A-01 (local) | recorded here only (no RAID row) | Gate C authorises PAPER only; live-capital criticals treated as Gate C blockers because LIVE shares the code path |
| C4 | R-07, O-22, O-07, O-08, O-19 (existing) | same IDs | Annotated in the remediation table; not renumbered |
| C4 | TC-KS-007 (proposed) | TC-KS-007 | Hook raises → activation recorded, S1 |
| C4 | TC-KS-008 (proposed: restart survival) | not implemented (R-23) | The delivered TC-KS-008 is the C2 cancel-scope case |
| C4 | TC-KS-009, TC-KS-010, TC-KS-011 (proposed) | not implemented (R-23, R-27) | Concurrent intent; PIR ref; liquidation registry |
| C4 | TC-RK-017 (proposed: account staleness) | TC-RK-018 | Stale account snapshot → HALTED |
| C4 | TC-RK-018 (proposed: tenant) | TC-RK-018 | Tenant mismatch |
| C4 | TC-RK-019 (proposed: split) | TC-RK-017 | Open orders projected into exposure |
| C4 | TC-RK-020 (proposed: reducing) | TC-RK-017 | Risk-reducing order passes |
| C4 | TC-RK-021 (proposed: negative NAV) | TC-RK-018 | NAV ≤ 0 |
| C4 | TC-RK-022 (proposed: pre-trade loss) | TC-RK-018 | Breached daily loss → REJECTED |
| C4 | TC-RK-023 (proposed: unsigned policy) | not implemented (R-29) | Unsigned/tampered policy → HALT |
| C4 | TC-AP-00x (proposed: re-decision) | TC-RK-019 | Approval re-decides on current snapshots |
| C4 | TC-ID-00x (proposed: limits) | TC-RK-020 | Limit change only via maker-checker |
| C4 | TC-OB-00x (proposed: heartbeat) | not implemented (R-26) | Monitor dead-man's switch |
| C4 | §7 RTM FR-11/11a/11b, FR-17/17a/17b, FR-12a, FR-01a/01b | RTM rows FR-11, FR-17 (Notes); TC-RK-019 (FR-12); R-28, R-29 | Proposed rows folded; FR-12 and FR-01 rows not edited this cycle |
| C5 | OBJ-1 | R-06, T-14 | Human authentication and MFA/PIM fully client-asserted |
| C5 | OBJ-2 | R-30, T-15 | Two-person rules bypassable by one human asserting a second actor id |
| C5 | OBJ-3 | R-31, T-16, D-024 | Audit not tamper-evident against tail truncation; caller timestamps |
| C5 | F-04 | O-51 | `/process` silently discards the queue |
| C5 | F-05 | R-34, T-22 | Stored XSS and log injection via `X-Actor-Id` |
| C5 | F-06 | R-35, T-25 | No CORS policy, no rate limiting, audit amplification |
| C5 | F-07 | O-51 | `/healthz` information leak |
| C5 | F-08 | R-22, T-17 | Tenant hard-coded; reads not tenant-scoped; no TC-TEN |
| C5 | F-09 | R-33, T-18 | `ActorKind` caller-declared |
| C5 | F-10 | R-33 (remediated), T-19 | Agent can disable a live jurisdiction flag |
| C5 | F-11 | R-18, T-20 | MCP egress nullified by policy union |
| C5 | F-12 | R-32, T-21 | Execution egress 0.0.0.0/0; edge reads execution; DNS |
| C5 | F-13 | O-50 | Secret scan false green and weak patterns |
| C5 | F-14 | O-23 | SBOM inaccurate and unsigned |
| C5 | F-15 | O-23 | CI missing SAST/DAST/SCA/signing |
| C5 | F-16 | O-23 | Dependencies unpinned |
| C5 | F-17 | O-23 | docker-compose plaintext password (now env-overridable; sim-only label) |
| C5 | F-18 | O-09, T-23, D-025 | Legal-hold scope mismatch; unauthorised release |
| C5 | F-19 | R-35, T-24 | Redaction gaps |
| C5 | T-14 (local) | T-14 | Header-asserted identity/role/MFA |
| C5 | T-15 (local) | T-14 (merged) | Fake PIM elevation + MFA in `require()` |
| C5 | T-16 (local) | T-15 | Two-person bypass via 2nd actor id |
| C5 | T-17 (local) | T-16 | Audit tail truncation / mutable store / caller ts |
| C5 | T-18 (local) | T-17 | Tenant reads not scoped |
| C5 | T-19 (local) | T-18 | Actor spoof |
| C5 | T-20 (local) | T-19 | Jurisdiction flag disabled by agent |
| C5 | T-21 (local) | T-20 | NetworkPolicy union |
| C5 | T-22 (local) | T-21 | Execution egress + DNS tunnel |
| C5 | T-23 (local) | T-22 | Stored XSS / log injection |
| C5 | T-24 (local) | T-23 | Legal-hold scope miss |
| C5 | T-25 (local) | T-24 | Redaction misses |
| C5 | T-26 (local) | T-25 | Intent-flood audit amplification |
| C5 | T-27 (local) | T-04 / T-10 (existing; O-23) | CI lacks SAST/DAST/SCA/signing — a control gap on existing threats, not a new threat |
| C5 | A-SEC-00 | O-43 | One author holds 1st + 3rd line; Board + IVA must ratify |
| C5 | R-SEC-01 | R-06 | Header-asserted auth + fake PIM/MFA |
| C5 | R-SEC-02 | R-30 | Two-person bypass |
| C5 | R-SEC-03 | R-31 | Audit truncation |
| C5 | R-SEC-04 | R-22 | Tenant reads unscoped |
| C5 | R-SEC-05 | R-18, R-32 | MCP egress union; execution egress |
| C5 | R-SEC-06 | O-23 | CI gates; SBOM |
| C5 | R-SEC-07 | R-33 | Jurisdiction flag; ActorKind spoof |
| C5 | R-SEC-08 | O-09 | Legal-hold fail-open |
| C5 | R-SEC-09 | R-34 | XSS / log injection |
| C5 | R-SEC-10 | R-35 | Redaction; DoS |
| C5 | I-SEC-11 | O-50 | Secret scan |
| C5 | I-SEC-12 | O-51 | `/process`; `/healthz` |
| C5 | D-SEC-13 | O-52 (H-10) | External pen-test and red team |
| C5 | TC-AUD-005, TC-AUD-006 (proposed) | TC-AUD-005 (both cases) | Truncation with sealed anchor; backdating refused |
| C5 | TC-ID-005, TC-ID-006 (proposed) | TC-E2E-AUTH (partial) | Forged non-human roles refused; non-sim start refused — fake PIM not covered |
| C5 | TC-ID-007, TC-ID-008, TC-AP-005 (proposed) | not implemented (R-30, R-33) | Second-id bypass; kind spoof |
| C5 | TC-TEN-001..004, TC-SEC-002/003, TC-SC-001/002, TC-NET-005/006, TC-PERF-004, TC-CP-007/008 (proposed) | not implemented (R-22, R-06, R-34, O-23, R-18, R-32, R-35, R-33, O-09) | Quartets that do not exist yet |
| C5 | TC-OB-005 (proposed: redaction) | not the delivered TC-OB-005 | The delivered TC-OB-005 covers alert auto-action integrity (R-17); redaction extension is untested (R-35) |
| C5 | §7 RTM NFR-SEC-03, NFR-SEC-04 (new) | R-06, R-30, R-18, R-32 | Proposed rows not added; tracked as risks |
| C5 | §7 RTM NFR-TEN-01, NFR-AUD-01, NFR-SEC-02, NFR-PRV-01 | RTM rows (Notes) | Existing rows annotated |
