# SEQUENCE_DIAGRAMS

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Enterprise Architect / Trading Domain Lead | Chief Risk Agent | ARB | B | Draft v1.0 |

## S-01 Trade intent to fill (authoritative pipeline) [Source: 00]
```mermaid
sequenceDiagram
  participant MD as Market Data
  participant SA as Strategy Agent (MCP)
  participant Q as Intent queue
  participant CE as Compliance/Eligibility
  participant RE as Risk Engine
  participant AP as Approval
  participant EG as Execution Gateway
  participant BR as Broker
  participant RC as Reconciliation
  participant AU as Audit
  MD->>SA: snapshot (market ts, provenance)
  SA->>Q: submit_trade_intent (strict schema, expiry)
  Q->>CE: intent
  CE->>AU: eligibility decision
  CE->>RE: ELIGIBLE
  RE->>AU: decision record (policy v, reasons, values, thresholds)
  alt REQUIRES_HUMAN_APPROVAL
    RE->>AP: queue
    AP->>AU: approver ≠ maker
    AP->>EG: authorised order command
  else APPROVED (bounded autonomous)
    RE->>EG: authorised order command
  end
  EG->>EG: idempotency + fencing token
  EG->>BR: order (client-order-id)
  BR-->>EG: ack / fills
  EG->>AU: events
  BR-->>RC: statement
  RC->>AU: reconciled / break
```

## S-02 Kill Switch activation [Source: 05]
Operator or monitor → Kill Switch service → block new risk → cancel open orders → apply account emergency policy (CANCEL_ONLY default) → revoke agent tokens → evidence snapshot → notify → (later) two-person restore.

## S-03 Executor failover with in-flight order [Committee]
Standby acquires lease with new fencing token → any late submission with old token rejected by gateway → reconciliation confirms single broker order.
