# PRIVACY_IMPACT

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Privacy Lead | Security Architect | Security & Privacy Board | D | Draft v1.0 |

Obligations [Source: 06]: purpose limitation, minimisation, consent where applicable, residency/transfer mapping, retention schedules, deletion workflows, subject rights, DPIA where required, privacy-safe telemetry.

| Data category | Purpose | Legal basis (per jurisdiction) | Residency | Retention | Deletion / legal hold [O-09] | Telemetry redaction |
|---|---|---|---|---|---|---|
| Identity & contact | account operation | [Open: O-10] | per tenant | regulatory record period | hold suppresses deletion; logged | redacted at emission |
| Trading records | execution, reporting, surveillance | regulatory duty | per tenant | per COMPLIANCE_MATRIX | hold by default | pseudonymised |
| Session/security logs | security | legitimate interest | per cell | security retention | — | IP/user redacted |
| AI context | analytics | contractual | per cell | short | none stored beyond audit refs | masked account state only |
DPIA status per launch jurisdiction: [Open: O-10].
