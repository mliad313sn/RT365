# PRODUCT_CHARTER

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Director | Compliance Agent | Product Council, Executive Steering | A | Draft v1.0 |

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

## Measurable outcomes (Gate A) [Open: O-16 targets to be set by Product Council]
Paper-mode reconciliation completeness · deterministic decision rate 100% · zero critical findings at each gate · operator time-to-halt in drills.

## Supported instrument classes (subject to per-market enablement) [Source: 00]
Equities, ETFs, forex, futures, options, commodities, fixed income, crypto-assets and other legally supported instruments — through certified market-data and broker adapters only.
