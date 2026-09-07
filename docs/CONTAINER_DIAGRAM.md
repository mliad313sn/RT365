# CONTAINER_DIAGRAM (C4 Level 2)

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Enterprise Architect | Cloud Architect | ARB | B | Draft v1.0 |

Twenty bounded contexts [Source: 03] grouped into three planes [Committee].

```mermaid
flowchart LR
  subgraph Edge
    WEB[Web/BFF Next.js PWA] --> IDN[Identity]
    WEB --> TEN[Tenant]
  end
  subgraph Analytics plane
    MD[Market Data] --> IM[Instrument Master]
    MD --> STR[Strategy]
    STR --> AI[AI / MCP servers]
    STR --> BT[Backtest]
  end
  subgraph Control plane
    INT[(Trade-intent queue)] --> CMP[Compliance / Eligibility]
    CMP --> RSK[Risk Engine]
    RSK --> APR[Approval]
    RSK --> AUD[(Audit WORM)]
    CMP --> AUD
    APR --> AUD
  end
  subgraph Execution plane
    OMS[OMS] --> EXG[Execution Gateway]
    EXG --> BRK[Broker Adapters]
    BRK --> REC[Reconciliation]
    REC --> PTF[Portfolio]
    EXG --> AUD
  end
  NOTF[Notification] ; BILL[Billing] ; SUP[Support]
  STR -- submit_trade_intent --> INT
  APR -- authorised order command --> OMS
  BRK --- EXT[(Brokers)]
  KS[Kill Switch service] -. halts .-> RSK & OMS & AI
```
Network policy: Analytics plane has no route to Execution plane or brokers; AI/MCP has no route to vault [Source: 04].

Stack [Source: 03]: Next.js/TypeScript PWA; FastAPI or typed service framework [Open: O-04]; PostgreSQL; time-series store [Open: O-13]; object storage (evidence); Redis (controlled cache); Kafka-compatible bus + schema registry; containers, IaC, mesh where justified, vault/HSM/KMS, WAF, SIEM, tracing, feature flags.
