# PRODUCT_CHARTER

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Director | Compliance Agent | Product Council (advisory); Product Owner decides | A | v1.1 — approved as the Gate A charter 2026-09-08 (D-042); outcome targets set (D-044) |

## Vision [Source: 01]
Deliver a modular trading operating system that converts governed AI insights into controlled execution across supported global markets.

## Product posture [Source: 00]
An autonomous, multi-asset platform may generate and execute orders only inside a deterministic, independently enforced control envelope. Profit is an objective, never a promise. Capital preservation, lawful operation, security, market integrity, traceability and human override have priority over model output.

## Personas [Source: 01]
Retail investor · Active trader · Professional trader · Portfolio manager · Risk officer · Compliance analyst · Operations analyst · Tenant administrator · Auditor · Support engineer. Detail in PERSONAS.md.

## Operating modes [Source: 01] and state machine [Committee]
| Mode | Meaning | Promotion requires |
|---|---|---|
| Observe | Analytics only | — |
| Backtest | Historical simulation | Data snapshot pinned, pre-registered hypothesis |
| Paper | Live data, virtual capital | Gate C |
| Supervised | Explicit approval per order/batch | Gate D |
| Bounded autonomous | Automatic execution inside approved limits | Gate E, per-cell enablement |
| Halted | New orders blocked; cancel/close per emergency policy | Reachable from any mode; exit needs two-person action |

## Out of scope without separate approval [Source: 01]
Custody, deposits/withdrawals, market making, copy trading, personalised financial advice, unlicensed solicitation, unsupported jurisdictions, manipulation-capable strategies. Enforced as absent permission flags [Committee].

## Measurable outcomes (Gate A) [Committee; D-044]
| Outcome | Target | Method / evidence ID | First measurable at |
|---|---|---|---|
| Reconciliation completeness | 100% of positions, cash and open orders reconciled-or-classified at EOD+1; residue = typed break + ticket + account to Supervised | TC-RC-001..005; reconciliation.completed / break events | paper (Gate C) |
| Deterministic decision rate | 100% byte-identical decisions across replicas for identical inputs | TC-RK-001..004; test/property; IVA determinism check | dev/sim (evidenced) |
| Gate findings | 0 open critical findings at each gate; highs resolved or risk-accepted in writing | GATE_REPORTS/; RAID | each gate |
| Time-to-halt | 100% of approvals blocked after `activated_at`; operator-action → engaged → last-cancel measured per drill; numeric ceiling [Open: Q-16-1] set at the first drill (O-64) | TC-KS-*; proposed TC-KS-009 and `time_to_halt_s` SLI (E12) | drill (H-19, Gate D) |
No outcome is denominated in PnL or return [Source: 00].

## Supported instrument classes (subject to per-market enablement) [Source: 00]
Equities, ETFs, forex, futures, options, commodities, fixed income, crypto-assets and other legally supported instruments — through certified market-data and broker adapters only.
