# COMPONENT_DIAGRAMS (C4 Level 3)

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Enterprise Architect | Backend Lead | ARB | B | Draft v1.0 |

## Risk Engine [Source: 05; Committee]
```mermaid
flowchart TB
  IN[Intent + account snapshot + market snapshot + policy version] --> V[Schema & staleness validator]
  V --> PRE[Pre-trade check chain fail-fast, all cheap checks evaluated]
  PRE --> DEC{Outcome}
  DEC -->|APPROVED| OUT[Decision record]
  DEC -->|REJECTED| OUT
  DEC -->|REQUIRES_HUMAN_APPROVAL| OUT
  DEC -->|HALTED| OUT
  MON[Runtime monitors: loss, drawdown, frequency, slippage, rejects, latency, connectivity, drift, breaks, venue] --> KS[Kill Switch service]
  KS --> V
  POL[(Policy store, maker-checker)] --> PRE
```
No I/O, randomness or model call inside the decision function; unavailability → HALTED.

## Execution Gateway [Source: 03; Committee]
```mermaid
flowchart LR
  CMD[Authorised order command] --> IDEM[Idempotency check: key = hash(intent_id, account, policy_version)]
  IDEM --> LEASE[Executor lease + fencing token per account]
  LEASE --> SUB[Broker submission with client-order-id derived from key]
  SUB --> ACK[Ack / reject / fill events → outbox]
  ACK --> AUD[(Audit)]
```

## MCP server sandbox [Source: 04]
Signed registry → allowlisted tools with scopes → short-lived identity → schema validation in/out → egress allowlist → quotas/timeouts/payload limits → tamper-evident logs → emergency revocation.
