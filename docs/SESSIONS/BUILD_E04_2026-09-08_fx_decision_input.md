# BUILD_E04 — FX as a deterministic decision input (register F-3)

| Field | Value |
|---|---|
| Session | BUILD_E04, 2026-09-08 |
| Epic | E04 — Portfolio & accounting (`goals/build/E04_portfolio_accounting.md`) |
| Register item | F-3 (docs/IMPROVEMENT_REGISTER.md §F) under delegation D-051; owner instruction "capable in every country on every continent" [Source: docs/GLOBAL_COMPATIBILITY.md §Currencies] |
| Branch / commits | `build/e04-fx-decision-input` — `917efd0` (tests, red), `cf662d3` (implementation), `09b3ff6` (format + evidence area + reason codes), `3f155b0` (TC-FX-005) |
| Environment | dev/sim only. Nothing here enables a market, a currency, a strategy or autonomy [Source: 00] |
| `make all` | green — lint, mypy (103 files), 21 event schemas, network policy, tool registry, 67 agents, secret scan (586 files), **216 tests passed**, evidence 196 records / 23 areas with a full quartet |

## 1. Roles

| Role | Who | Line |
|---|---|---|
| Author (build) | Build agent E04 (AI), for the Backend Lead | 1st |
| Accountable lead | Backend Lead | 1st |
| Reviewer (required, not obtained) | Chief Risk Agent (2nd line) — `services/risk` is a protected path (.github/CODEOWNERS) | 2nd |
| Reviewer (required, not obtained) | Trading Domain Lead — rate convention, settlement vs trading currency | 1st (different owner) |
| Assurance | Independent Validation Agent — may veto this evidence | 3rd |
| Approver | the human Product Owner (D-039). **No approval is recorded here.** | — |

Author ≠ reviewer ≠ approver. This packet is a recommendation; it certifies nothing.

## 2. Purpose

- FR-05 requires positions, cash, NAV and P&L from fills; FR-11 requires the deterministic pre-trade decision [Source: 02]. Both were single-currency in the dev/sim build: `AccountBook.cash` was one Decimal and the risk engine summed position market values across currencies as if they were commensurable [Source: code before `ded8e17`].
- docs/GLOBAL_COMPATIBILITY.md names F-3 as the build item: "FX rate as a decision input (fail closed when missing/stale), cross-currency NAV and limits, multi-currency cash ledger", with the FX **data licence** left as a human act (H-08) [Source: docs/GLOBAL_COMPATIBILITY.md].
- The control this session adds is: **an amount whose base-currency value is not known is never presented as a number and never decided upon.** Missing, unknown-pair, stale, future-dated or unbudgeted rates give `NavStatus.UNKNOWN` with a reason code, and the engine halts [Committee].
- Not delivered here and still open: margin models per asset class, attribution reports, durable ledger (R-05), FX-rate sourcing/licensing, the freshness budget value, settlement-vs-trading currency, per-tenant base currency [Open].

## 3. Decision — proposed ADR-021 (text for the ARB; **not** filed in docs/ADRs/, no id assigned)

