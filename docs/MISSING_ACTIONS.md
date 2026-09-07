# MISSING_ACTIONS — human acts the kit cannot perform

| Owner | Reviewer | Status |
|---|---|---|
| Program Orchestrator | Independent Validation Agent | living register, reviewed weekly |

Rule: an action stays here until its evidence file exists. The orchestrator prepares everything around it; only a named human closes it.

| ID | Action | Category | Owner | Blocks gate | Prepared by prompt | Evidence when done | Due | Status |
|---|---|---|---|---|---|---|---|---|
| H-01 | Appoint people to the 27 committee roles and name deputies | Governance | Executive sponsor | A | goals/decisions/O-19 | RACI.md complete | | Open |
| H-02 | Ratify committee structure and decisions D-001..D-004 | Governance | Executive Steering | A | GOAL.md | DECISION_LOG entry | | Open |
| H-03 | Choose first jurisdiction cell | Strategy | Product Director + Compliance | A | O-11 pack | JURISDICTION_MATRIX row | | Open |
| H-04 | Engage external counsel; obtain legal opinion per cell | Legal | Legal Agent | D | external/legal_regulatory_engagement | signed legal record | | Open |
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
