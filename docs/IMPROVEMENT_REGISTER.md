# IMPROVEMENT_REGISTER — everything still needed to reach a controlled market release

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Owner (delegate agent maintains) | Independent Validation Agent | Product Owner (D-040) | A–F | v1.0 — 2026-09-08; single ordered register of every open improvement, replacing nothing (RAID, MISSING_ACTIONS and BACKLOG stay the detailed ledgers and are referenced by ID) |

**Definition of complete.** The product is complete when Gate F has passed for one jurisdiction cell: every FR/NFR row of the RTM evidenced in the environment the gate authorises, every human act closed with its evidence file, no open critical, highs risk-accepted in writing, and a controlled GA for that one cell. Today (head of `claude/project-owner-agent-setup-hi3xqu`): **Gate A passed with conditions (D-048); dev/sim build complete and executable; Gates B–F not passed; no market, broker, strategy or autonomy enabled.**

Effort key: S = days · M = weeks · L = a release. "Who" names the accountable role; every build item has its epic and build prompt (goals/build/).

## A. Human-only acts (no agent can close these)
| # | Improvement | Why | Blocks | Who | Effort | Source |
|---|---|---|---|---|---|---|
| A-1 | Supply the operating entity's country (ISO 3166-1 alpha-2) so the first-cell hypothesis names a regulator pointer | GA-C1; every counsel question hangs on it | Gate B | Product Owner (human) | S | O-66, H-03 |
| A-2 | Merge this branch's pull request (or an owner-authored commit) as authorship evidence of D-039/D-040 | GA-C3 | Gate B | Product Owner (human) | S | H-27, O-62 |
| A-3 | Name the counsel of record and issue the engagement with the question lists as scope (Q-J, Q-P, Q-B, Q-T) | GA-C5 | Gate B (scope) / D (answers) | Legal Agent (human) | S | H-25, H-04 |
| A-4 | Name the two dual-key humans (one Legal, one Compliance) and the deputy for two-person runtime controls | GA-C6, GA-C8 | Gate C (deputy) / D (dual key) | Product Owner (human) | S | H-26, H-01, O-19, D-047 |
| A-5 | Appoint people to the remaining committee seats or record that the owner holds them until staffed | H-01 roles half | Gate B | Product Owner (human) | S | H-01, R-48 |
| A-6 | Approve budget and cloud spend; provision the cluster | infrastructure for shadow/paper | Gate B | Product Owner + Cloud Architect | M | H-05 |
| A-7 | Sign model-provider terms and DPA; choose providers (O-05) | AI provider needed for any non-fixture strategy | Gate B | Finance, Privacy Lead | M | H-06 |
| A-8 | Sign broker agreement(s); credentials into the vault; certify the real sandbox | V-C3 veto ground | Gate C | Finance + Broker-Connector Lead | M | H-07, O-26..O-28 |
| A-9 | Sign market-data licences; settle derived/redistribution rights | data for shadow/paper | Gate C | Finance + Legal | M | H-08, O-12 |
| A-10 | Fill numeric risk limits at every level (Trading Risk Committee decision) | V-C4 veto ground | Gate C | Product Owner with Trading Risk Committee chair | M | H-09, O-07, O-46..O-49 |
| A-11 | Provision KMS/HSM keys (registry signing, command authorisation) with rotation | replaces dev HMAC | Gate C | Security Architect + Cloud Architect | M | H-20, O-22, O-53 |
| A-12 | Provision the WORM/replica audit anchor store written by a separate principal | audit integrity beyond sim | Gate C | SRE Lead + Internal Audit | M | H-21, O-54 |
| A-13 | Contract external pen-test and red team; run RT-01..RT-06 | independent assurance | Gate D | Security Architect + Finance | M | H-10 |
| A-14 | Certify operators; run DR, rollback and Kill Switch drills on real infrastructure; set the time-to-halt ceiling from the drill | GA-C7, outcome targets | Gate D/E | SRE Lead, Support & Training Lead | M | H-11, H-19, Q-16-1, O-64 |
| A-15 | Compliance & Legal sign-off per cell (legal record), DPIA, disclosures and terms, second-person flag activation | market enablement | Gate D/F | Compliance & Legal chairs (humans), counsel | L | H-12, H-16, H-17, O-09, O-10 |
| A-16 | Approve capital envelope, liquidation policy, SLO targets from baselines | autonomy | Gate E | Product Owner with Trading Risk Committee chair | M | H-13, H-14, H-15, O-03, O-08 |
| A-17 | Launch decision for one cell; post-launch reviews at 30/90 days | GA | Gate F | Product Owner | S | H-18 |
| A-18 | Record the Windows executable evidence on a Windows machine; decide artefact signing | supply chain | Gate B | SRE Lead + Security Architect | S | H-24, O-23 |
| A-19 | Stand up Meridian for real: PostgreSQL, restore-tested backup, second instance, security policy, demo accounts removed | PMO instance | Gate C | SRE Lead + Security Architect | M | H-28, O-76 |
| A-20 | Convene the Committee to receive the 2026-09-07 gate reports, the re-validation and GATE_A_2026-09-08 | approver of record | Gate B | Product Owner | S | H-22 |

