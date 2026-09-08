# MISSING_ACTIONS — human acts the kit cannot perform

| Owner | Reviewer | Status |
|---|---|---|
| Program Orchestrator | Independent Validation Agent | living register, reviewed weekly |

Rule: an action stays here until its evidence file exists. The orchestrator prepares everything around it; only a named human closes it. Since 2026-09-08 (D-039) the Product Owner is the deciding human for every row; the Owner column names who prepares or executes the act, and the decision is taken through docs/PO_DECISION_QUEUE.md. Acts that need an external party (counsel, regulator, broker, data vendor, a second person for two-person controls) still need that party.

| ID | Action | Category | Owner | Blocks gate | Prepared by prompt | Evidence when done | Due | Status |
|---|---|---|---|---|---|---|---|---|
| H-01 | Appoint people to the 27 committee roles (Gate A); name deputies for two-person controls by Gate C (O-19, O-63) | Governance | Product Owner | A (roles) / C (deputies) | goals/decisions/O-19 | RACI.md complete | | Open |
| H-02 | Ratify committee structure and decisions D-001..D-004 | Governance | Product Owner (agent under D-040) | A | GOAL.md | D-042 | 2026-09-08 | Closed |
| H-03 | Choose first jurisdiction cell | Strategy | Product Owner (agent under D-040); **owner to supply the operating entity's country (Q-11-1)** | A | O-11 pack; COUNCIL_2026-09-08_gate_A_* | D-043; JURISDICTION_MATRIX hypothesis row | 2026-09-08 | Hypothesis recorded; country fact open |
| H-04 | Engage external counsel; obtain legal opinion per cell — scope = the question lists of H-25 | Legal | Legal Agent | D | external/legal_regulatory_engagement; COUNCIL_2026-09-08_gate_A_compliance_legal | signed legal record | | Open |
| H-05 | Approve budget and cloud spend | Finance | Executive Steering | B | external/infrastructure_provisioning | budget approval | | Open |
| H-06 | Sign model-provider terms and DPA | Procurement | Finance + Privacy | B | external/model_provider_procurement | filed contract | | Open |
| H-07 | Sign broker agreements; obtain sandbox and production credentials into vault | Procurement | Finance + Broker-Connector | C | external/broker_onboarding | BROKER_CERTIFICATIONS/ | | Open |
| H-08 | Sign market-data licences | Procurement | Finance + Legal | C | external/data_licensing | licence register | | Open |
| H-09 | Fill numeric limits in LIMIT_MATRIX at all levels | Risk | Trading Risk Committee | C | O-07 pack | LIMIT_MATRIX v1 approved | | Open |
| H-10 | Contract external pen-test and red team | Procurement | Security Architect + Finance | D | external/pentest_redteam_procurement | reports | | Open |
| H-11 | Certify operators after training | Operations | Support & Training Lead | D | external/operator_readiness | assessment records | | Open |
| H-12 | Compliance & Legal sign-off per cell (legal record) | Compliance | C&L Committee | D | C6 session | COMPLIANCE_MATRIX row | | Open |
| H-13 | Approve capital envelope for bounded autonomy | Risk | Trading Risk Committee + Exec Steering | E | C4/P4 sessions | DECISION_LOG entry | | Open |
| H-14 | Approve SLO targets from baselines | SRE | Executive Steering | E | O-03 pack | SLO_SLA targets | | Open |
| H-15 | Approve liquidation policy | Risk | Trading Risk Committee | E | O-08 pack | RISK_POLICY annex | | Open |
| H-16 | Approve disclosures, terms and marketing copy | Legal/GTM | Legal Agent | F | E15 build | approved copy | | Open |
| H-17 | Activate technical jurisdiction flag (second person) | Compliance | named second approver | F | C6 session | jurisdiction.flag.changed event | | Open |
| H-18 | Launch decision | Governance | Executive Steering | F | gate_F | DECISION_LOG entry | | Open |
| H-19 | Perform DR, rollback and Kill Switch drills with named operators | Operations | SRE Lead | D/E/F | external/dr_and_halt_drills | drill logs | | Open |
| H-20 | Provision KMS/HSM-held asymmetric key for order-command authorisation and registry signing, with rotation (replaces dev/sim shared HMAC and dev registry key) | Security | Security Architect + Cloud Architect | C | O-22, O-53 packs; ADR-015 | key ceremony record; `verify_tool_registry.py --production` passes | | Open |
| H-21 | Provision a WORM/replica anchor store for the audit `ChainHead`, written by a principal separate from the audit service | Operations | SRE Lead + Internal Audit | C | O-54; ADR-004 | anchor store attestation; TC-AUD anchor test against the external store | | Open |
| H-22 | Receive GATE_A/B/C_2026-09-07, the re-validation report and GATE_A_2026-09-08; the Product Owner is the approver of record under D-040 (A decided D-048; B and C pending) | Governance | Committee chair | B | docs/GATE_REPORTS/ | DECISION_LOG entries with approver ≠ author | | Open |
| H-23 | Ratify the Product Owner appointment (acting from 2026-09-07), name the person and deputy of record | Governance | Product Owner | A | goals/00_product_owner.md; docs/PRODUCT_OWNER.md; D-035 | D-039 (owner declaration 2026-09-08); deputy remains under O-19 | 2026-09-08 | Closed (appointment and authority); deputy open |
| H-24 | Confirm the `release` workflow evidence (run 34167194283 built and smoke-tested `rt365.exe`, SHA-256 recorded in AUDIT_EVIDENCE_INDEX #28), download `rt365-windows-x64`, verify the checksum on a Windows machine, sign the row; decide artefact signing (O-23) | Operations | SRE Lead + Security Architect | B | .github/workflows/release.yml; docs/INSTALLATION.md | AUDIT_EVIDENCE_INDEX row with run URL and checksum | | Open |
| H-25 | Adopt the counsel question lists Q-J01..Q-J18, Q-P01..Q-P07, Q-B01..Q-B04, Q-T01..Q-T02 (COUNCIL_2026-09-08_gate_A_compliance_legal, _product_director) as the H-04 engagement scope; name the counsel of record | Legal | Legal Agent (human of record) | B (scope) / D (answers) | GATE_A_2026-09-08 GA-C5 | H-04 scope attached; counsel named | | Open |
| H-26 | Name the two dual-key humans (one Legal Agent, one Compliance role; never the Product Owner, a 1st-line member or an agent) | Compliance | Product Owner | D | GATE_A_2026-09-08 GA-C6; TC-CP-007 | names in RACI.md | | Open |
| H-27 | Owner-authored evidence of D-040: merge the branch's pull request (or an owner-authored commit or signed line in DECISION_LOG) | Governance | Product Owner (human) | B | GATE_A_2026-09-08 GA-C3 | commit/merge authored by the owner | | Open |
| H-28 | Stand up the Meridian instance for real: PostgreSQL, backup with a timed restore, second instance, security policy, demo accounts removed, group-level account for `make pmo-sync` | Operations | SRE Lead + Security Architect | C | docs/PMO.md; docs/PMO_MERIDIAN_ASSESSMENT.md §3 M-08 | instance runbook; restore drill log | | Open |
| H-29 | Verify the world registry (rtcore.world) against the current ISO 3166-1 and ISO 4217 registers and sign the row; repeat on each ISO change | Data | Data Architect (human of record) | B | docs/GLOBAL_COMPATIBILITY.md; libs/core/rtcore/world.py | signed verification record in AUDIT_EVIDENCE_INDEX | | Open |
| H-30 | Procure the code-signing certificate (Windows Authenticode) and developer identity (macOS); keys in the platform secret store | Security | Security Architect + Finance | C | COUNCIL_2026-09-08_gate_B_security_privacy §3.5; D-054 | signed release artefacts verified by the installers | | Open |
