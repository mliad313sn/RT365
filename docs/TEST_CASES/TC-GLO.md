# TC-GLO — Global compatibility: any country, currency and venue timezone; enablement per cell only

Control: Global compatibility: any country, currency and venue timezone; enablement per cell only — Requirement: NFR-GLO-01 — RTM row: NFR-GLO-01 — Owner: Backend Lead / Data Engineering Lead — Reviewer (≠ owner): Compliance Agent — **signature pending** (generated evidence is never self-certified [Source: 00, 11])

Environment tag: dev/sim — Data version: `sim-policy-v0.1 | sim-feed seed=7 | tool_registry 0.1.0` — Generated 2026-09-08T14:44:53.342334+00:00 at `02b9e9e92cca83c89385b98dedca922704f43e39` (tree dirty, tested tree `e85220959f2e`)

| Quartet | Test ID | Given/When/Then (docstring) | Expected | Actual | Evidence link |
|---|---|---|---|---|---|
| positive | TC-GLO-001 | The world registry covers every ISO 3166-1 country/territory on all seven continents with an ISO 4217 currency; each can be proposed as a jurisdiction cell (proposed, never enabled). | pass | passed | `test/quartets/test_tc_glo_global.py::test_every_country_on_every_continent_is_a_valid_cell_with_a_currency` |
| negative | TC-GLO-002 | A cell for a code that is neither ISO 3166-1 nor user-assigned is refused; user-assigned codes (ZZ) are accepted only as simulated and say so. | pass | passed | `test/quartets/test_tc_glo_global.py::test_unknown_country_codes_are_refused_and_simulated_codes_are_labelled` |
| abuse | TC-GLO-003 | Proposing every country enables nothing: no legal record, no flag, eligibility stays INELIGIBLE; a simulated cell can be exercised in sim but its legal record is labelled simulated in the audit. | pass | passed | `test/quartets/test_tc_glo_global.py::test_world_coverage_never_means_legal_availability` |
| recovery | TC-GLO-004 | Venue sessions declared in local time (Tokyo, São Paulo, Sydney) evaluate correctly across the UTC day boundary and honour local-date holidays; UTC-declared venues keep working. | pass | passed | `test/quartets/test_tc_glo_global.py::test_venue_calendars_work_in_any_timezone_including_day_boundaries` |

Quartet complete: yes. Records: 4.
