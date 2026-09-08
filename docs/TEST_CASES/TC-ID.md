# TC-ID — Identity, privileged access, maker-checker, mode ladder

Control: Identity, privileged access, maker-checker, mode ladder — Requirement: FR-01 — RTM row: FR-01 — Owner: Backend Lead — Reviewer (≠ owner): Security Architect — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T08:44:59.790245+00:00 at `e437bd03c9484a51aeccbb27168703ca3ddabc59`

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-ID-001 | A limit change proposed by one person stays pending until a different person from another line checks it; cooling period applies. | pass | passed | `test/quartets/test_tc_id_identity.py::test_privileged_change_needs_second_approver_from_different_line` |
| negative | TC-ID-002 | RBAC denies missing permissions; MFA is required; privileged permissions need an active elevation window. | pass | passed | `test/quartets/test_tc_id_identity.py::test_rbac_mfa_and_pim` |
| abuse | TC-ID-003 | Agents cannot promote modes; promotion is one step with gate evidence; out-of-scope capabilities have no permission flag. | pass | passed | `test/quartets/test_tc_id_identity.py::test_agent_cannot_change_mode_or_skip_steps_and_out_of_scope_flags_absent` |
| abuse | TC-ID-005 | Agents cannot reject (or otherwise touch) controlled changes; a decided change cannot be re-decided (IVA-05). | pass | passed | `test/quartets/test_tc_id_identity.py::test_reject_requires_human_and_pending_change` |
| recovery | TC-ID-004 | Halted is reachable by an authorised role; leaving it needs two persons from different lines and never straight to autonomy. | pass | passed | `test/quartets/test_tc_id_identity.py::test_return_from_halted_requires_two_persons_different_lines` |

Quartet complete: yes. Records: 5.
