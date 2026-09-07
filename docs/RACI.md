# RACI

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | Executive Steering | A | Draft v1.0 |

Rule [Source: 13]: builder is never the sole approver; risk, compliance and security controls have independent accountable owners; emergency authority and deputies documented.

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
Deputies: [Open: O-19 to be named per role].
