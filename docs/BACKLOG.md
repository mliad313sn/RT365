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
