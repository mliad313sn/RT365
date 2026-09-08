# TC-FX — FX as a deterministic decision input: cross-currency NAV, cash and limits, fail closed when missing or stale

Control: FX as a deterministic decision input: cross-currency NAV, cash and limits, fail closed when missing or stale — Requirement: FR-05 — RTM row: FR-05 — Owner: Backend Lead — Reviewer (≠ owner): Chief Risk Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T15:53:14.477297+00:00 at `48650eda8aff77972e8d6c81c28e9a3fce99dd88` (tree dirty, tested tree `2628132e3ba5`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-FX-001 | A JPY/KWD/USD book converts to the USD base through the FX snapshot: NAV, cash per currency and exposure are Decimal, rounded per ISO 4217 minor units; positions keep their instrument currency; triangulation only through the snapshot base. | pass | passed | `test/quartets/test_tc_fx_valuation.py::test_multi_currency_book_values_in_base_with_fx_snapshot` |
| negative | TC-FX-002 | A missing snapshot, a missing pair, an undefined budget or a stale snapshot make the NAV UNKNOWN (typed, value None, reason code); `nav()` raises a typed FX error; nothing falls back to a 1.0 rate. | pass | passed | `test/quartets/test_tc_fx_valuation.py::test_missing_or_stale_rate_makes_nav_unknown_never_a_number` |
| negative | TC-FX-005 | The deterministic engine receives the FX snapshot as an argument (it never fetches one): an UNKNOWN account value, or an order it cannot express in the account base currency, is HALTED with RK-FX-MISSING / RK-FX-STALE / RK-FX-UNDEFINED, and the decision stays reproducible. | pass | passed | `test/quartets/test_tc_fx_valuation.py::test_risk_engine_takes_fx_as_an_input_and_halts_when_it_is_missing_or_stale` |
| abuse | TC-FX-003 | Rate 0, negative, NaN/Infinity, unknown or lower-case ISO 4217 code, bad pair form, same-currency pair, duplicate pair, naive timestamp, unknown field and a snapshot id that does not match its content are rejected at the schema boundary; no MCP tool can write a rate and an intent cannot carry one. | pass | passed | `test/quartets/test_tc_fx_valuation.py::test_fx_snapshot_schema_boundary_rejects_bad_rates_and_no_agent_can_supply_one` |
| recovery | TC-FX-004 | UNKNOWN (missing, then stale) -> a fresh snapshot ingested through the store restores a numeric NAV; the audit trail shows the ingests under one correlation id and the store never serves a snapshot beyond knowledge time. | pass | passed | `test/quartets/test_tc_fx_valuation.py::test_fresh_fx_snapshot_restores_numeric_nav` |

Quartet complete: yes. Records: 5.
