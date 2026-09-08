# DR_PLAN

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Cloud Architect | SRE Lead | ARB, Executive Steering | E | Draft v1.1, 2026-09-08 — the O(n) start-up dependency of O-18 recorded (CAPACITY_MODEL §4a); SRE Lead review **pending**; not accepted |

Scope: regional cell loss, data-store corruption, vault loss, bus loss. RPO/RTO candidates [Open: O-18] set after drill baselines.

**Why O-18 cannot be answered yet [Committee] — added 2026-09-08 with CAPACITY_MODEL v0.2 §4a.** Two verifications are unconditional on process start and both are linear in history: the control store replays its uncompacted journal at open (ADR-018, O(journal), O-111) and the audit store verifies its whole chain at open, with the anchor chain re-verified on every read (ADR-020, O(events)+O(anchors), O-133). Both are correct fail-closed design and neither may be weakened for speed — recovery is *restore then verify*, and disabling the check is never the fix (O-134). Consequently: step 2 below ("verify chain before reopening trading") is an unmeasured O(n) operation on the recovery-time path; a standby cell inherits **both** verifications, not one; and no RPO/RTO candidate may be proposed until they are measured against a stated journal and chain length. **A drill on a fresh cell measures the best case and will be quoted as the general case**, so every drill record must state the history length it ran against. O-18 is blocked on O-111, O-133 and a drill — not merely on a human choosing a number [Open: O-18, O-111, O-133]. No RPO or RTO figure is stated or implied anywhere in this document [Source: 00].
| Scenario | Strategy | Order of restoration | Evidence |
|---|---|---|---|
| Cell loss | active/standby cell; audit replicated; portfolio roll-up | 1 identity/vault 2 audit 3 control plane 4 execution (Supervised mode) 5 analytics | drill report |
| Audit store corruption | WORM replica + hash-chain verification | verify chain before reopening trading | verification log |
| Vault/KMS loss | HSM-backed key escrow per policy | rotate broker credentials post-restore | rotation log |
| Bus loss | replay from outbox tables | consumers idempotent | dedupe evidence |
Reopening trading after DR requires reconciliation against broker statements first [Source: 03] and two-person restore.