## B. Build gaps by epic (agents can build; 2nd-line review and gate evidence still required)
| # | Improvement | Epic / prompt | Gate | Who | Effort | Source |
|---|---|---|---|---|---|---|
| B-1 | Durable stores: lease, outbox/inbox, decision index, nonce journal, revocations, Kill Switch activation state (Postgres/Kafka adapters per ADR-010) | E07, E09, E05 (goals/build/E07, E09, E05) | C (shadow) | Backend Lead | L | R-05, O-55, R-23, O-33; **built in dev/sim 2026-09-08** (ADR-018, D-058, merge 880b2bc): seam + SQLite for lease, outbox/inbox, gateway indexes, Kill Switch activations; still open: Postgres/Kafka adapters, intent tracker and decision index, nonce/revocation journals on the seam, audit store (B-5) |
| B-2 | IdP/MFA/passkeys integration replacing dev header auth; PIM elevation with real sessions; CSP and output encoding on the BFF | E01, E10 | B/C | Backend Lead, Frontend Lead | M | R-06, R-30, R-34, O-51 |
| B-3 | Tenant isolation: multi-tenant allowlist store, scoped BFF reads, TC-TEN quartet, tenant-escape red-team case | E01, E09 | B | Backend Lead | M | R-22, RT-03 |
| B-4 | Asymmetric command authorisation and registry signing (Ed25519/KMS) with rotation; verify-only handles | E07, E09, E13 | C | Backend Lead, Security Architect | M | O-53, O-22, R-44 |
| B-5 | External audit-anchor publication and append-only interface; anchor test against the external store | E11 | C | Backend Lead, SRE Lead | M | R-31, O-54 |
| B-6 | Real broker adapters (FIX/REST) with capability discovery, rotation, health; certification rows to 14/14 | E03 | C | Broker-Connector Lead | L | H-07, O-26..O-28, V-C3 |
| B-7 | Licensed data adapters with entitlement at ingest; watchlists/charts/news (FR-04 partial) | E02, E10 | C | Data Engineering Lead, Frontend Lead | L | O-12, H-08 |
| B-8 | Margin models per asset class; attribution reports; durable ledger; reconciliation tolerances and fee model; reconciliation events on the bus | E04, E07 | C | Backend Lead | M | O-29, O-30 |
| B-9 | Risk: thresholds loaded from the approved LIMIT_MATRIX; remaining review partials R-26..R-29; liquidation policy hook once O-08 is decided | E05 | C/E | Backend Lead | M | R-26..R-29, O-46..O-49 |
| B-10 | Compliance: `legal_record_ref` verified (not a free string); disclosure-acknowledgement, mode-consent and classification-evidence fields on CustomerProfile; persona-role vs enabled_feature test (TC-ID-006); CustomerType × mode NOCELL test; surveillance wired at strategy registration; reporting adapters — **typed legal record, standing fields, TC-CP-008..012 and TC-ID-006 delivered 2026-09-08 (BUILD_E06; 188 tests); residual O-96..O-99, surveillance wiring and reporting adapters open** | E06, E01, E11 | D | Backend Lead, Compliance Agent | M | O-71, council P-2..P-4, BACKLOG P9 |
| B-11 | Strategy/backtest: walk-forward, Monte Carlo, scenario; independent reproduction protocol on separate infrastructure; model provider integration behind the prompt registry | E08, E09 | C/D | Quant Research Lead, Model Risk Lead | L | O-05, O-06, Gate D |
| B-12 | MCP: registration review of the six tools and the stdio transport (O-35), remaining review partials R-17, R-19, R-20; O-36..O-45; identity TTL and refresh for non-sim hosts | E09 | D | Backend Lead, MCP Security Agent | M | O-35..O-45, R-47 |
| B-13 | Dashboard: Next.js PWA and design system, admin console, accessibility evidence with assistive technology, incident centre, customer reporting | E10, E14 | C/F | Frontend Lead, Accessibility Lead | L | ADR-012, NFR-A11Y-01, O-51 |
| B-14 | Observability: telemetry export to a backend, SLO targets after baselines, on-call model, redaction assertions for id/IBAN/IP (TC-OB), drill measurement of operator-action → engaged | E12 | C/E | SRE Lead | M | O-03, O-15, O-18, R-35, O-64 |
| B-15 | Security: gating SAST/DAST/SCA, artefact and image signing, cluster network policies applied and tested, secrets in vault, agent-guard hardening (Bash bypass R-46) — **2026-09-08: lock regenerated from the declared closure, pip-audit runnable and clean (idna upgraded), bandit six Low; thresholds pending the Board packet** | E13 | B/C | Security Architect, Cloud Architect | M | O-23, R-46, O-58 |
| B-16 | Billing/support/admin: services tenant, notification, billing, support; NFR-BIL-01 boundary and quartet TC-BIL-001..004; metering from the audit chain (Gate D), invoicing provider (Gate F) | E14 | D/F | Backend Lead, Enterprise Architect | L | O-31, D-046 |
| B-17 | Market launch: launch matrix per cell, disclosures, dual-key ceremony runbook, post-launch review template filled | E15 | F | Compliance Agent, GTM Lead | M | H-16, H-17, O-14 |
| B-18 | Evidence provenance: evidence headers embed the tested commit, gate decisions cite the CI-evidenced commit, reviewer columns carry 2nd-line roles | QA (test/evidence_plugin.py), Program Orchestrator | B | QA Lead | S | O-65, O-67 |

