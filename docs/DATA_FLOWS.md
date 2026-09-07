# DATA_FLOWS

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Data Architect | Privacy Lead | ARB, Security & Privacy Board | B | Draft v1.0 |

| Flow | From → To | Data | Classification | Controls |
|---|---|---|---|---|
| DF-01 | Provider → Market Data | ticks/bars | Licensed, non-personal | Source contract, provenance stamp, freshness SLA, entitlement check |
| DF-02 | Market Data → Strategy/AI | normalised snapshots | Licensed | Masking of unlicensed fields, provenance labels |
| DF-03 | Portfolio → AI | account state | Confidential | Masked (no identifiers), read-only tool |
| DF-04 | AI → Intent queue | trade intent | Confidential | Strict schema, signed tool call |
| DF-05 | Control plane → Execution | authorised command | Confidential | Idempotency, fencing token |
| DF-06 | Execution ↔ Broker | orders, fills, statements | Confidential | Vault credentials, mTLS, no agent access |
| DF-07 | All → Audit | events | Regulated record | WORM, hash chain, retention schedule, legal hold |
| DF-08 | Users ↔ BFF | PII, sessions | Personal | MFA, residency per tenant, redaction in telemetry |
| DF-09 | Platform → Regulatory adapters | reports | Regulated | Per-jurisdiction, dual-key enabled |
Residency/transfer map per tenant maintained in PRIVACY_IMPACT.md [Source: 06].
