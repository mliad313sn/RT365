# TC-TEN — Tenant isolation

Control: Tenant isolation — Requirement: NFR-TEN-01 — RTM row: NFR-TEN-01 — Owner: Backend Lead — Reviewer (≠ owner): Security Architect — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T10:14:10.043066+00:00 at `9e78104537c718553b7d1275a5f6fc34696997e6` (tree dirty, tested tree `4e3e1c96a0b2`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-TEN-001 | Agents and humans of two tenants read, submit and approve their own data; every audit row is tenant-tagged and correlated. | pass | passed | `test/quartets/test_tc_ten_tenancy.py::test_two_tenants_act_only_on_their_own_data` |
| negative | TC-TEN-002 | A's agent on B's account -> SCOPE (audited); cross-tenant identity mint refused; human A on B -> refused; pipeline CP-TENANT then RK-AUTH-TENANT. | pass | passed | `test/quartets/test_tc_ten_tenancy.py::test_cross_tenant_access_is_denied_at_every_layer` |
| abuse | TC-TEN-003 | Every read returns only the principal's tenant; actions on the other tenant are 404 without existence leak; forged tenant header 403. | pass | passed | `test/quartets/test_tc_ten_tenancy.py::test_every_bff_read_is_scoped_and_every_cross_tenant_action_refused` |
| recovery | TC-TEN-004 | Revoking tenant A stops only A (B keeps working), survives a restart, and is lifted only by two distinct approvers; all audited. | pass | passed | `test/quartets/test_tc_ten_tenancy.py::test_tenant_wide_revocation_hits_one_tenant_survives_restart_and_needs_two_persons_to_lift` |

Quartet complete: yes. Records: 4.
