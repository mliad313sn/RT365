# RED_TEAM_PLAN

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Red-Team & Pen-Test Lead | Security Architect | Security & Privacy Board | D | Draft v1.0 |

Scope [Source: 06, 11]: AI/MCP paths (injection, tool escalation, exfiltration, hallucinated symbols, audit deletion, unsafe tool selection), tenant escape, secrets leakage, replay, duplicate orders, supply chain, authorisation.
| Exercise | Objective | Success for red team = finding | Cadence |
|---|---|---|---|
| RT-01 Injection via news adapter | make agent submit intent outside envelope | any control bypass | before Gate D, F |
| RT-02 Tool escalation | reach broker or vault from MCP server | any route | before Gate D |
| RT-03 Tenant escape | read another tenant's positions; executed in dev/sim as TC-TEN-002/003 (agent → other account, cross-tenant mint, human A → B on every endpoint, forged X-Actor-Tenant, unbound principal, cross-tenant limit leak, cross-tenant kill switch and deactivation, other tenant's queued intent; 404 bodies identical for missing vs foreign objects). Open: run against the deployed BFF with an IdP session (after R-06) and add a multi-account tenant case | any leak | before Gate D |
| RT-04 Replay/duplicate | create two live orders from one intent | duplicate | before Gate C |
| RT-05 Audit tamper | alter or delete an audit event | success | before Gate C |
| RT-06 Supply chain | deploy unsigned image | success | before Gate B |
Reporting: severity, evidence, owner; retest before gate; external pen-test annually.
