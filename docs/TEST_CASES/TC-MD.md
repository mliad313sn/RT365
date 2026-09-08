# TC-MD — Market data provenance, freshness, look-ahead

Control: Market data provenance, freshness, look-ahead — Requirement: FR-03 — RTM row: FR-03 — Owner: Data Engineering Lead — Reviewer (≠ owner): Data Architect — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T15:48:15.949441+00:00 at `5bf73b616d466abb75922409297f9ef323a3239c` (tree clean, tested tree `18b0a7418af7`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-MD-001 | Every stored snapshot carries market_ts, ingest_ts, provenance and quality; the universe includes delisted names as of date. | pass | passed | `test/quartets/test_tc_md_marketdata.py::test_bar_stored_with_timestamps_and_provenance` |
| negative | TC-MD-002 | Snapshot older than the per-asset-class freshness budget -> RK-FRESH rejection; autonomy would be suspended by SLO semantics. | pass | passed | `test/quartets/test_tc_md_marketdata.py::test_stale_beyond_budget_rejected` |
| abuse | TC-MD-003 | Poisoned tick (outlier) is flagged SUSPECT and rejected; backdated ingest is a clock anomaly; unentitled tenant is denied. | pass | passed | `test/quartets/test_tc_md_marketdata.py::test_outlier_backdated_and_unentitled_data` |
| recovery | TC-MD-004 | After a stale period, a fresh bar restores decisions without any manual step. | pass | passed | `test/quartets/test_tc_md_marketdata.py::test_feed_restored_next_intent_passes` |

Quartet complete: yes. Records: 4.
