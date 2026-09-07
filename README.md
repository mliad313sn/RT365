# Global AI-MCP RoboTrader — Project Kit v1.1 + dev/sim build

**Version 1.1 — 7 September 2026.** Basis: *Master Product, Architecture, Governance and Delivery Blueprint* sections 00–17. Nothing in this repository enables a market, a strategy or autonomous execution; those require gate evidence and board sign-off. The code here is the **development/simulation** build of the control envelope: it proves determinism, fail-closed behaviour, topology enforcement, idempotency and auditability with simulated data and a simulated broker. It makes no claim about returns, regulatory status, broker capability or data entitlement.

## Provenance convention (applies to every file)
`[Source: NN]` taken from blueprint section NN · `[Committee]` proposal requiring board validation · `[Open]` unresolved, tracked in `docs/RAID_LOG.md`.

## Layout
| Path | Content |
|---|---|
| `GOAL.md` | Master Delivery Orchestrator /goal prompt |
| `goals/01..28_*.md` | One /goal prompt per committee role |
| `goals/gate_A..F_*.md` | One /goal prompt per release gate |
| `goals/build/E01..E15_*.md` | Build-agent prompts per epic (for Claude Code): scope, requirements, test IDs, build rules |
| `goals/decisions/O-01..O-19_*.md` | Decision packs that prepare every open item for its human owner |
| `goals/external/*.md` | Workflows for brokers, data licences, legal, model providers, pen-test, drills, operators, infrastructure |
| `docs/` | Every artefact in blueprint §15 catalogue, pre-filled; `docs/SESSIONS/` holds the session packets and independent reviews; `docs/GATE_REPORTS/` the IVA gate validation reports |
| `docs/PROJECT_EXECUTION_PLAN.md` | Phase 0–7 sequence from empty repo to controlled GA |
| `docs/MISSING_ACTIONS.md` | Register of acts only humans can perform (sign, pay, authorise, operate) |
| `contracts/api/API_OPENAPI.yaml`, `contracts/events/*.json` | Schema-first contracts; event schemas generated from the typed models and drift-checked in CI |
| `mcp/policies/` | Signed tool registry (dev key), per-tenant allowlist, egress and runtime policy |
| `libs/core/rtcore` | Strict schemas, canonical hashing, plane guard, monotonic state machines |
| `services/*` | One package per bounded context (risk, compliance, approval, oms, execution, reconciliation, audit, killswitch, identity, market-data, strategy, backtest, portfolio) |
| `mcp/servers`, `connectors/brokers`, `connectors/data-providers` | MCP sandbox runtime and the six tools; broker adapter contract + simulated sandbox broker + certification harness; simulated feed |
| `apps/web` | FastAPI BFF (`web_bff.app`), dev/sim composition root (`web_bff.platform`), risk-first dashboard |
| `observability/` | Correlation, redacting JSON logs, metrics, tracer, SLI catalogue (targets unset), alert catalogue |
| `infra/` | Namespaces and network policies for the three planes; docker-compose; Dockerfile |
| `security/` | Security controls index, signing policy, SBOM output, secret-scan allowlist |
| `test/` | Control-quartet tests per TC area, property-based determinism, contract, integration, e2e; evidence plugin |
| `scripts/` | bootstrap, signing/verification, schema export, network-policy check, evidence report, broker certification, SBOM, secret scan |

## Authoritative pipeline, enforced by topology [Source: 00]
Market Data → Feature/Signal → Strategy Agent → Trade Intent → Schema Validation → Compliance Eligibility → Deterministic Risk → Optional Human Approval → Execution Gateway → Broker → Reconciliation → Surveillance → Immutable Audit. Analytics plane reaches the Control plane only through the intent queue; only the Execution Gateway has a broker route (`rtcore.planes`, `infra/kubernetes/network-policies`, TC-NET-001..004).

## Status (2026-09-07, dev/sim only)
151 tests passing (control quartets for 15 areas, property and contract tests) at the head of `claude/attachment-solution-dev-52k8u0`; lint, typecheck, schema-drift, network-policy, registry and secret-scan checks green. Committee challenge cycle 1, the Independent Validation Agent's Gate A/B/C reports and its re-validation of the first remediation are in `docs/SESSIONS/REVIEW_*.md` and `docs/GATE_REPORTS/` (verdicts: A REJECT on human decisions, B ACCEPT WITH CONDITIONS, C REJECT; all recommendations with the human approver pending). Nothing in this repository is approved, certified or authorised beyond dev/sim; see `docs/RAID_LOG.md` and `docs/MISSING_ACTIONS.md` for what humans must decide.

## Run the dev/sim build
```bash
make install          # pip install -e ".[dev]"
make all              # lint, typecheck, schema drift, policy checks, secret scan, tests, evidence report
make run-bff          # http://localhost:8080  (dashboard) — dev header auth only; see ADR-012 and RAID R-06
make certify-broker   # regenerates docs/BROKER_CERTIFICATIONS/sim-broker.md (reviewer signature pending)
```
Evidence: `test/evidence/evidence_index.json` → `docs/TEST_CASES/EVIDENCE_REPORT.md` (reviewer column is always *pending*: the author never certifies their own evidence).

## How to run the project with these prompts
1. Load `GOAL.md` as the orchestrator system prompt; follow `docs/PROJECT_EXECUTION_PLAN.md` phase by phase.
2. For each component C1–C12 and process P1–P6, invoke the accountable role's `goals/NN_*.md`, then a challenging role from a different line, then `goals/28_independent_validation_agent.md`. Session packets live in `docs/SESSIONS/`.
3. Write session outputs into the owned files in `docs/`; append to `RAID_LOG.md`, `DECISION_LOG.md`, `REQUIREMENTS_TRACEABILITY.md`, `AUDIT_EVIDENCE_INDEX.md`.
4. Convene gates with `goals/gate_*.md`. A gate authorises only the next environment on the ladder: dev → sim → shadow → paper → supervised pilot → capped autonomous pilot → controlled GA.
5. Chase `docs/MISSING_ACTIONS.md` weekly.

## Repository structure target [Source: 16]
`/apps/web /apps/admin /services/{market-data,strategy,backtest,portfolio,risk,compliance,approval,oms,execution,reconciliation,audit} /mcp/{servers,policies} /connectors/{brokers,data-providers} /contracts/{api,events} /infra/{iac,kubernetes} /observability /security /test /docs`

Protected paths requiring 2nd-line CODEOWNERS approval [Committee]: `/services/risk`, `/services/compliance`, `/services/execution`, `/services/killswitch`, `/mcp/policies`, `/security`, `/contracts/*` (see `.github/CODEOWNERS`; team handles are placeholders — MISSING_ACTIONS).
