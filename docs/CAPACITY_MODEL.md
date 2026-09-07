# CAPACITY_MODEL (Gate B exit evidence)

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Enterprise Architect / Cloud Architect | SRE Lead | ARB | B | Skeleton v0.1 — numbers [Open: O-03, O-13, O-17] |

## What is fixed now [Committee]
| Dimension | Unit of scale | Partition key | Shed under load? |
|---|---|---|---|
| Analytics plane (market data, strategy, MCP servers, backtest) | per cell, autoscale on event lag | tenant / instrument | Yes — shed first [C2 §6] |
| Control plane (intent queue, eligibility, risk, approval, audit) | per cell, autoscale on risk-decision latency | tenant / account | Never — fails closed (HALTED) |
| Execution plane (OMS, gateway, adapters, reconciliation, portfolio) | one active executor per account (lease), standby per cell | account | Never — cancel-only on degradation |
| Audit WORM | append-only, replicated cross-cell | tenant | Never |

## Measurement plan (PERFORMANCE_PLAN.md)
| SLI (observability/slis.yaml) | Baseline to measure | Where |
|---|---|---|
| risk_decision_latency_ms_p99 | intent enqueue → decision write | `oms.pipeline` span |
| order_ack_latency_ms | command → broker ack | `execution_gateway` |
| event_lag_ms | produce → consume | bus (after ADR-005 deployment) |
| market_data_freshness_s | market_ts age at use | `risk_engine` RK-FRESH |

## Inputs that only humans can supply
Expected intents per second per cell, number of tenants/accounts at launch, instrument universe size, provider tick rates, cloud budget (MISSING_ACTIONS H-05). No number in this document is set; the ARB signs the model once baselines exist.
