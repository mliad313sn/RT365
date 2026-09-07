# goals/build — build-agent prompts per epic [Source: 14, 16; Committee ADR-028 in SESSIONS/C12]

One prompt per epic E01–E15 for Claude Code (or any coding agent). Each carries the epic's scope, requirement IDs, code paths, test IDs, current dev/sim state, the open items the agent may not close on its own, and the mandatory build rules from CLAUDE.md. Generated agent definitions live in `.claude/agents/build-e*.md` (`scripts/generate_agents.py`).

| Epic | Prompt | Accountable | 2nd-line reviewer | First gate |
|---|---|---|---|---|
| E01 Foundation & identity | `E01_foundation_identity.md` | Backend Lead | Security Architect | B |
| E02 Market data & instrument master | `E02_market_data_instrument_master.md` | Data Engineering Lead | Data Architect | C |
| E03 Broker adapter framework | `E03_broker_adapter_framework.md` | Broker-Connector Lead | Trading Domain Lead | C |
| E04 Portfolio & accounting | `E04_portfolio_accounting.md` | Backend Lead | Chief Risk Agent | C |
| E05 Deterministic risk engine & Kill Switch | `E05_deterministic_risk_engine.md` | Backend Lead | Chief Risk Agent | C |
| E06 Compliance & eligibility | `E06_compliance_eligibility.md` | Backend Lead | Compliance Agent | D |
| E07 OMS & execution gateway | `E07_oms_execution_gateway.md` | Backend Lead | Trading Domain Lead | C |
| E08 Strategy & backtesting | `E08_strategy_backtesting.md` | Quant Research Lead | Model Risk Lead | C |
| E09 MCP / AI governance | `E09_mcp_ai_governance.md` | Backend Lead | MCP Security Agent | D |
| E10 Dashboard & mobile | `E10_dashboard_mobile.md` | Frontend Lead | Accessibility Lead | C |
| E11 Audit, surveillance, reporting | `E11_audit_surveillance_reporting.md` | Backend Lead | Compliance Agent | D |
| E12 Observability & SRE | `E12_observability_sre.md` | SRE Lead | ARB | C |
| E13 Security & privacy | `E13_security_privacy.md` | Security Architect | Security & Privacy Board | B |
| E14 Billing, support, admin | `E14_billing_support_admin.md` | Backend Lead | Finance / Support & Training Lead | F |
| E15 Regulatory & market launch | `E15_regulatory_market_launch.md` | Compliance Agent | Legal Agent | F |

Order of build (docs/PROJECT_EXECUTION_PLAN.md): E01, E13 (Gate B) → E02, E03, E04, E05, E07, E08, E10, E12 (Gate C) → E06, E09, E11, E14 (Gate D) → E15 (Gate F). E05 and E07 touch protected paths and need 2nd-line CODEOWNER approval on every merge.
