# RACI

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | Executive Steering | A | Draft v1.1 — Product Owner rows added 2026-09-07 (appointment acting, H-23) |

Rule [Source: 13]: builder is never the sole approver; risk, compliance and security controls have independent accountable owners; emergency authority and deputies documented.

**Authority since 2026-09-08 (D-039, docs/PRODUCT_OWNER.md):** the "A" column below names the council that recommends; the human Product Owner decides every row and may convene any council. Kill Switch activation authority and the runtime two-person rules are unchanged (a second distinct human is still required).

| Control / decision | R | A | C | I |
|---|---|---|---|---|
| Risk limits and policy | Backend Lead (impl) | Chief Risk Agent / Trading Risk Committee | Trading Domain Lead, Compliance | IVA |
| Strategy/model approval | Quant Research Lead | Model Risk Committee | Chief Risk Agent | IVA |
| Jurisdiction enablement | Compliance Agent | Compliance & Legal Committee (dual key) | Product, Trading Domain | Exec Steering |
| MCP tool registration | Backend Lead | MCP Security Agent | Security Architect | Model Risk |
| Security/privacy acceptance | Security Architect | Security & Privacy Board | Privacy Lead, Red-Team | CAB |
| Production release | SRE Lead | CAB | all 2nd line | Exec Steering |
| Gate pass | Program Orchestrator | boards per gate; IVA veto | — | all |
| Kill Switch activation | SRE Lead / Chief Risk Agent / Compliance Agent / Trading Domain Lead / deputies (any one) | same | — | all |
| Kill Switch deactivation | two persons, different lines | Trading Risk Committee | Compliance | all |
| Backlog priority and story readiness | Program Orchestrator | **Product Owner** (acting, docs/PRODUCT_OWNER.md) | Product Director, epic leads | IVA |
| Epic acceptance against PRD and DoD | Epic accountable lead | Product Owner recommends → Product Council approves | 2nd-line reviewer of the epic | IVA |
| Agent and MCP roster (`.claude/agents/`, `.mcp.json`, AGENT_ROSTER.md) | Delivery Orchestrator (AI) | Product Owner | MCP Security Agent (any MCP server), Security Architect | all |
| Executability (install, check, serve, package, release) | Backend Lead, SRE Lead | Product Owner | Cloud Architect, Security Architect | CAB |
Deputies: [Open: O-19 to be named per role]. Product Owner: appointed 2026-09-07 (D-035), decision authority 2026-09-08 (D-039), all decisions delegated to the Product Owner agent (D-040); the Product Owner decides gates, limits and enablements after the councils recommend, but is never a hand in a runtime two-person control (Kill Switch deactivation, dual-key flag, maker-checker) — those need two other distinct humans (H-26, O-19).
