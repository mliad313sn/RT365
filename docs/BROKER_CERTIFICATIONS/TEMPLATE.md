# Broker Certification — <broker> / <venue set>  [Source: 02, 11, 17]
Owner: Broker-Connector Lead · Reviewer: Trading Domain Lead · Gate C
| Check | Test ID | Result | Evidence |
|---|---|---|---|
| Authentication via vault; credential rotation | TC-BR-001 | | |
| Capability discovery (order types, TIF, asset classes) | TC-BR-002 | | |
| Each supported order type submit/ack | TC-BR-003 | | |
| Partial fill handling | | | |
| Cancel / replace | | | |
| Reject handling and reason mapping | | | |
| Reconnection and idempotent resubmission | TC-BR-004 | | |
| Statement download and reconciliation match | | | |
| Instrument identifiers, sessions/holidays, tick/lot, settlement, short-sale, margin, fees, corporate actions [Source: 17] | | | |
| Incident contacts and support hours | | | |
Unsupported order types must be rejected at schema validation (FR-02).
