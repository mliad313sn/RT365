# TEST_CASES — index and control-quartet template
ID scheme: TC-<area>-<nnn>: ID identity · BR broker · MD market data · AI MCP/AI · RK risk · AP approval · EX execution · RC reconciliation · CP compliance · KS kill switch · NET network policy · OB observability · SEC secrets · SC supply chain · TEN tenancy · AUD audit · PERF performance · A11Y accessibility · DR disaster recovery · PKG distribution (CLI, installer, executable) · AGT agent roster and write-scope guard · GLO global compatibility · DUR durable control state across restarts.

## Quartet template (one file per critical control)
```
Control: <name> — Requirement: <FR/NFR> — RTM row: <id> — Owner: — Reviewer (≠ owner):
Environment tag: dev | sim | shadow | paper | pilot   Data version:
Positive  TC-XX-nn1: Given … When … Then … | expected | actual | evidence
Negative  TC-XX-nn2: …
Abuse     TC-XX-nn3: …
Recovery  TC-XX-nn4: …
```
## Seed quartets
- TC-RK-001..004 Determinism: identical inputs → identical decision across replicas; changed policy_version → new decision; tampered intent hash → REJECTED; engine restart → same decision.
- TC-EX-001..004 Duplicate delivery: one order; replayed command → dedupe; stale fencing token → rejected; failover with in-flight order → single broker order confirmed by reconciliation.
- TC-KS-001..004 Kill Switch: activation blocks new risk and cancels open orders; agent attempts to deactivate → denied; single-person deactivate → pending; two-person deactivate → restored with audit.
- TC-AI-001..004 MCP: allowlisted tool works; injected instruction ignored; non-allowlisted tool call → denied+alert; revoked tool mid-session → denied.
- TC-NET-001..004 Planes: Analytics→Control via queue OK; Analytics→Execution → deny; MCP→vault → deny; policy restore after change.
- TC-CP-001..004 Eligibility/dual-key: eligible passes; ineligible reason code; legal record without flag → blocked; flag without record → blocked.
