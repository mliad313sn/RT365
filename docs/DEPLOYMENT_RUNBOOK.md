# DEPLOYMENT_RUNBOOK

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| SRE Lead | Backend Lead | CAB | C | Draft v1.0 |

1. Confirm CAB authorisation in DECISION_LOG.md and target environment ≤ gate-authorised ladder step.
2. Verify artefact signature and SBOM/SCA status; refuse unsigned.
3. Apply IaC change in the target cell; feature flags default off for new behaviour.
4. Deploy Control and Execution planes behind the executor lease (standby first, then lease transfer, then old active drained) — no in-flight order may be orphaned (TC-EX-004).
5. Run synthetic intent probe end to end; check trace completeness and alert delivery.
6. Enable flags progressively per tenant/account; observe SLIs for the soak window.
7. On any guardrail, integrity, reconciliation or observability failure → ROLLBACK_PLAN.md automatically [Source: 00].
8. Record evidence in AUDIT_EVIDENCE_INDEX.md.
