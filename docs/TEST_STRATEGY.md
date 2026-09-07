# TEST_STRATEGY

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| QA Lead | Backend Lead | CAB | C | Draft v1.0 |

Families [Source: 11]: unit, property-based, contract, integration, e2e · historical replay, deterministic simulation, broker sandbox certification · load, spike, soak, latency, failover, capacity · chaos · security · model · compliance, accessibility, localisation, DR, operational readiness.

Principles [Source: 00; Committee]: control quartet (positive/negative/abuse/recovery) for every critical control; environment ladder tags (dev, sim, shadow, paper, pilot); evidence record with reviewer ≠ owner; backtest and production share one code path (ADR-008).

Evidence record [Source: 11]: requirement ID · environment · data version · expected · actual · evidence link · owner · reviewer.

Coverage report before each gate: % critical controls with full quartet; open defects by severity; determinism test status; broker certifications complete.