## C. Governance, evidence and process
| # | Improvement | Why | Gate | Who | Effort | Source |
|---|---|---|---|---|---|---|
| C-1 | Re-validate by the IVA on the committed head: V-C1/V-C2 remediation, GA-C1..GA-C3, TC-CP-007 review by the Compliance Agent | verdicts stand until re-validated | B | Independent Validation Agent, Compliance Agent | S | O-56, R-49, AEI #31 |
| C-2 | Convene Gate B (ARB and Security & Privacy chairs) on dev/sim evidence; then Gate C after B-1, B-4, B-6, A-8, A-10 | next rung | B/C | gate-b, gate-c agents; Product Owner decides | S each | PO_DECISION_QUEUE §C |
| C-3 | Decide the remaining decision packs in queue order (O-04, O-05, O-13, O-17, O-22, O-23 for B; O-07, O-12, O-19 for C; …) with their councils | every pack is a Product Owner decision now | B–F | product-owner delegate + councils | S each | PO_DECISION_QUEUE §A |
| C-4 | Weekly loop: `make all`, `make pmo-sync`, run the weekly in Meridian, weekly report in docs/REPORTS | rhythm | continuous | Program Orchestrator | S/week | GOAL.md standing loop |
| C-5 | Global RAID IDs for the council's local findings; RACI reviewers on AEI rows; O-72 wording | ledger hygiene | B | Program Orchestrator | S | O-67, O-71 |

