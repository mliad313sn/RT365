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

## Assumptions [Open]
O-11 first jurisdiction; O-02 pricing; O-05 model hosting.
