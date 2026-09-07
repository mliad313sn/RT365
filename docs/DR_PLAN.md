# DR_PLAN

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Cloud Architect | SRE Lead | ARB, Executive Steering | E | Draft v1.0 |

Scope: regional cell loss, data-store corruption, vault loss, bus loss. RPO/RTO candidates [Open: O-18] set after drill baselines.
| Scenario | Strategy | Order of restoration | Evidence |
|---|---|---|---|
| Cell loss | active/standby cell; audit replicated; portfolio roll-up | 1 identity/vault 2 audit 3 control plane 4 execution (Supervised mode) 5 analytics | drill report |
| Audit store corruption | WORM replica + hash-chain verification | verify chain before reopening trading | verification log |
| Vault/KMS loss | HSM-backed key escrow per policy | rotate broker credentials post-restore | rotation log |
| Bus loss | replay from outbox tables | consumers idempotent | dedupe evidence |
Reopening trading after DR requires reconciliation against broker statements first [Source: 03] and two-person restore.
