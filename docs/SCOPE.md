# SCOPE

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Director | Legal Agent | Product Council | A | Draft v1.0 |

## In scope [Source: 00, 02]
Paper trading, human-approved execution, bounded autonomous execution across authorised instruments through certified adapters; the 17 functional groups in PRD.md.

## Out of scope without separate approval [Source: 01]
| Capability | Enforcement [Committee] |
|---|---|
| Custody | No custody permission exists in the permission model |
| Deposits/withdrawals | No money-movement API; broker handles funding |
| Market making | No quoting engine; two-sided resting order patterns rejected at strategy registration |
| Copy trading | No cross-account signal replication feature |
| Personalised financial advice | UI copy and AI outputs are analytics, never recommendations to a person |
| Unlicensed solicitation | GTM content reviewed by Compliance/Legal |
| Unsupported jurisdictions | Dual-key enablement; default off |
| Manipulation-capable strategies | Surveillance pattern library used as registration filter |

## Billing scope [Committee; D-046, O-02]
Meter from Gate D, invoice from Gate F. Per-tenant subscription tiered by seats/accounts, prices from the cost model [Open: O-13]; usage metered from the audit chain for cost attribution only; invoicing and tax through an external provider once a third-party tenant exists [Open: provider, tax, Q-B01..Q-B04]. Permanently excluded without a separate decision: performance fees, per-trade fees, commission sharing, broker rebates, client money, referral payments. Billing has no route to the control or execution planes and never gates a halt, a Kill Switch or a disclosure (NFR-BIL-01).

## Assumptions [Open]
O-11 decided as hypothesis (D-043; country fact Q-11-1); O-02 decided (D-046; prices, tax, provider open); O-05 model hosting.
