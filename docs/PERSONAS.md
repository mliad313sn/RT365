# PERSONAS

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Director | Support & Training Lead | Product Council (advisory); Product Owner decides | A | v1.1 — persona × mode policy decided 2026-09-08 (D-045) |

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

## Persona × mode policy [Committee; D-045, O-01]
Global floor for every persona and every jurisdiction: Observe, Backtest, Paper. Supervised and Bounded autonomous are OFF everywhere by default and are enabled only per six-dimension cell by dual key after Gate D (Supervised) and Gate E (Bounded, with a capital envelope). Customer type is never self-declared; the persona → `CustomerType` mapping is [Open: Q-01-1, counsel].

| Persona | Floor | Supervised | Bounded autonomous | First-cell hypothesis (D-043) |
|---|---|---|---|---|
| Professional trader | Observe/Backtest/Paper | after Gate D, per cell | after Gate E, per cell, capital envelope | H(D) Supervised, H(E) Bounded |
| Portfolio manager | Observe/Backtest/Paper | after Gate D, per cell | after Gate E, per cell, capital envelope | H(D) Supervised, H(E) Bounded |
| Active trader | Observe/Backtest/Paper | only if classified PROFESSIONAL | OFF | not in first cell |
| Retail investor | Observe/Backtest/Paper | OFF for the first cell | OFF in every hypothesis | not in first cell |
| Risk officer, Compliance analyst, Operations analyst, Auditor, Support engineer | no trading mode (control and read roles) | — | — | — |
| Tenant administrator | admin only; cannot change mode | — | — | — |
