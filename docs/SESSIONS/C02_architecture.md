# Session C2 — System Architecture (blueprint 03)

**Environment:** dev/sim only. The composition root wires every bounded context in one process with in-memory stores; no broker, market, strategy or autonomy is enabled. Documented by the Program Orchestrator (1st line, recommends, never approves).

## 1 Roles

| Function | Role (line) | Basis |
|---|---|---|
| Accountable | Enterprise Architect (Architecture tier, 1st line) — chairs ARB | COMMITTEE_DEEP_DIVE §C2 |
| Consulted | Data, Cloud, Integration and Security Architects; Backend Lead; SRE Lead | COMMITTEE_DEEP_DIVE §C2 |
| Builder | Backend Lead (1st line) — `libs/core/rtcore/*`, `services/execution/*`, `services/oms/*`, `apps/web/web_bff/platform.py`; Cloud Architect — `infra/kubernetes/**` | RACI |
| Challenger (different line) | MCP Security Agent (2nd line) — challenged the plane topology and the in-process guard as a substitute for network policy | Protocol §1.4 rule 4 |
| Assurance / IVA | ARB (standards) and Independent Validation Agent (evidence, veto at Gate B/C) | COMMITTEE_DEEP_DIVE §C2 |

Statement: author != reviewer != approver. Backend Lead and Cloud Architect authored code; MCP Security Agent challenged; IVA reviews; ARB approves ADRs. Nothing here is self-certified.

## 2 Purpose

- [Source: 03] Twenty bounded contexts; reference stack (Next.js/TypeScript PWA, FastAPI or typed framework, PostgreSQL, time-series store, Redis, Kafka-compatible bus, schema registry, vault/HSM/KMS); core guarantees: idempotency, monotonic state, outbox/inbox, correlation IDs, clock sync, stale-data detection, exactly-once business effect, broker as final truth.
- [Source: 00] Analytics plane -> Control plane -> Execution plane; no direct analytics-to-execution route; only the deterministic Execution Gateway submits orders.
- [Committee] Three planes enforced by Kubernetes namespaces and network policies (`infra/kubernetes/namespaces.yaml`, `network-policies/*.yaml`) and mirrored in-process by `rtcore.planes.PlaneGuard` so tests can prove denial; single active executor per account via `LeaseStore` with a monotonic fencing token; idempotency key = SHA-256(intent_id | account | policy_version) (`rtcore/schemas/order.py:idempotency_key`).
- [Open: O-03] freshness/latency thresholds; [Open: O-04] service framework (build uses FastAPI, see ADR-009); [Open: O-13] time-series store (ADR-004 deferred; `BitemporalStore` is in-memory).

## 3 Decisions and ADRs

| # | Decision | Alternatives compared | Why chosen | Evidence |
|---|---|---|---|---|
| C2-D1 | Three-plane topology as namespaces + default-deny network policies; static invariant checker `scripts/check_network_policies.py` fails CI if analytics gains an execution, vault or ipBlock egress. | ADR-001: (a) convention only; (b) single plane + RBAC; (c) chosen: planes + policy. | Topology is testable and drift is caught by TC-NET-004 (mutate policy -> checker exits 1 -> restore). | ADR-001; TC-NET-001..004 |
| C2-D2 | In-process `PlaneGuard` with `ALLOWED_ROUTES` and `contextvars` attribution; unattributed callers are treated as Analytics (fail closed). | (a) Trust in-process calls (single binary, no guard); (b) a decorator per service entry point; (c) chosen: context-scoped guard checked at `IntentQueue.submit` and `ExecutionGateway.submit`. | (a) lets a dev/sim wiring mistake reach the gateway silently; (b) is equivalent but scatters the rule. The guard is defence in depth, not a substitute for network policy (R-07). | **Proposed ADR-013** [Committee]; TC-NET-002, `test_gateway_denies_calls_from_analytics_plane` |
| C2-D3 | Executor lease with fencing token: `LeaseStore.acquire/preempt/is_valid`; gateway rejects stale tokens on submit, retry and cancel and raises an S1 alert. | ADR-002: (a) leader election without fencing; (b) broker-side dedupe only; (c) chosen. | Closes T-09 during failover; TC-EX-004 proves one broker order after failover. | ADR-002; TC-EX-003, TC-EX-004 |
| C2-D4 | Idempotency key and client order id derived from it (`RT` + 24 hex); inbox dedupe in `ExecutionGateway._by_key` and `TradePipeline.process` (`Inbox.process_once` keyed by `intent:<intent_hash>`). | ADR-003: (a) random UUID per attempt; (b) broker IDs; (c) chosen. | At-least-once delivery yields one business effect (NFR-CON-01). | ADR-003; TC-EX-002 |
| C2-D5 | Monotonic state machines from one generic `MonotonicStateMachine` (`rtcore/statemachine.py`) used by orders, intents and strategies; terminal states cannot transition. | (a) Ad-hoc `if` checks per service; (b) chosen: one table-driven machine with `assert_transition`. | One implementation, one test surface (TC-EX-005). | NFR-CON-02; TC-EX-005 |
| C2-D6 | Dev/sim composition root `build_sim_platform` with in-memory stores (`AuditStore`, `LeaseStore`, `Outbox/Inbox`, `BitemporalStore`, registries); `infra/docker-compose.yml` names Postgres and Redpanda as the replacement targets before Gate C. | (a) Build against Postgres/Kafka from day one; (b) mocks per test; (c) chosen: real code paths, in-memory stores behind small interfaces. | (a) blocks the control-envelope tests on infrastructure that needs human provisioning (MISSING_ACTIONS H-05); (b) would not exercise the production code path (ADR-008). | **Proposed ADR-010** [Committee] (already cited in `platform.py:1`, `lease.py:24`, `store.py:71`) |
| C2-D7 | FastAPI BFF (`apps/web/web_bff/app.py`) implementing `contracts/api/API_OPENAPI.yaml`; contract tests keep pydantic models and OpenAPI aligned. | (a) FastAPI; (b) another typed framework (e.g. Litestar / gRPC-first); (c) no BFF, direct service APIs. | Chosen for the dev/sim build only because pydantic models are already the schema source; O-04 remains open and the ARB decides at Gate B. | **Proposed ADR-009** [Committee, pending O-04]; `test/contract/test_openapi_alignment.py` |
| C2-D8 | Static HTML console served by the BFF (`apps/web/static/index.html`, "(simulation)"), pending the Next.js/TypeScript PWA of the reference stack. | (a) Ship the PWA now; (b) no UI until Gate C; (c) chosen: minimal static console for operators and journeys. | Front-end lead capacity and a11y verification (NFR-A11Y-01) are Gate F items; the console exists only to exercise journeys J-03/J-05/J-06. | **Proposed ADR-012** [Committee]; `test/e2e/test_journeys_and_bff.py` |

