# PROJECT_EXECUTION_PLAN — from empty repository to controlled GA

| Owner | Reviewer | Approving body | Status |
|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB | v1.1 |

This plan sequences every prompt in the kit so that no action needed for the final product is left unassigned. Each phase lists: prompts to run, human actions that cannot be delegated, exit evidence, and the gate that authorises the next environment. Loop inside a phase until exit evidence exists.

## Phase 0 — Bootstrap (week 0)
- Run `scripts/bootstrap_repo.sh` → repository structure [Source: 16], CODEOWNERS for protected paths, CI skeleton, docs copied.
- Load `GOAL.md` as orchestrator; register the committee (`docs/RACI.md`); name deputies (decision pack O-19).
- Appoint the Product Owner (`docs/PRODUCT_OWNER.md`; acting from 2026-09-07); generate the agent roster (`make agents`; `.claude/agents/`, `docs/AGENT_ROSTER.md`) and enable the only MCP server (`.mcp.json` → `rt365-sim`).
- Prove executability from a clean machine: `make install && make all`, `rt365 check --env sim`, `make package`, release workflow (`docs/INSTALLATION.md`).
- **Human:** appoint accountable people to the 27 roles; ratify D-001..D-004 and the Product Owner appointment (H-23) at Executive Steering.
- Exit: RACI complete; `docs/MISSING_ACTIONS.md` initialised.

## Phase 1 — Discovery → Gate A
- Committee sessions C1 (`goals/01`, challenge `goals/07`, validate `goals/28`).
- Decision packs O-01, O-02, O-11, O-16.
- External workflow: `goals/external/legal_regulatory_engagement.md` (start).
- **Human:** choose first jurisdiction cell; engage counsel; approve charter and outcomes.
- Exit: `goals/gate_A_discovery.md` passed.

## Phase 2 — Architecture & foundation → Gate B
- Committee sessions C2, C3, C5, C12 and process P1, P3.
- Decision packs O-04, O-05, O-13, O-17; ADR-001..008 accepted at ARB.
- Build: E01, E13 (`goals/build/E01`, `E13`); infra: `goals/external/infrastructure_provisioning.md`.
- External: `model_provider_procurement.md`, `pentest_redteam_procurement.md` (contract).
- **Human:** approve budget; sign provider terms; approve threat model at Security & Privacy Board.
- Exit: `gate_B_architecture.md` passed → development and simulation environments authorised.

## Phase 3 — Data & execution core → Gate C
- Committee sessions C4, C7, C9, C10 and process P6.
- Decision packs O-07, O-12, O-19.
- Build: E02, E03, E04, E05, E07, E08, E10, E12 (in that dependency order; E05 and E07 gated by 2nd-line CODEOWNERS).
- External: `broker_onboarding.md`, `data_licensing.md` to certification/contract.
- Assurance: TC-RK, TC-EX, TC-KS, TC-NET quartets; RT-04, RT-05; performance baselines.
- **Human:** sign broker and data contracts; Trading Risk Committee fills LIMIT_MATRIX numbers.
- Exit: `gate_C_paper_readiness.md` passed → shadow and paper environments authorised.

## Phase 4 — Governance & AI → Gate D
- Committee sessions C6, C8, C11 and process P2, P5.
- Decision packs O-06, O-09, O-10.
- Build: E06, E09, E11, E14 (billing scope from O-02).
- Assurance: independent backtest reproduction (`goals/28`), external pen-test and red team (RT-01..03, 06), rollback drill (`dr_and_halt_drills.md`), operator training (`operator_readiness.md`), UAT.
- **Human:** Compliance & Legal sign-off per cell (legal record); operators certified.
- Exit: `gate_D_supervised_pilot.md` passed → supervised pilot authorised.

## Phase 5 — Autonomy → Gate E
- Process P4 drills on real infrastructure; decision packs O-03 (targets from baselines), O-08, O-18.
- Capital envelope approved by Trading Risk Committee and Executive Steering; runtime halts evidenced in paper and pilot; incident command staffed.
- **Human:** approve capital envelope; sign off SLO targets.
- Exit: `gate_E_capped_autonomy.md` passed → capped autonomous pilot authorised.

## Phase 6 — Market release → Gate F
- Build E15; decision packs O-14, O-15; workflows `legal_regulatory_engagement.md` (complete), `operator_readiness.md`, `dr_and_halt_drills.md` (DR).
- Release dossier assembled from `docs/AUDIT_EVIDENCE_INDEX.md`; accessibility verified; disclosures and terms approved; dual-key flag activation.
- **Human:** second-person flag activation; Executive Steering launch decision.
- Exit: `gate_F_market_release.md` passed → controlled GA for that cell only. Repeat Phases 4–6 per additional market.

## Phase 7 — Operate & improve (continuous)
- Post-launch reviews at 30/90 days; champion/challenger reviews; quarterly Kill Switch and revocation drills; annual pen-test; RAID and RTM maintenance; this plan re-baselined after each gate.

## Standing loop every week (orchestrator)
1. Read `docs/MISSING_ACTIONS.md`; chase overdue human actions; escalate blockers to the owning board.
2. Report RTM gaps, quartet coverage, open criticals/highs, gate readiness, confidence/provenance.
3. Any new gap discovered → add to RAID with owner and gate, and to MISSING_ACTIONS if a human act is needed.