## D. Meridian IT-PMO improvements (proposed upstream; detail and rationale in docs/PMO_MERIDIAN_ASSESSMENT.md §5)
| # | Improvement | Effort |
|---|---|---|
| I-1 | Fix the first hour: load `.env` / default `PGLITE_DIR`, recursive data-dir creation, `dev` builds or proxies the client, refuse silent in-memory books — filed as https://github.com/mliad313sn/Meridian/issues/1 | S |
| I-2 | Write API v1 with external ids, idempotency keys, scoped integration keys and generated OpenAPI — filed as https://github.com/mliad313sn/Meridian/issues/2 | M |
| I-3 | Configurable gate ladder and phases per programme (Meridian's four gates as default template) — filed as https://github.com/mliad313sn/Meridian/issues/3 | M |
| I-4 | Evidence and traceability objects per gate criterion (type, link, hash, owner, reviewer); gate cannot pass unreviewed — filed as https://github.com/mliad313sn/Meridian/issues/4 | M |
| I-5 | Progress and cost from source systems (inbound events with provenance; EVM on measured progress) — filed as https://github.com/mliad313sn/Meridian/issues/5 | L |
| I-6 | Operate-for-real kit: pg_dump backup with restore drill, second instance, PostgreSQL required outside training, instance identity, fleet runbook — filed as https://github.com/mliad313sn/Meridian/issues/6 | M |
| I-7 | Decision register outside meetings (alternatives, dissent, links to change/gate/RAID) — filed as https://github.com/mliad313sn/Meridian/issues/7 | S |
| I-8 | RAID linked to gates and change requests; review dates drive agenda items — filed as https://github.com/mliad313sn/Meridian/issues/8 | S |
| I-9 | Release discipline: tags, changelog check, OpenAPI version = package version, signed installer — filed as https://github.com/mliad313sn/Meridian/issues/9 | S |
| I-10 | Stakeholders, skills in capacity, supplier performance, communication plan — filed as https://github.com/mliad313sn/Meridian/issues/10 | M–L |
| I-11 | English translation of the committee record — filed as https://github.com/mliad313sn/Meridian/issues/11 | S |
| I-12 | Day-one security posture: no demo accounts in production, security-policy template, break-glass shown in UI — filed as https://github.com/mliad313sn/Meridian/issues/12 | S |

## F. Global compatibility (owner requirement 2026-09-08; docs/GLOBAL_COMPATIBILITY.md; D-050)
| # | Improvement | Gate | Who | Effort | Status |
|---|---|---|---|---|---|
| F-1 | World registry verified against ISO 3166/4217 registers and signed (H-29) | B | Data Architect (human) | S | open |
| F-2 | Subdivision codes (ISO 3166-2) for federal regimes where rules differ by state/province | D | Data Engineering Lead | S | open |
| F-3 | FX rates as a deterministic decision input (fail closed when missing/stale); cross-currency NAV, limits and cash ledger | C | Backend Lead | M | open |
| F-4 | Licensed holiday calendars per venue; DST-aware freshness budgets | C | Data Engineering Lead | M | open |
| F-5 | Venue registry (MIC), tick tables and settlement conventions per market | C | Trading Domain Lead, Data Engineering Lead | M | open |
| F-6 | Locale packs (dashboard, reason dictionary, disclosures), CLDR formatting, RTL layout, accessibility per script (launch locales O-14) | F | Frontend Lead, Support & Training Lead | M | open |
| F-7 | Regional cells with residency enforcement at storage; retention schedules per jurisdiction (O-09, O-10) | D | Cloud Architect, Privacy Lead | L | open |
| F-8 | Sanctions and restricted-list feeds screened per cell | D | Compliance Agent, Data Engineering Lead | M | open |
| F-9 | Regulatory and tax reporting adapters per regime (E11) | D/F | Backend Lead | L | open |
| F-10 | Follow-the-sun on-call and support hours per market (O-15) | F | SRE Lead, Support & Training Lead | M | open |
| — | Built 2026-09-08: world registry (250 rows, 7 continents), country validation with simulated cells, timezone-aware venue calendars, TC-GLO-001..004 | B | Backend Lead | — | done in dev/sim |

## Execution (D-051)
Sections B, C, D, E and F are delegated to the Product Owner agent and its counsellors. Execution order: Gate B items first (B-2, B-3, B-15, B-18, C-1, C-2, C-5, F-1), then Gate C (B-1, B-4, B-5, B-6, B-7, B-8, B-9, F-3, F-4, F-5), then D and F. Each build item runs through its build agent with the control quartet first, a session packet `docs/SESSIONS/BUILD_<epic>_<date>.md`, `make all` green, and the 2nd-line reviewer named; section D items were filed upstream on 2026-09-08 as mliad313sn/Meridian issues #1–#12. Progress is reported in the weekly report and mirrored in Meridian by `make pmo-sync`.

## E. Delivery-kit and agent tooling
| # | Improvement | Why | Who | Effort | Source |
|---|---|---|---|---|---|
| E-1 | Agent write-scope guard enforced beyond Edit/Write (Bash-path writes) or replaced by branch-level checks in CI (path ownership per author) | R-46 | Product Owner, MCP Security Agent | M | R-46, O-58 |
| E-2 | Verify that the harness honours `hooks:` in agent frontmatter; otherwise move the guard to project settings — **closed 2026-09-08: frontmatter hooks are advisory; the project-level hook enforces the roster using the `agent_type` the harness passes** | O-58 | Product Owner | S | O-58 |
| E-3 | Council convening automation: one command that runs the member agents, the challenger and the IVA for a queue item and fills the recommendation | speed of the decision loop | product-owner delegate | M | PO_DECISION_QUEUE |
| E-4 | Two-way Meridian link once I-2 exists: decisions and actions recorded in the room flow back into the ledgers | ledger/PMO drift | Program Orchestrator | M | ADR-017 |
| E-5 | Windows/macOS executables signed; installer verifies signature, not only SHA-256 | O-23 | Security Architect | S after A-18 | O-23 |

## Status at a glance (2026-09-08, head of the branch)
| Area | Complete | Open |
|---|---|---|
| Governance kit (roles, agents, councils, approvers, counsel, queue, PMO) | yes — 67 agents, decision authority D-039/D-040, Gate A passed with conditions | ratification evidence A-2; deputies A-4; seats A-5 |
| Dev/sim control envelope | yes — 167 tests, 17/17 quartets, executable and packaged (wheel, Linux/macOS/Windows binaries) | durable stores B-1; real adapters B-6/B-7; keys B-4 |
| Human decisions | Gate A set decided (D-041..D-048) | 22 decision packs and 26 human acts in docs/PO_DECISION_QUEUE.md |
| Market readiness | none — no jurisdiction, broker, licence, limits or autonomy | A-1..A-17, B-*, C-* |