> ### ADR-021 — FX rates are a deterministic decision input, supplied to the engine and to the ledger, never fetched by them
> **Status:** Proposed (build agent E04, 2026-09-08). **Deciders (proposed):** ARB with the Trading Risk Committee (freshness budget and rate convention) and the Data Architect (source and provenance); the Product Owner approves (D-039). **Consulted:** Backend Lead, Chief Risk Agent, Trading Domain Lead, Data Engineering Lead. **Provenance:** [Source: 02 FR-05/FR-11, 05, 08] / [Committee: ADR-001 planes, ADR-010/ADR-018 store seam, ADR-020 audit conventions] / [Open: H-08 FX licence, O-07 budget, O-29 fee/tolerance model].
>
> **Context.** An account may hold cash and positions in more than one ISO 4217 currency, and every limit, NAV ratio and capital envelope is expressed in one base currency. Something must turn the set of amounts into one number. Whatever does that is inside a control decision, so it must be reproducible from recorded inputs, must not perform I/O inside the deterministic engine (NFR-DET-01), and must never substitute a default when a rate is absent.
>
> **Decision.**
> 1. `FxSnapshot` is a strict, frozen model: base currency, `AAA/BBB → Decimal` rates, tz-aware `as_of`, `source`, `Provenance`, and a `snapshot_id` derived from the content, so an edited rate or a forged id is refused at the schema boundary.
> 2. Rates enter through one bitemporal store (`market_data.FxStore`, as-of × knowledge time) via one audited write path (`platform.ingest_fx`, action `fx.snapshot.ingested`, caller's `correlation_id`). There is **no** MCP tool and no intent field for a rate.
> 3. `rtcore.money.convert()` is the only conversion: Decimal only, direct or inverse leg, triangulation **only** through the snapshot base currency and only when both legs are present, one rounding at the end to the target's ISO 4217 minor units, and a typed `FxUnavailable` error instead of a fallback rate.
> 4. The ledger converts at *valuation* time, never at fill time: every fill settles a cash leg in the instrument's currency. The account snapshot carries `cash_by_currency`, `Position.base_market_value` and a typed `Valuation` (`KNOWN`/`UNKNOWN` + `reason_code` + `fx_snapshot_id`).
> 5. `risk_engine.decide()` receives `(fx, fx_max_age_s)` as arguments beside the market and account snapshots. An `UNKNOWN` valuation, or an order that cannot be expressed in the account base currency, is `HALTED` with `RK-FX-MISSING`, `RK-FX-STALE` or `RK-FX-UNDEFINED`. The engine performs no I/O.
> 6. An undefined freshness budget is **not** "unlimited": it is `RK-FX-UNDEFINED` and it halts.
>
> **Alternatives considered.**
>
> | Alternative | Pros | Cons | Why not |
> |---|---|---|---|
> | A. FX as an input handed to the engine and the ledger (**chosen**) | pure and reproducible; one write path to audit; UNKNOWN is expressible; conversion is testable in isolation | callers must fetch the snapshot and carry a budget; a second bitemporal store | chosen: it is the only option that keeps `decide()` a pure function of recorded inputs |
> | B. The engine fetches the rate itself (client inside the engine) | fewer parameters at the call site | I/O inside the deterministic decision breaks NFR-DET-01 and replica reproduction (TC-RK-001); a network failure would become a risk outcome; the engine would need credentials | rejected |
> | C. Rates embedded in each market snapshot | already a bitemporal, provenance-stamped object; nothing new to wire | the rate would be duplicated per instrument and could disagree between two snapshots decided in the same instant; a cash-only currency (a JPY balance with no JPY instrument) would have no rate at all; the market-data contract and 21 event schemas would change | rejected; revisit only if the licensed feed delivers rates per instrument |
> | D. Per-account fixed rates (a configured table) | trivial; no feed licence needed | a fixed rate is a silent, permanent mis-valuation and would let a limit pass on a number nobody published; it is exactly the "silent 1.0" the control forbids | rejected |
> | E. Refuse multi-currency accounts entirely | no FX anywhere | contradicts the owner instruction (every country, every continent) and hides the risk rather than controlling it | rejected |
> | Rounding: half-even at the end / per-leg / banker's on intermediates | — | per-leg rounding drifts over many legs; no rounding leaks 28-digit artefacts into displayed money | one rounding, at the end, to the target's minor units |
>
> **Consequences.** `ENGINE_BUILD_HASH` changes (the engine source changed), so decision ids of the same inputs differ from previous builds — expected and covered by TC-RK-001. A single-currency book is unaffected: no snapshot is required and no budget is consulted. Cross-currency books cannot trade until a rate source exists per pair — which is the intended fail-closed behaviour, and which makes H-08 (FX data licence) a blocker for any real multi-currency cell, not a nicety.

Second decision recorded here for the log: **the FX quartet is filed as its own area TC-FX rather than appended to TC-RC**, because `scripts/export_test_cases.py` derives the evidence area from the test id and TC-RC is bound to FR-14 reconciliation; alternatives were (a) keep TC-RC-006..009 in the reconciliation file (rejected: FR-05 evidence would be filed under FR-14), (b) a new TC-FX area (chosen).

## 4. Proposed RTM rows (**not** written to docs/REQUIREMENTS_TRACEABILITY.md; the Orchestrator assigns and files them)

| Req | Architecture element | Implementation owner | Control | Test IDs (quartet) | Evidence | Gate | Status |
|---|---|---|---|---|---|---|---|
| FR-05 | Portfolio ledger (`portfolio_service.ledger`) — balance per currency; valuation from an FX snapshot supplied by the caller; `rtcore.money.convert`, `rtcore.schemas.fx.FxSnapshot`, `rtcore.world.CURRENCIES` | Backend Lead | Cross-currency NAV, cash and exposure in the account base currency; typed `NavStatus.UNKNOWN` + reason code instead of a number when a rate is missing, unknown, stale, future-dated or unbudgeted; content-bound `snapshot_id`; Decimal only | TC-FX-001 (positive), TC-FX-002 (negative), TC-FX-003 (abuse), TC-FX-004 (recovery) | TEST_CASES/TC-FX.md | C | dev/sim; FX source and licence [Open: H-08]; freshness budget [Open: O-07] |
| FR-11 | Deterministic risk engine (`risk_engine.decide`) takes `(fx, fx_max_age_s)` as decision inputs | Backend Lead (2nd-line: Chief Risk Agent) | Fail closed on FX: `RK-FX-MISSING` / `RK-FX-STALE` / `RK-FX-UNDEFINED` are HALT codes; exposure book summed in base currency; no I/O in the engine | TC-FX-005; TC-RK-001 (determinism unchanged) | TEST_CASES/TC-FX.md, TEST_CASES/TC-RK.md | C | dev/sim; per-pair budget [Open: O-07] |
| NFR-GLO-01 | `rtcore.world.CURRENCIES` (ISO 4217 code → minor units) covering the principal currency of every country in the table, plus CLF/UYW | Data Architect (rows), Backend Lead (code) | `XXX` is not a currency; unknown or lower-case codes are refused; minor units drive rounding | TC-FX-001, TC-FX-003 | TEST_CASES/TC-FX.md | C | rows need reviewer verification against the current ISO 4217 register [Open: H-29] |

## 5. Threat-model delta (no T-numbers assigned; for the Security Architect)

| # | Threat | Surface added | Mitigation in this change | Residual |
|---|---|---|---|---|
| a | An agent or a compromised analytics component supplies or overrides a rate to move a valuation past a limit | none added — this is the point | No MCP tool writes a rate (TC-FX-003 asserts `set_fx_rate`, `ingest_fx_snapshot`, `override_fx` are `TOOL_NOT_REGISTERED` and raise `mcp.non_allowlisted_tool`); intents are `extra="forbid"` so `fx_rate` is refused; `ingest_fx` exists only on the composition root | Deployment must not expose an FX ingest route to the analytics plane [Open: O-37 pattern] |
| b | A tampered snapshot (rate edited in transit, in a file, or in a store row) | the new FX store and its JSON form | `snapshot_id` is derived from the content and re-checked at every `model_validate`; a forged id and an edited rate both raise | The digest holds no key: tamper-evident, not tamper-proof against a writer who recomputes it — same limitation as ADR-018 §C-3; an anchored or signed feed is [Open] |
| c | A stale or replayed snapshot used to value a book (or a rate dated in the future to defeat a freshness check) | the freshness budget | Age is exact Decimal arithmetic; `age < 0` (future-dated) is `RK-FX-STALE`; an absent budget is `RK-FX-UNDEFINED`, never "unlimited" | The budget value itself is a placeholder [Open: O-07] |
| d | Look-ahead: a rate ingested later used to justify an earlier decision | bitemporal store | `latest(as_of, knowledge_ts)` never returns a row whose knowledge time is after the reader's (TC-FX-004) | The store is in-memory; durability is R-05 |
| e | Silent mis-valuation through a default rate, an implicit 1.0, or a float | conversion code | No default exists; `convert` raises; rates refuse floats at the schema boundary; one rounding at the end | Rate-source correctness (is 150 the right USD/JPY?) is a data-quality question this change cannot answer [Open: H-08] |
| f | Currency confusion: settlement currency vs trading currency vs the account base currency | the ledger's per-currency legs | The instrument master's `currency` is used for both the cash leg and the position; the account base currency is the only reporting currency | A market where trading and settlement currencies differ (for example GBX/GBP quoting, or CNH/CNY) is **not** modelled [Open] — see §9 |

## 6. Control quartet

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| Cross-currency valuation of an account (FR-05) | TC-FX-001 — a JPY/KWD/USD book values to USD; NAV 100091.67, exposure 2133.34, cash per currency; minor units 0/2/3/4; triangulation EUR→USD→JPY | TC-FX-002 — missing snapshot, missing pair, stale, future-dated and unbudgeted each give `UNKNOWN`, `value is None`, the right reason code, and a typed raise from `nav()` | TC-FX-003 — rate 0/negative/NaN/±Inf/float, `ZZZ`, `XXX`, lower-case, `USDJPY`, `USD/USD`, duplicate pair, naive `as_of`, empty source, unknown field, edited rate, forged `snapshot_id`; no MCP tool and no intent field can carry a rate | TC-FX-004 — UNKNOWN → stale → fresh snapshot ingested through the store restores a numeric NAV; two `fx.snapshot.ingested` rows under one correlation id; audit chain verifies; no look-ahead |
| FX as a decision input to the deterministic engine (FR-11) | TC-FX-005 first assertion (single-currency book decides with no snapshot at all) + TC-RK-001 (determinism unchanged) | TC-FX-005 — UNKNOWN valuation and an unconvertible order both HALT with the FX reason codes; repeating the call returns the identical record | TC-FX-003 (the abuse surface is the same one: nothing outside the operator path can inject a rate) | TC-FX-005 last assertion — with a fresh snapshot the same order carries no FX reason code and is judged on its base-currency notional |

## 7. Evidence

| Artefact | Path |
|---|---|
| Quartet | `test/quartets/test_tc_fx_valuation.py` (TC-FX-001..005) |
| Generated evidence | `docs/TEST_CASES/TC-FX.md` (new area), `docs/TEST_CASES/EVIDENCE_REPORT.md` (196 records, 23/23 areas with a full quartet) |
| Reason dictionary | `docs/REASON_CODES.md` rows `RK-FX-MISSING`, `RK-FX-STALE`, `RK-FX-UNDEFINED`, generated from `apps/web/web_bff/reason_codes.py` |
| Schema | `libs/core/rtcore/schemas/fx.py`, `libs/core/rtcore/schemas/account.py` (`NavStatus`, `Valuation`, `cash_by_currency`, `Position.base_market_value`, `OpenOrder.currency`) |
| Conversion | `libs/core/rtcore/money.py` (`is_iso4217`, `minor_units`, `quantize_money`, `convert`), `libs/core/rtcore/errors.py` (`FxUnavailable` family), `libs/core/rtcore/clock.py` (`age_seconds_decimal`), `libs/core/rtcore/world.py` (`CURRENCIES`) |
| Ledger | `services/portfolio/portfolio_service/ledger.py` |
| Store and write path | `services/market-data/market_data/fx.py`, `apps/web/web_bff/platform.py` (`ingest_fx`, `fx_for_decision`, `account_snapshot`) |
| Protected path | `services/risk/risk_engine/engine.py` (+84/−12 lines: imports, `FX_CODES`, four `_Ctx` fields, `_book` in base currency, `_fx_guard`, two `decide` parameters and one guard block) — **needs the named 2nd-line CODEOWNER approval** |
| Pipeline | `services/oms/oms/pipeline.py` (`fx_inputs` provider, default `(None, None)`) |
| This packet | `docs/SESSIONS/BUILD_E04_2026-09-08_fx_decision_input.md` |

## 8. Proposed RAID rows (**not** written to docs/RAID_LOG.md; no ids assigned)

| Type | Proposed text | Owner | Gate |
|---|---|---|---|
| Open item | FX rate source, licence and entitlement per pair and per cell; provenance label for production (`Provenance.SIMULATED` is dev/sim only). Until it exists, no cross-currency cell can be valued and every such decision halts | Data Engineering Lead, Legal Agent (licence H-08) | C |
| Open item | FX freshness budget: value(s), granularity (global / per pair / per asset class / per session state) and the behaviour at a venue close or a weekend, when the newest honest rate is hours old by construction. Placeholder in code: `FX_MAX_AGE_S = Decimal("5")` in the sim composition root only, and a per-call argument everywhere else | Trading Risk Committee | C |
| Open item | Which currency is a tenant's / an account's base currency, who may set it and whether it can ever change (a base-currency change re-bases every historical NAV, P&L and limit) | Product Owner, Trading Domain Lead | C |
| Open item | Settlement currency vs trading currency vs quotation unit (GBX/GBP, CNH/CNY, ILA/ILS): the ledger currently uses one `currency` field from the instrument master for the position and its cash leg | Trading Domain Lead, Data Architect | C |
| Risk | Concentration-by-currency (`RK-CONC-CCY`) groups by the instrument currency but its threshold is a percentage of a base-currency NAV; the semantics of "currency concentration" for a hedged or a cash-only currency exposure are undefined | Chief Risk Agent | C |
| Risk | `AccountSnapshot.gross_exposure` / `net_exposure` fall back to `market_value` when `base_market_value` is None. In this build that state is unreachable through the composition root (an unconvertible position makes the whole valuation UNKNOWN and the engine halts first), but a future caller could construct such a snapshot directly | Backend Lead | C |
| Risk | The ISO 4217 rows in `rtcore.world.CURRENCIES` (codes and minor units) are seeded, not verified against the current register; the same reviewer step as the country table (H-29) applies before any real cell | Data Architect | C |
| Dependency | R-05: the FX store is in-memory like the market-data store; a restart loses every rate and every account with a foreign leg becomes UNKNOWN until re-ingest. Fail-closed, but an availability risk to size before shadow | Backend Lead, SRE Lead | C |
| Open item | O-29 (existing): the fee/accrual model per broker **and currency**; this change books the fee in the instrument's currency, which is an assumption, not a broker fact | Trading Risk Committee, Broker-Connector Lead | C |

## 9. Concerns for the Product Owner

**Rate-source licensing.** Nothing in this change obtains, or entitles the platform to, a single FX rate. The code accepts a snapshot with a `source` string and a provenance label; the only label used anywhere in this build is `SIMULATED`, which the platform refuses to treat as production data. Before any cross-currency cell can be valued for real, someone must license an FX source, and the licence has to permit the *use* we make of it — valuing customer accounts and gating orders, which is usually a different (and more expensive) right than displaying a rate. This is H-08 in MISSING_ACTIONS and it is now a hard blocker rather than a nice-to-have: with no rate, a multi-currency account is `UNKNOWN` and every order on it halts. I could not verify what any provider offers or costs. [Open: H-08]

**The freshness budget.** I did not invent a threshold. The code takes the budget as an argument at every call and treats an absent budget as a failure (`RK-FX-UNDEFINED`), never as "unlimited". The dev/sim composition root carries one placeholder, `FX_MAX_AGE_S = Decimal("5")` seconds, chosen only so the sim tests can exercise fresh-versus-stale; it is labelled in the code as a fixture and not a policy value. **Proposed placeholder for the Trading Risk Committee to replace: 5 seconds, global.** [Open: O-07] The real question is harder than a number: an FX rate is not quoted continuously in every pair, and outside the relevant market's hours the newest honest rate may be many hours old. A single global budget will either halt trading every weekend or accept rates that are stale in fast markets. The Committee should decide the granularity (per pair, per asset class, per session state) and what should happen at a venue close — halt, or value at the official close rate with an explicit label. [Open]

**Which currency is a tenant's base.** The build assumes one base currency per *account*, set when the account is opened (`USD` for the sim fixture), and reports NAV, limits, P&L and the capital envelope in it. Nobody has decided who chooses it, whether a tenant with accounts in several countries has one base or several, or whether it can ever be changed — a change re-bases every historical NAV, drawdown, peak and limit, so my strong recommendation is that it be immutable after the first fill and that a "change" be a new account. I could not find a decision on this in the ledgers. [Open]

**Settlement versus trading currency.** The instrument master has one `currency` field, and this change uses it for both the position's value and the cash leg of a fill. Real markets separate these: London quotes in pence but settles in pounds; some venues trade in one currency and settle in another; offshore/onshore pairs (CNH/CNY) are different currencies with different rates. Nothing in this build detects that mismatch — it will simply book a cash leg in the quoted currency. This needs a Trading Domain Lead decision (and probably a second field on the instrument master) before any venue with a quotation unit is enabled. [Open]

**What I could not verify.**
- The ISO 4217 rows I added (156 rows: the 154 distinct national currencies of the country table, `XXX` excluded, plus the fund codes CLF and UYW, each with its minor units) are seeded from public knowledge and are *not* checked against the current register; codes change (SLE, ZWG, MRU, VES are recent). They need the same reviewer step the country table has (H-29). A wrong minor-unit value would round money incorrectly and silently. [Open: H-29]
- The rate convention `A/B = one unit of A is B units of B` is the market convention I implemented and the one the tests encode; no broker or vendor contract was available to confirm which direction a future feed will deliver. A mis-read direction would be a large, silent valuation error, so the ingest path should validate direction against a known reference before shadow. [Open]
- Whether any broker we might certify reports multi-currency balances in a form that reconciles against this ledger (O-29 covers the fee and tolerance half of the same question). Fees are booked here in the instrument's currency; that is an assumption. [Open: O-29]
- The freshness, availability and cost characteristics of any real FX feed, and therefore whether a fail-closed valuation is operationally acceptable on a normal trading day. [Open]

**What this does not do.** It does not enable a currency, a country, a venue or a market. It does not make the platform "global": it makes the platform able to *say honestly that it does not know*, which is the prerequisite. Profit is an objective, never a promise; the P&L fields are set to zero, not to a guess, when the valuation is unknown.

## 10. Assumptions, confidence, provenance

- **Assumptions.** (1) The account base currency is the reporting currency for every limit and ratio [Committee]. (2) A fill's cash leg settles in the instrument's currency [Committee; assumption, see §9]. (3) A rate dated in the future relative to decision time is a clock anomaly and is treated as stale [Committee]. (4) An identity conversion needs neither a snapshot nor a budget, so single-currency books are unchanged [Source: code].
- **Confidence.** High that the control behaves as tested in dev/sim (216 tests, quartet complete, `make all` green). Medium that the design survives a real feed unchanged — the ingest path is deliberately narrow but has only ever seen a fixture. Low on anything about licensing, budgets or venue conventions, all of which are human decisions listed above.
- **Provenance.** [Source: 02 FR-05/FR-11, 05, 08]; [Committee: ADR-001, ADR-008, ADR-010, ADR-018, ADR-020, docs/GLOBAL_COMPATIBILITY.md F-3, D-051]; [Open: H-08, H-29, O-07, O-29, R-05, and the new rows in §8].
- **Test facts corrected** relative to the recovered specification: only the four test ids (`TC-RC-006..009` → `TC-FX-001..004`) and the addition of `@pytest.mark.env("sim")`; every assertion is byte-for-byte the one written before the implementation. TC-FX-005 is new coverage for the protected-path change, not a change to the contract.
