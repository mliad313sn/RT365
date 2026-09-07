# PERSONAS

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Director | Support & Training Lead | Product Council | A | Draft v1.0 |

| Persona [Source: 01] | Goal | Modes available (default) [Committee] | Key screens | Risks to design against |
|---|---|---|---|---|
| Retail investor | Understand and control exposure | Observe, Backtest, Paper; Supervised/autonomy only per jurisdiction policy [Open: O-01] | Dashboard, approval queue | Misreading PnL as promise; unclear rejection |
| Active trader | Fast supervised execution | Observe → Supervised | Orders, alerts | Fat-finger, over-trading |
| Professional trader | Bounded autonomy on approved strategies | All, per cell enablement | Strategy registry, exposure | Limit evasion via order splitting |
| Portfolio manager | Allocation across strategies/accounts | Observe → Bounded autonomous | Portfolio, attribution | Concentration, correlated risk |
| Risk officer | Set/enforce limits, halt | Halted control, limits | Limit matrix, breaches, Kill Switch | Latency of halt, unclear evidence |
| Compliance analyst | Eligibility, surveillance, retention | Read + policy flags | Compliance matrix, surveillance | Enabling a market without legal record |
| Operations analyst | Reconciliation, incidents | Read + break resolution | Breaks, incident centre | Silent breaks |
| Tenant administrator | Users, roles, brokers | Admin | Admin console | Privilege creep |
| Auditor | Evidence review | Read-only | Audit explorer | Tampered logs |
| Support engineer | Customer resolution | Read + runbooks | Incident centre, reason dictionary | Over-privileged support access |