Standing ADRs referenced: ADR-001, 002, 003, 005 (outbox/inbox, event envelope `rtcore/envelope.py`), 006 (mesh: not in this build), 007 (cells: `infra/iac/README.md`), 008.

## 4 RTM rows

| Requirement | Architecture element | Implementation owner | Control | Test IDs | Evidence path | Gate |
|---|---|---|---|---|---|---|
| NFR-SEC-01 | Namespaces + network policies; `PlaneGuard`; `mcp-servers.yaml` egress | Cloud Architect / Backend Lead | Default deny; analytics -> control via intent-queue only; no analytics -> execution/vault | TC-NET-001..004, TC-AI-005 | `infra/kubernetes/**`, `scripts/check_network_policies.py`, `test/quartets/test_tc_net_planes.py` | B |
| FR-13 | `ExecutionGateway`, `LeaseStore` | Backend Lead | Fencing token, inbox dedupe, retry with same client_order_id | TC-EX-001..004, TC-EX-006 | `test/quartets/test_tc_ex_execution.py` | C |
| NFR-CON-01 | `idempotency_key`, `Inbox.process_once`, `Outbox.replay` | Integration Architect / Backend Lead | Exactly-once business effect | TC-EX-002 | same | C |
| NFR-CON-02 | `MonotonicStateMachine`, `ORDER_MACHINE`, `INTENT_MACHINE` | Backend Lead | Illegal/terminal transitions raise | TC-EX-005 | `libs/core/rtcore/statemachine.py` | C |
| NFR-RES-01 | Lease preempt on failover; cells (ADR-007) | Cloud Architect | Failover with in-flight order -> single broker order | TC-EX-004 | `services/execution/execution_gateway/lease.py` | C (cells: E) |
| NFR-AUD-01 / NFR-OBS-01 | `EventEnvelope` (correlation_id, payload_hash) | Integration Architect | Every event carries correlation ID and hash | TC-AUD-001, TC-OB-001 | `libs/core/rtcore/envelope.py` | C |
| NFR-SCL-01 / NFR-AVL-01 | `IntentQueue.max_depth` backpressure (analytics shed first) | Backend Lead | Queue at capacity -> intent REJECTED with reason BACKPRESSURE | GAP (no test) | `services/oms/oms/intent_queue.py` | E [Open: O-03] |

## 5 Threat-model delta

