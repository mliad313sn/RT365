# CONTEXT_DIAGRAM (C4 Level 1)

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Enterprise Architect | Security Architect | ARB | B | Draft v1.0 |

```mermaid
C4Context
  title Global AI-MCP RoboTrader — System Context [Source: 03; Committee]
  Person(trader, "Trader / PM", "Supervised or bounded-autonomous user")
  Person(risk, "Risk / Compliance officer", "Limits, eligibility, halts")
  Person(ops, "Operations / Support", "Reconciliation, incidents")
  Person(auditor, "Auditor", "Read-only evidence")
  System(rt, "RoboTrader Platform", "Analytics, Control and Execution planes")
  System_Ext(broker, "Brokers / Exchanges", "Certified adapters; final external truth")
  System_Ext(data, "Market-data providers", "Licensed real-time and historical feeds")
  System_Ext(llm, "Model providers", "Governed models via MCP [Open: O-05]")
  System_Ext(reg, "Regulatory reporting endpoints", "Per jurisdiction")
  System_Ext(idp, "Identity provider / MFA", "")
  Rel(trader, rt, "Uses")
  Rel(risk, rt, "Sets policy, halts")
  Rel(ops, rt, "Resolves breaks, incidents")
  Rel(auditor, rt, "Reviews audit")
  Rel(rt, broker, "Authorised orders only via Execution Gateway")
  Rel(data, rt, "Ticks/bars with provenance")
  Rel(rt, llm, "Analytics-plane calls only")
  Rel(rt, reg, "Reports")
  Rel(idp, rt, "AuthN")
```
Boundary rule: only the Execution Gateway holds a route to brokers [Source: 00].
