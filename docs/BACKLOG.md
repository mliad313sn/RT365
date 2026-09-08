# BACKLOG

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB | A | Draft v1.0 |

## Epics [Source: 14] with owners [Committee]
| Epic | Accountable | 2nd-line reviewer | First gate | Key features |
|---|---|---|---|---|
| E01 Foundation & identity | Backend Lead | Security Architect | B | Tenant model, MFA/passkeys, RBAC/ABAC, PIM, maker-checker primitive |
| E02 Market data & instrument master | Data Engineering Lead | Data Architect | C | Source contracts, provenance stamping, bitemporal store, instrument master, calendars |
| E03 Broker adapter framework | Broker-Connector Lead | Trading Domain Lead | C | Adapter contract, capability discovery, rotation, health, sandbox certification |
| E04 Portfolio & accounting | Backend Lead | Chief Risk Agent | C | Positions, cash, margin, PnL, attribution, EOD reconciliation |
| E05 Deterministic risk engine | Backend Lead | Chief Risk Agent | C | Pure decision function, limit hierarchy, runtime monitors, Kill Switch service |
| E06 Compliance & eligibility | Backend Lead | Compliance Agent | D | Eligibility engine, restricted lists, jurisdiction flags, retention/WORM |
| E07 OMS & execution gateway | Backend Lead | Trading Domain Lead | C | Intent state machine, outbox/inbox, executor lease, idempotent submission, fills |
| E08 Strategy & backtesting | Quant Research Lead | Model Risk Lead | C | Registry, pre-registration, single-code-path backtester, walk-forward, cards |
| E09 MCP/AI governance | Backend Lead | MCP Security Agent | D | Signed registry, tool servers, provenance labels, model lifecycle |
| E10 Dashboard & mobile | Frontend Lead | Accessibility Lead | C | Hierarchy, reason dictionary, approval queue, admin, PWA |
| E11 Audit, surveillance, reporting | Backend Lead | Compliance Agent | D | Immutable audit, correlation search, surveillance patterns, reporting adapters |
| E12 Observability & SRE | SRE Lead | ARB | C | Telemetry, SLIs, runbooks, safety semantics, probes |
| E13 Security & privacy | Security Architect | Security & Privacy Board | B | Vault, workload identity, SDLC gates, SBOM, DPIA workflows |
| E14 Billing, support, admin | Backend Lead | Finance / Support | F | Billing scope [Open: O-02], support console, training |
| E15 Regulatory & market launch | Compliance Agent | Legal Agent | F | Launch matrix, disclosures, dual-key enablement, post-launch review |

## Product Owner priority (2026-09-07, acting; docs/PRODUCT_OWNER.md) [Committee]
Ordered by gate dependency; a story is Ready only with the template fields and an RTM row (DEFINITION_OF_READY.md).
| # | Story / act | Epic | Blocks | Owner |
|---|---|---|---|---|
| P0 | Keep the build executable: `make all`, `rt365 check/probe --env sim`, `make package`, release workflow green on every push | E13 | everything | Backend Lead, SRE Lead |
| P1 | Human acts on the critical path to Gate A/B: H-01, H-02, H-03, H-22, H-23 | — | Gates A, B | Executive Steering, Committee chair |
| P2 | MCP Security Agent registration review of the six tools and the stdio transport (O-35; REVIEW_C3) | E09 | Gate D | MCP Security Agent |
| P3 | KMS/HSM key and WORM anchor (H-20, H-21; O-53, O-54) | E13, E11 | Gate C | Security Architect, SRE Lead |
| P4 | Durable stores for lease/outbox/inbox/decision index/nonce journal (R-05, O-55) | E07, E09 | Gate C (shadow) | Backend Lead |
| P5 | Trading Risk Committee numbers (H-09, O-07) and broker/data contracts (H-07, H-08) | E05, E03, E02 | Gate C | Trading Risk Committee, Finance |
| P6 | Accessibility evidence and PWA (NFR-A11Y-01, ADR-012, O-51) | E10 | Gate F | Frontend Lead, Accessibility Lead |
| P7 | E14 per D-046: metering from the audit chain (Gate D), NFR-BIL-01 boundary and quartet TC-BIL-001..004, services `tenant/notification/billing/support` (O-31); invoicing provider at Gate F | E14 | Gate D/F | Backend Lead, Enterprise Architect |
| P8 | E12 per D-044: `time_to_halt_s` SLI, block-rate assertion after `activated_at` (TC-KS-009), drill measurement path (O-64) — **delivered in dev/sim 2026-09-08**; drill and ceiling remain (H-19, Q-16-1) | E12 | Gate C | SRE Lead, QA Lead |
| P9 | E06/E01 per D-045: persona-role vs `enabled_feature` test (TC-ID-006), CustomerType × mode NOCELL test, disclosure/consent/classification fields on CustomerProfile (council P-3, P-4) | E06, E01 | Gate D | Backend Lead, Compliance Agent |

## Story template [Source: 14] + [Committee]
```
Story ID / Epic / FR link / RTM row
Business value:
Scope (in/out):
Assumptions:
API / event impact:
Security / privacy impact:
Observability (metrics, logs, traces, alerts):
Migration:
Rollback:
Control quartet reference (if control-bearing): positive / negative / abuse / recovery test IDs
Acceptance:
  Given ... When ... Then ...
Owner / Reviewer (different line) / Approver
```