| Threat | Boundary | Control | Test | Owner |
|---|---|---|---|---|
| T-02 Excessive agency | B3 | Analytics reaches Control only via `intent_queue` channel; `PlaneGuard` and network policy | TC-NET-001/002, TC-AI-005 | MCP Security Agent |
| T-08 Replay | B3/B4 | Idempotency key dedupe; `IntentQueue` rejects expired/future-dated intents | TC-EX-002, TC-AI-002 | Integration Architect |
| T-09 Duplicate orders / race | B4/B5 | Fencing token on submit/retry/cancel; `execution.stale_fencing_token` S1 alert | TC-EX-003, TC-EX-004 | Integration Architect |
| T-05 Credential theft | B5 | Vault ingress only from control and execution namespaces (`security.yaml`) | TC-NET-003 | Security Architect |
| NEW T-16 Broker egress over-broad (`execution.yaml` ipBlock `0.0.0.0/0:443` minus RFC1918) | B5 | Comment says "allowlisted per adapter [Committee]" but the policy is not yet narrowed | GAP (O-25) | Security Architect, Cloud Architect |
| NEW T-17 In-process guard bypass by omitting `enter(plane)` | B3 | Unattributed callers default to ANALYTICS (fail closed) | TC-NET-002 second assertion | Backend Lead |

## 6 Control quartet per critical control

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Plane topology | TC-NET-001 `test_analytics_to_control_via_intent_queue_allowed` | TC-NET-002 `test_analytics_to_execution_denied_with_alert` | TC-NET-003 `test_mcp_to_vault_and_broker_denied` | TC-NET-004 `test_policy_change_detected_and_restore` |
| Executor lease + fencing | TC-EX-001 `test_one_authorised_command_one_broker_order` | TC-EX-002 `test_replayed_command_deduplicated` | TC-EX-003 `test_stale_fencing_token_rejected` | TC-EX-004 `test_failover_with_in_flight_order_single_broker_order` |
| Idempotency / inbox | TC-EX-001 | TC-EX-002 (three redeliveries, one broker order) | TC-EX-003 (new key with stale token still rejected) | TC-EX-004 (retry with same client_order_id, broker dedupe) |
| Monotonic state | TC-EX-005 `test_order_states_are_monotonic` | TC-EX-005 (FILLED -> ACKNOWLEDGED raises) | TC-EX-005 (unknown fill alerts, no mutation) | GAP — no test that a partially applied transition is rolled back on store failure |
| Backpressure (analytics shed first) | GAP | GAP | GAP | GAP — `max_depth` exists but untested; tie to O-03 |

## 7 Evidence list

- `docs/CONTEXT_DIAGRAM.md`, `docs/CONTAINER_DIAGRAM.md`, `docs/COMPONENT_DIAGRAMS.md`, `docs/SEQUENCE_DIAGRAMS.md`, `docs/DATA_FLOWS.md`, `docs/EVENT_CATALOG.md`, `docs/ADRs/ADR-001..008.md`
- `libs/core/rtcore/{planes.py,statemachine.py,envelope.py,ids.py}`; `services/execution/execution_gateway/{lease.py,gateway.py}`; `services/oms/oms/{outbox.py,lifecycle.py,intent_queue.py,pipeline.py}`; `apps/web/web_bff/platform.py`
- `infra/kubernetes/namespaces.yaml`, `infra/kubernetes/network-policies/{analytics,control,execution,mcp-servers,security}.yaml`, `infra/iac/README.md`, `infra/docker-compose.yml`, `scripts/check_network_policies.py`
- `test/quartets/test_tc_net_planes.py`, `test/quartets/test_tc_ex_execution.py`, `test/contract/test_openapi_alignment.py`, `test/evidence/evidence_index.json`

## 8 RAID entries, assumptions, confidence, provenance

| ID | Type | Item | Owner | Gate |
|---|---|---|---|---|
| O-24 | Dependency | `LeaseStore` needs a strongly consistent backing store (CP store or Postgres advisory locks) before any environment with two executors; docker-compose names Postgres but no adapter exists | Cloud Architect, Backend Lead | C |
| O-25 | Gap | Execution-plane broker egress is `0.0.0.0/0:443` minus private ranges; must become per-adapter allowlist through the egress gateway (T-16) | Security Architect, Cloud Architect | B |
| O-26 | Decision | ADR-009 (FastAPI) and ADR-012 (static console) are provisional; ARB decides O-04 and the PWA plan at Gate B | Enterprise Architect (ARB) | B |
| R-07 | Risk | Teams may treat `PlaneGuard` passing tests as proof of network isolation; only `check_network_policies.py` plus a cluster-level e2e test (not yet written) proves the deployed topology | Cloud Architect | B |

Assumptions: single process, single executor by default (`executor_id="executor-a"`); a second executor is simulated with `LeaseStore.preempt`; no service mesh (ADR-006) or cells (ADR-007) exist in the build.

Confidence: **high** that the in-process controls behave as tested; **medium** for the Kubernetes policies (static invariants only, never applied to a cluster); **low** for scalability/backpressure claims (untested, O-03).

Provenance: [Source: 00, 03] for planes, guarantees and stack; [Committee] for ADR-009/010/012/013 proposals and the `PlaneGuard` design; [Open] O-03, O-04, O-13, O-24..O-26. Evidence is cited by path; reviewer sign-off pending IVA.
