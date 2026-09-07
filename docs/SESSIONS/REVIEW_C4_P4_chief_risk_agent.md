# REVIEW_C4_P4 — Chief Risk Agent CHALLENGE of C4 (Deterministic Risk Engine) and P4 (Kill Switch)

| Owner (this packet) | Builder under review | Assurance | Session step | Date | Status |
|---|---|---|---|---|---|
| Chief Risk Agent (2nd line, goals/06) | Backend Lead (1st line, E05) | Independent Validation Agent (3rd line, veto) | CHALLENGE (operating loop step 2) | 2026-09-07 | Draft v1.0 — findings only, not self-certified |

This packet contains findings and proposals only. The Chief Risk Agent does not write or merge risk-engine code and does not approve changes to the artefacts it owns (docs/RISK_POLICY.md, docs/LIMIT_MATRIX.md); every remedy below is a proposal for the Backend Lead (code) or the Trading Risk Committee (policy), to be validated by IVA [Source: 00, 13; goals/06].

---

## 1. Roles

| Line | Role | Person/agent | Responsibility in this session |
|---|---|---|---|
| 2nd | Challenger | Chief Risk Agent (goals/06) | Adversarial review of C4/P4 against blueprint 05 and RISK_POLICY/LIMIT_MATRIX; opens RAID entries; proposes RTM rows and policy ADRs [Committee] |
| 1st | Builder | Backend Lead (goals/build/E05) | Owns services/risk, services/killswitch, services/oms, services/identity code and TC-RK/TC-KS tests; must remediate, never sole approver [Source: 13] |
| 3rd | Assurance | Independent Validation Agent (goals/20) | Reviews this packet and the builder's remediation evidence; holds veto at Gate C [Source: 00] |
| Board | Approver | Trading Risk Committee (chaired by Chief Risk Agent; the chair does not approve its own policy changes) | Approves RISK_POLICY/LIMIT_MATRIX changes and O-07/O-08 [Source: 05; goals/06] |

Author != reviewer != approver holds: Backend Lead authored the code, Chief Risk Agent reviews, IVA and the Committee approve [Source: 13].

## 2. Purpose

- Confirm that `decide()` is a pure, fail-closed function of (intent, account snapshot, market snapshot, policy version) and that every pre-trade control #1-16 is implemented with reason code, evaluated value and threshold [Source: 05].
- Confirm that runtime controls produce HALT events consumed by the Kill Switch and that the Kill Switch blocks new risk first, cancels, applies the per-account emergency policy (CANCEL_ONLY default), revokes agent tools, preserves evidence and needs two persons from different lines to deactivate [Source: 02, 05, 10; Committee P4].
- Confirm limit hierarchy platform > tenant > account > strategy > instrument with effective = min, changed only by maker-checker with cooling period and with no agent/MCP write path [Source: 00, 05; Committee].
- Numeric thresholds are not judged here: every number in `sim-policy-v0.1.yaml` and `RuntimeThresholds` is a sim fixture [Open: O-07, O-03]. The liquidation policy content is not judged here [Open: O-08].
- Evidence basis [Committee]: read of the 16 files named in the session packet plus `apps/web/web_bff/platform.py`, `apps/web/web_bff/app.py`, `services/identity/identity_service/rbac.py`, `libs/core/rtcore/{money,clock,lines,ids,provenance}.py`, `libs/core/rtcore/schemas/{intent,market}.py`; execution of `python3 -m pytest test/quartets/test_tc_rk_determinism.py test/property test/quartets/test_tc_ks_killswitch.py -q -p no:cacheprovider` (55 passed); and 22 read-only adversarial probes P1-P22 executed against `build_sim_platform()` (Appendix A). Files were reformatted on disk during the review; all `file:line` references below are to the reformatted content re-read on 2026-09-07.

## 3. The three strongest objections

### Objection 1 — Kill Switch engagement is not fail-closed: side effects run before the state is recorded, and a failing hook leaves the switch un-engaged with no audit trail

- **Severity:** Critical
- **Where:** `services/killswitch/killswitch_service/service.py:79-115`. The comment at line 79 says "1. block new risk: the activation itself is the flag consulted by the risk engine", but the `Activation` is only stored at line 109, after `cancel_open_orders` (line 81), `emergency_policy_for`/`apply_liquidation` (83-90), `revoke_agent_identities` (92) and `evidence_snapshot` (94) have all run. `halt_account` runs at 110-111, audit at 112. Nothing is wrapped in `try/except`.
- **Evidence:** Probe P9 — with `cancel_open_orders` raising `RuntimeError("broker down")` (the exact condition a Kill Switch exists for), `activate()` propagates the exception, `ks.active() == ()`, `ks.blocks(...) is False`, no `killswitch.activated` audit record exists and `halt_account` never runs. The account keeps trading. [Evidence: Appendix A, P9]
- **Why it matters:** "Kill Switch ... supersedes everything" [Source: 00]. P4 orders the actions "block new risk; cancel open orders; apply emergency policy; revoke; preserve evidence; notify" [Committee P4]. The code inverts that order, so (a) in a deployed multi-process topology new intents evaluated between line 81 and line 109 still see `KillSwitchFlags()` = none and are APPROVED; (b) the most likely real-world trigger (broker/venue failure) is precisely the one that makes the switch silently not engage; (c) there is no partial-failure record, so operators cannot tell that engagement failed. The state is also an in-memory dict (`_activations`, line 65; the dev/sim in-memory limitation is already logged as existing R-05, but the missing fail-closed read semantics are a design gap independent of the store) and `halt_account` is only invoked for `KillSwitchLevel.ACCOUNT` (110-111), so PLATFORM/TENANT/STRATEGY/ASSET/VENUE activations vanish on a service restart without any two-person deactivation (see F-18).
- **Proposed remedy (for Backend Lead; IVA to verify):** Persist the `Activation` as step 0 (durable store, synchronous, before any hook) with `active=True` and `engaged_state=ENGAGING`; execute each hook in its own `try/except`, recording per-hook outcome in the activation (`hook_results`), raising an S1 alert `killswitch.hook_failed` on any failure and retrying via a saga; never allow an exception to leave the activation unrecorded. The risk engine must treat "kill-switch state unknown/stale" as HALTED (see Objection 2). Add TC-KS-007 (abuse/recovery): hook raises -> activation recorded, flags set, new intents HALTED, S1 alert raised.

### Objection 2 — Fail-open defaults on the execution path: a missing account snapshot at approval time routes to LIVE, kill-switch/account state cannot express "unknown", and account-snapshot staleness is never checked

- **Severity:** Critical
- **Where:**
  - `services/oms/oms/pipeline.py:164-173` — `on_approval`: `mode = acct.mode if acct else AccountMode.SUPERVISED`; the kill-switch/HALTED guard at 166 is skipped when `acct is None`; execution proceeds.
  - `services/oms/oms/pipeline.py:54` — `TARGET_FOR_MODE` maps only BACKTEST and PAPER; every other or unknown mode falls through to `ExecutionTarget.LIVE` at line 208 (`TARGET_FOR_MODE.get(mode, ExecutionTarget.LIVE)`). Probe P13: SUPERVISED, BOUNDED_AUTONOMOUS, HALTED and OBSERVE all resolve to LIVE.
  - `libs/core/rtcore/schemas/account.py:108` — `kill_switch: KillSwitchFlags = KillSwitchFlags()`; the schema default is "no kill switch anywhere", so a snapshot builder that omits or fails to fetch kill-switch state yields an APPROVED-capable snapshot. `KillSwitchFlags` (72-83) has no `as_of` or `state_known` field.
  - `services/risk/risk_engine/engine.py:164-202` — freshness is checked only for `market_snapshot.market_ts`; `account_snapshot.as_of` (`account.py:90`) is never compared with `now`. Probe P2: an account snapshot one day old -> APPROVED with no reason code.
  - `services/risk/risk_engine/engine.py:103-140` — the engine checks `account_id` match (109) but never `validated_intent.tenant_id == account_snapshot.tenant_id`. Probe P5: tenant mismatch -> APPROVED.
  - The approved decision is never re-evaluated at approval time; only intent expiry (approval queue) and, when a snapshot exists, kill-switch/HALTED are checked. Limits, freshness, trading status, exposure may all have changed.
- **Why it matters:** The contract is "Unavailable inputs -> HALTED (fail closed)" [Source: 05; RISK_POLICY decision contract] and "Only the deterministic Execution Gateway submits real orders after Risk, Compliance/Eligibility and account policy authorise it" [Source: 00]. `decide()` itself is fail-closed for `None` inputs (TC-RK-004, property test), but the pipeline re-introduces fail-open defaults after the decision: the unavailable-snapshot branch that HALTs in `_process` becomes LIVE execution in `on_approval`. Exposure is computed from positions whose age is unknown to the engine, which defeats controls #5-9 and #16 when the portfolio service is lagging. Default-to-LIVE is the opposite of the required posture for any new mode added later.
- **Proposed remedy:** (1) `on_approval`: `acct is None` -> transition to HALTED with `RK-HALT-INPUT`, never execute; re-run `decide()` with fresh snapshots and require `outcome in {APPROVED, REQUIRES_HUMAN_APPROVAL}` and the same `policy_version` as the queued decision (else re-queue/reject). (2) Replace `TARGET_FOR_MODE.get(mode, LIVE)` with an explicit allowlist and `ControlDenied` for anything else; LIVE only for SUPERVISED/BOUNDED_AUTONOMOUS with `policy.environment_tag in {"pilot","production"}` and `approved_for_production is True` (both fields exist in `policy.py:77-78` and are consumed nowhere — grep evidence). (3) `KillSwitchFlags`: add `as_of: datetime` and `state_known: bool` with no defaults; engine emits `RK-HALT-KS-UNKNOWN` when absent or older than a policy budget. (4) Add control `RK-FRESH-ACCOUNT` (account snapshot age <= budget; budget field to LIMIT_MATRIX "Freshness budget" row) and `RK-AUTH-TENANT`. Tests: TC-RK-017 (account staleness), TC-RK-018 (tenant mismatch), TC-AP-00x (approval with missing snapshot -> HALTED; re-decision at approval).

### Objection 3 — Exposure controls can be evaded by order splitting across instruments because open orders are not projected, while the same controls trap an account that is already over limit; and two runtime controls block nothing

- **Severity:** High (Critical once real capital is at risk; Gate C authorises paper only)
- **Where:**
  - `services/risk/risk_engine/engine.py:267-275` `_projected_positions` uses `acct.positions` plus this order only; `chk_exposure` (278-286), `chk_concentration` (290-303), `chk_leverage` (307-311) and `chk_correlated` (385-406) all ignore `acct.open_orders`. The only aggregation is `engine.py:261-262`: same instrument, same side, tested against `MAX_NOTIONAL_PER_ORDER` (a per-order metric reused as an aggregate — semantic confusion, over-restrictive for two legitimate resting orders and under-restrictive across instruments). Probe P3: NAV 100k, four open BUY orders totalling 160k on other instruments, new BUY -> gross exposure evaluated at 9.9% of NAV -> APPROVED. The "order splitting cannot evade the cap [Committee C4 abuse test]" comment is only true for one instrument.
  - `services/risk/risk_engine/engine.py:278-311, 385-406` have no risk-reducing carve-out. Probe P4: account at 300% gross vs 200% limit; a SELL of 100 shares (reducing) -> REJECTED with RK-CAP-POS, RK-EXP, RK-EXP-NET, RK-CONC, RK-CONC-CCY, RK-LEV, RK-CORR. With CANCEL_ONLY as the default emergency policy and the liquidation policy open [Open: O-08], the only path to reduce a breached book is a human override outside the engine.
  - `services/risk/risk_engine/monitors.py:91` and `:95` emit `RT-DRIFT` with `level=STRATEGY, target="*"` and `RT-VENUE` with `level=VENUE, target="*"`; `apps/web/web_bff/platform.py:302-303` passes `"*"` through as the target; `engine.py:132-137` tests `i.strategy_id in ks.strategies` / `i.venue in ks.venues`, which `"*"` never satisfies. Probe P11: after RT-DRIFT and RT-VENUE fire, flags are `strategies=('*',), venues=('*',)` and the next intent is APPROVED with no reason codes. TC-KS-006 only exercises RT-LOSS-DAILY, and TC-RK-016 only asserts the events exist.
  - `services/risk/risk_engine/monitors.py:71-78` — loss limits and drawdown are skipped when the limit is undefined (`if limit is not None and ...`), the opposite of the pre-trade `_cap_check` fail-closed rule (`engine.py:94-99`). Probe P12: no daily-loss/drawdown limit defined, 90% loss -> zero HALT events. `monitors.py:53` substitutes hard-coded `RuntimeThresholds()` when none are supplied.
  - `engine.py` does not consult `daily_pnl/weekly_pnl/monthly_pnl/peak_nav` at all, although they are in the snapshot (`account.py:99-103`). Probe P14: daily loss 50% of NAV, monitor not yet run -> APPROVED. Between monitor evaluations the pre-trade path adds risk to an account that has already breached its loss limit; there is no monitor heartbeat, so "monitor not running" is undetectable.
- **Why it matters:** Controls #6-9 and #16 exist to bound the exposure that can be reached, not the exposure already on the book [Source: 05]. An agent that sends N single-instrument orders each within caps reaches N times the intended exposure once they fill. Runtime controls "model drift" and "venue health" are listed as HALT triggers [Source: 05; RISK_POLICY runtime controls] and are currently no-ops at the engine. Undefined runtime limits silently disabling loss/drawdown halts is a fail-open condition that will exist by construction until O-07 closes.
- **Proposed remedy:** (1) Project remaining open-order notional (side-signed) into `_projected_positions` and into `chk_caps` position cap; add a per-account pessimistic exposure reservation in the OMS between decision and fill (or serialise decisions per account) [Committee decision needed, see §5]. (2) Define in RISK_POLICY a "risk-reducing order" rule (Committee ADR, proposed in §5): for closing sides, controls #6-9/#16 pass when the projected metric is strictly lower than the current metric and no other control fails; collar, freshness, kill switch, session, status still apply. (3) Monitors: STRATEGY halts must carry the concrete strategy ids in scope and VENUE halts the concrete venue id (the `RuntimeMetrics` schema needs `strategy_ids` / `venue_id`); alternatively map `"*"` to a PLATFORM or ACCOUNT activation so it fails closed. (4) Monitors fail closed on undefined limits (emit `RT-LOSS-*-UNDEFINED` -> ACCOUNT halt) and refuse to run without explicit thresholds. (5) Add pre-trade `RK-LOSS-DAILY/WEEKLY/MONTHLY` and `RK-DRAWDOWN` checks (defence in depth, same metrics) and a monitor heartbeat with a dead-man's switch that suspends autonomy after N seconds without evaluation (ties to C9 §3).

## 4. Additional findings

Format: ID — severity — location — finding — why it matters — remedy. Line references are to the reformatted files as of 2026-09-07.

- **F-01 — High — `services/killswitch/killswitch_service/service.py:83-90`, `apps/web/web_bff/platform.py:638-642`, `services/identity/identity_service/accounts.py:58-59`.** The liquidation path is gated only by `if liq_ref:` (a non-empty string). Probe P10: `liquidation_policy_ref="garbage-ref"` -> `apply_liquidation(CANCEL_AND_FLATTEN)` executed and recorded as applied. `Account.liquidation_policy_ref` and `emergency_policy` are plain fields with no maker-checker, no registry of approved liquidation policies, no effective date. The O-08 fallback test only covers the `None` case. Remedy: hard-disable reduce/flatten until O-08 closes (feature flag owned by the Committee); when enabled, resolve `liq_ref` against a signed registry of approved liquidation policies (maker, checker, version, effective_from) and record the resolved version in the activation. Emergency policy and liquidation ref changes go through `MakerChecker` with `require_different_line=True`. [Open: O-08]

- **F-02 — High — `services/identity/identity_service/accounts.py:141-166`.** `restore_from_halt` defaults `target=AccountMode.SUPERVISED` and does not store the pre-halt mode. Probe P7: PAPER account halted by the runtime monitor, restored by two persons with the default target -> SUPERVISED, skipping Gate D (`MODE_GATE`, lines 20-26) and the one-step promotion rule. A halt/restore cycle is therefore a promotion path without a gate record. Remedy: persist `pre_halt_mode`; restore only to `min(pre_halt_mode, requested)`; require a gate record for anything above pre-halt mode; add TC-ID/TC-KS abuse test.

- **F-03 — High — `services/identity/identity_service/accounts.py:175-181` and `:129-139`.** `set_trading_status` performs no actor check at all. Probe P8: an `ActorKind.AGENT` sets `trading_status=ACTIVE`. Trading status is the input of control #1 (`RK-AUTH-STATUS`). `halt()` checks role but not kind: Probe P8b: an AGENT carrying `Role.RISK_OFFICER` halts the account (denial-of-service on trading by an agent; audit shows a human role). Remedy: `is_human and role in MODE_CHANGERS` for `set_trading_status`; `halt()` accepts AGENT never, SYSTEM only for RUNTIME_MONITOR/SYSTEM roles; `suspend_autonomy` (168-173) takes an `Actor` not a free-text `by`.

- **F-04 — High — `services/identity/identity_service/makerchecker.py:102-110`, `apps/web/web_bff/app.py:283-293`, `apps/web/web_bff/platform.py:283-309` (no apply step), `services/risk/risk_engine/policy.py:158-160`.** The limit maker-checker is disconnected from the policy store: a change that reaches `EFFECTIVE` never mutates `RiskPolicy`, never bumps `policy_version`, never writes the LIMIT_MATRIX change log (maker, checker, cooling end, policy_version) [Source: 05; LIMIT_MATRIX]. Probe P19: EFFECTIVE change, policy unchanged. The actual write path is the YAML file loaded at boot with no signature, hash or maker/checker verification (`load_policy`, `policy.py:158-160`; `maker: chief_risk_agent:fixture` is free text), and tests assign `platform.policy = None/…` directly. `RiskPolicy.cooling_period_end` (`policy.py:89`), `approved_for_production` (78) and `environment_tag` (77) are consumed nowhere (grep). At the service layer any human in a different line may check — Probe P19: PORTFOLIO_MANAGER proposes, AUDITOR (3rd line) checks -> EFFECTIVE; only the HTTP layer (`rbac.py:35-70`) narrows this, and the MCP/agent runtime does not go through HTTP. Remedy: (a) policy artefact signed like `tool_registry.signed.json` under the asymmetric-signing decision already open as O-22; engine HALTs (`RK-HALT-POLICY`) when signature, maker != checker, or `cooling_period_end > now` fail; (b) `MakerChecker.effective()` is the only writer of a new `RiskPolicy` version (append-only policy versions, hash in the decision record); (c) role authorisation inside `MakerChecker` (proposers: RISK_OFFICER/CHIEF_RISK_AGENT; checkers: TRADING_DOMAIN_LEAD or Committee delegate; never 3rd line); (d) tightening effective immediately, loosening after cooling (policy ADR, §5). "No agent/MCP write path" is true today only because no apply path exists at all.

- **F-05 — High — `services/risk/risk_engine/monitors.py:28-34, 53`.** `RuntimeThresholds` carries numeric defaults in code (50 bps, 20%, 500 ms, 2x) and is substituted when `None` is passed. These are neither in LIMIT_MATRIX nor under maker-checker and will silently become production thresholds [Open: O-03]. Remedy: thresholds come from the policy hierarchy (`Metric` entries for slippage, rejection rate, latency, frequency factor), fail closed when undefined; delete the code defaults.

- **F-06 — Medium — `services/risk/risk_engine/engine.py:564` and `:488`.** `decision_id` is derived from intent hash, snapshot ids, policy version and build hash but not from `now`. Probe P6: same inputs one hour later -> same `decision_id`, outcome APPROVED -> REJECTED (RK-EXPIRED, RK-FRESH). Two audit records with the same id and different outcomes; the OMS idempotency key (`pipeline.py:189`) also ignores the decision. RISK_POLICY's contract lists four inputs, but decision time is a fifth. Remedy: include `now` in the id derivation; correct the RISK_POLICY decision contract to `decide(intent, account_snapshot, market_snapshot, policy_version, decision_time)` (Committee approval, not self-approved).

- **F-07 — Medium — `services/risk/risk_engine/engine.py:278-303`.** Negative NAV makes every `pct(x, nav)` negative and therefore `<= threshold`. Probe P1: NAV -1000 -> gross/net/concentration all PASS with value `-990.6`; only `chk_leverage` (310, `Infinity`) catches it, and only if a leverage limit is defined. Remedy: explicit precondition check `nav > 0` -> `RK-HALT-INPUT`/`RK-AUTH-NAV`, before any ratio is computed; property test with negative and zero NAV.

- **F-08 — Medium — `services/risk/risk_engine/policy.py:81` vs `services/risk/risk_engine/engine.py:299-302`.** `concentration_action` is dead: `chk_concentration` always emits REJECT codes. RISK_POLICY #8 says "REJECTED or REQUIRES_HUMAN_APPROVAL per policy". Same for `complex_asset_classes` (policy.py:86, unused in the risk path). Remedy: wire or delete; a policy knob the engine ignores is a false control.

- **F-09 — Medium — `services/risk/risk_engine/engine.py:361-381`.** Protective stop is checked for presence and side only. Probe P15: stop at 0.01 on a ~99 entry -> PASS. Control #15 "stop-loss / protective policy" [Source: 05] should bound the loss the stop implies (`|entry - stop| * qty <= X% NAV`, X [Open: O-07]) and require the stop to be an actual resting order or an OMS-managed exit, not a number on the intent. Remedy: add `RK-PROT-DIST` with value/threshold; LIMIT_MATRIX row "Max loss per position (stop distance)".

- **F-10 — Medium — `services/risk/risk_engine/engine.py:237-248`.** `SELL_SHORT` is not `is_buy`, so buying power is auto-PASS. Probe P16: short with zero buying power -> APPROVED. Margin requirements for shorts are not modelled anywhere (control #9 "leverage / margin" implements leverage only). Remedy: buying-power/margin check for SELL_SHORT and BUY_TO_COVER using the broker's margin model (capability certified per C10 §4; do not assume [Source: 00]).

- **F-11 — Medium — `services/risk/risk_engine/engine.py:334-336`, `libs/core/rtcore/schemas/intent.py:49`.** Duplicate detection compares the canonical hash, which includes `intent_id` (UUID). Probe P17: economically identical intent with a new id -> no RK-DUP. Control #11 needs an economic-duplicate window (account, instrument, side, quantity, price within N s [Open: O-07]) in addition to the replay check. Remedy: `RK-DUP-ECON` from `recent_intent_fingerprints` in the snapshot.

- **F-12 — Medium — `services/risk/risk_engine/engine.py:385-397`, `apps/web/web_bff/platform.py:155` (hard-coded `correlation_groups`).** Correlation groups are supplied by the account snapshot builder, not by policy, so they sit outside maker-checker; an instrument in no group is PASS with value 0. Missing group data is indistinguishable from "uncorrelated". Group exposure sums `abs()` (gross) — net semantics for hedged pairs are undefined in LIMIT_MATRIX. Remedy: groups move to the policy artefact (versioned, maker-checker); an instrument without group membership in an asset class that requires it fails `RK-CORR-UNDEFINED`; define gross vs net in LIMIT_MATRIX.

- **F-13 — Medium — `services/risk/risk_engine/policy.py:106-113`, `services/risk/risk_engine/monitors.py:54`.** Level/scope confusion: STRATEGY and INSTRUMENT limits are keyed by bare id, so a STRATEGY limit applies across all tenants/accounts sharing that strategy id (Probe P20: tenant-B/acct-B inherits `strat-sma-xover` 50k). Because effective = min this only tightens, but it leaks one tenant's risk appetite into another and makes "account x strategy" limits inexpressible. The runtime scope uses `strategy_id="*"`/`instrument_id="*"`, so STRATEGY/INSTRUMENT-level loss limits are silently ignored at runtime. `Metric.FRESHNESS_BUDGET_S` exists but freshness is a flat asset-class dict with a `DEFAULT` fallback (`engine.py:166-168`), not in the hierarchy as LIMIT_MATRIX states. Remedy: scope ids become composite (`tenant/account/strategy`); runtime evaluation iterates strategies with positions; freshness moves into the hierarchy or LIMIT_MATRIX is corrected.

- **F-14 — Medium — `services/risk/risk_engine/engine.py:193-201`.** Intent age is not budgeted; only `intent.market_ts <= now` is checked. An intent computed on data 10 minutes old passes if the market snapshot is fresh. Remedy: `RK-FRESH-INTENT-AGE` with a budget per asset class; also compare `intent.market_ts` with `market_snapshot.market_ts` (intent must not be newer than the snapshot it is judged against).

- **F-15 — Medium — `services/risk/risk_engine/engine.py:315-330`, `:57-61`.** MARKET orders bypass the collar entirely (PASS with value "market"); fat-finger protection then rests only on notional caps. `est_price` for STOP/STOP_LIMIT uses `reference_price`, not the stop, understating notional for far stops. Remedy: MARKET orders require `bid/ask` in the snapshot and a spread/impact bound (`RK-COLLAR-MKT`), else REQUIRES_HUMAN_APPROVAL; est_price = worst of (limit, stop, reference).

- **F-16 — Medium — `services/risk/risk_engine/engine.py:410-438, 463`.** `RK-ENVELOPE` when `capital_envelope is None` in BOUNDED_AUTONOMOUS is classified REQUIRES_HUMAN_APPROVAL. A misconfigured autonomous account silently degrades to supervised instead of halting; `promote()` prevents this state but `Account` can be edited directly (tests do). Remedy: undefined envelope in autonomous mode -> `RK-HALT-ENVELOPE` (HALT_CODES).

- **F-17 — Medium — `services/risk/risk_engine/engine.py:507-578`.** `decide()` is not wrapped: any internal exception (Decimal `InvalidOperation`, KeyError) propagates, so no `DecisionRecord` and no `risk.decided.v1` audit event are produced. The pipeline fails closed by accident (exception) but unrecorded, and the docstring's "never raises for domain reasons" is untested. Remedy: outermost `try/except` returning HALTED `RK-HALT-ERROR` with the exception class in `value`, plus an S1 alert; property test injecting NaN/Infinity/zero fields.

- **F-18 — Medium — `services/killswitch/killswitch_service/service.py:65, 110-111, 127-135`; `libs/core/rtcore/schemas/account.py:72-83`.** Kill-switch state is in-memory; non-ACCOUNT levels do not halt accounts, so a restart lifts PLATFORM/TENANT/STRATEGY/ASSET/VENUE switches without two-person deactivation, no post-incident review gate exists for PLATFORM/TENANT deactivation, and a pending first deactivation never expires. `flags_for(asset_classes=...)` (159) ignores its parameter. Remedy: durable store with fail-closed read (engine HALTs on unavailable/stale state, Objection 2); pending deactivation TTL; PIR reference required before deactivating PLATFORM/TENANT.

- **F-19 — Medium — RISK_POLICY.md evaluation-order claim vs `services/risk/risk_engine/engine.py:441-460, 548-550`.** The code evaluates every check unconditionally (no fail-fast), `_ne` (86-87) is never used and `NOT_EVALUATED` never appears. The "complete reason list" property holds (TC-RK-011), so this is a documentation defect, not a control defect; but RISK_POLICY sentence "fail-fast order ... all cheap checks still evaluated" must be corrected to "all checks always evaluated" (Committee-approved wording) so IVA does not test for a behaviour that does not exist.

- **F-20 — Low — `services/risk/risk_engine/engine.py:177, 180`; `libs/core/rtcore/clock.py:54-55`.** `age_seconds` returns `float`, converted through `str()`; deterministic for identical inputs but contradicts money.py's "floats never enter a decision". The global `decimal` context is not pinned inside `decide()`; a library changing precision changes results across replicas. `ENGINE_BUILD_HASH` (32-41) covers only `risk_engine/*.py`, not `rtcore.money/clock/ids` or pydantic. Remedy: integer microseconds; `decimal.localcontext()` with fixed precision/rounding; build hash over the lockfile plus rtcore.

- **F-21 — Low — `services/risk/risk_engine/monitors.py:65-74`.** Loss % uses current NAV as the base rather than start-of-period NAV; conservative (overstates the %) but undefined in LIMIT_MATRIX ("ccy or %"). Remedy: LIMIT_MATRIX to state the base explicitly (Chief Risk Agent action, Committee approval).

- **F-22 — Low — `services/risk/risk_engine/engine.py:387`.** `correlation_groups.items()` order comes from the snapshot builder; a builder that materialises the dict from a set would reorder `evaluated`, breaking `d1 == d2` across builders (TC-RK-001 only tests one builder). Remedy: iterate `sorted(groups)`.

- **F-23 — Low — LIMIT_MATRIX.md rows vs `Metric` enum.** The matrix lacks rows for `volatility_regime_pct`, `correlated_group_pct_nav` and any runtime-threshold metrics (slippage, rejection rate, latency), and lists "Freshness budget" in the hierarchy while the code keeps it flat (F-13). Chief Risk Agent action, to be approved by the Committee, not by the author.

- **F-24 — Low — `services/identity/identity_service/makerchecker.py:69-91`.** The cooling period applies equally to tightening and loosening a limit, so an emergency tightening waits one hour in the sim configuration. Policy ADR proposed in §5 (tighten immediately with two persons; loosen after cooling).

Positive observations, recorded for balance [Committee]: `decide()` is pure in the tested sense (TC-RK-001 replica check, Hypothesis property test, deterministic ids, ordered tuples not sets, Decimal end to end); `None` inputs HALT; undefined pre-trade limits fail closed (`RK-*-UNDEFINED`); tamper detection (`RK-INTEG`) raises S1; outcome precedence HALTED > REJECTED > REQUIRES_HUMAN_APPROVAL > APPROVED is implemented and property-tested; `-APPROVAL-UNDEFINED` correctly degrades to REJECTED; agents are denied on the Kill Switch with S1 alert and audit; two-person, different-line deactivation and restore are enforced with the same-person and same-line negative tests; every reason code carries value and threshold strings.

## 5. Compare — alternatives for the most important objection (and for the exposure/reduction policy)

### 5.1 Objection 1: making Kill Switch engagement fail-closed

| Option | Description | Pros | Cons | Chief Risk Agent view |
|---|---|---|---|---|
| A. Persist-first, best-effort hooks | Write `Activation(active=True, engaged=ENGAGING)` durably before any hook; each hook in `try/except`; results recorded; S1 alert on any failure; operator runbook completes manually | Smallest change; engine sees the flag immediately; failure is visible | Side effects may be partially done; needs runbook and retry | Minimum acceptable for Gate C |
| B. Two-phase saga | Phase 1 = durable flag + `halt_account` for every account in scope (all levels); Phase 2 = asynchronous saga for cancel/liquidate/revoke/evidence with retries and dead-letter; `engaged` moves to COMPLETE only when all steps succeed | Correct ordering ("block new risk" first) by construction; survives restarts; complete audit of each step | More moving parts; requires durable queue (ADR-005 bus already planned) | Preferred target design for Gate D/E |
| C. Engine-side dead-man's switch (complement) | Engine HALTs (`RK-HALT-KS-UNKNOWN`) when kill-switch state is absent or older than N s; Kill Switch service publishes heartbeats | Independent of the Kill Switch service's own correctness; also covers restart loss (F-18) | Introduces a liveness dependency: heartbeat outage halts trading (acceptable — fail closed) | Recommend combining C with A now and B later |

Recommendation [Committee, to be decided by the Backend Lead with IVA verification]: A + C for Gate C; B before Gate E.

### 5.2 Objection 3: open-order projection and the risk-reducing carve-out (policy ADR proposal; Chief Risk Agent may not approve it)

| Option | Description | Pros | Cons |
|---|---|---|---|
| A. Project open orders pessimistically | Add side-signed remaining notional of all open orders (any instrument) into `_projected_positions`; position cap includes open same-instrument quantity | Deterministic, pure, no OMS change; closes the cross-instrument split | Double counts when orders will not all fill; TOCTOU window remains between decision and snapshot update |
| B. Per-account exposure reservation in OMS | Decision returns `reserved_exposure`; OMS reserves it atomically per account until fill/cancel; snapshot carries reservations | Closes the TOCTOU window; exact | Stateful; needs lease/fencing like the executor; more code in the control plane |
| C. Serialise decisions per account | One in-flight decision per account (queue) | Simplest correctness argument | Latency under burst; does not solve unfilled-order accumulation without A |

Risk-reducing rule (RISK_POLICY change proposal, tagged [Committee], approval by Trading Risk Committee with IVA): "For closing sides (SELL against long, BUY_TO_COVER against short), controls #6-9 and #16 PASS when the projected metric is strictly lower than the current metric; all other controls apply unchanged; the decision record carries `RK-REDUCING` as an informational code." Alternative: keep strict limits and rely on the liquidation policy — rejected by the reviewer because O-08 is open until Gate E and CANCEL_ONLY leaves no engine path to reduce risk.

## 6. Control quartet gaps (per critical control considered under-tested)

| Control | Positive | Negative | Abuse | Recovery | Gap (to add) |
|---|---|---|---|---|---|
| Kill Switch engagement (P4) | TC-KS-001, -005 | TC-KS-003 | TC-KS-002 (agent) | TC-KS-004 | Abuse/Recovery: hook raises -> activation persisted, flags set, S1 alert (TC-KS-007); restart of service -> non-ACCOUNT activations survive (TC-KS-008); concurrent intent during activation -> HALTED (TC-KS-009); PLATFORM/TENANT deactivation requires PIR ref (TC-KS-010) |
| Runtime monitors -> halt | TC-RK-016 (events exist), TC-KS-006 (RT-LOSS-DAILY only) | none | none | none | Negative: undefined loss/drawdown limit -> halt not silence; Positive for each of the 10 codes that the resulting flag actually blocks the next intent (drift, venue currently do not); Abuse: monitor starved (no heartbeat) -> autonomy suspended; Recovery: monitor restart re-evaluates and re-engages |
| Exposure/concentration/leverage (#6-9) | implicit in TC-RK-001 | TC-RK-010 (single breach each) | TC-RK-010 RK-CAP-AGG (same instrument only) | none | Abuse: N orders across N instruments each within caps, sum over gross/concentration -> REJECTED; Negative: negative/zero NAV; Positive: value arithmetic asserted numerically (currently only code presence); Recovery: risk-reducing order accepted when over limit (after policy ADR) |
| Fail closed on inputs (contract) | TC-RK-004, property test | same | TC-RK-003 (tamper) | TC-RK-004 | Negative: stale account snapshot -> RK-FRESH-ACCOUNT; kill-switch state unknown -> HALTED; tenant mismatch; approval-time snapshot missing -> HALTED not LIVE (pipeline) |
| Limit change maker-checker/cooling | TC-ID-* (primitive) | TC-ID-* | none for limits specifically | none | Positive: EFFECTIVE change produces new signed policy version consumed by engine; Negative: unsigned/tampered policy -> RK-HALT-POLICY; Abuse: 3rd-line or agent checker denied at service layer; MCP tool cannot reach any limit write; Recovery: rollback to previous policy version with audit |
| Emergency/liquidation policy (O-08) | fallback test (unnamed) | none | none | none | Abuse: arbitrary `liquidation_policy_ref` string -> no liquidation; Negative: reduce/flatten disabled while O-08 open; Positive (post O-08): approved ref resolves to versioned policy; Recovery: partial liquidation failure recorded |
| Mode restore after halt | TC-KS-004 (explicit PAPER) | TC-KS-003 | none | TC-KS-004 | Abuse: default-target restore above pre-halt mode denied; agent with human role cannot halt/set status |
| Protective stop (#15) | TC-RK-010 (present) | TC-RK-010 (missing, wrong side) | none | n/a | Abuse: stop at 0.01 (unbounded loss) -> fail once RK-PROT-DIST exists |
| Duplicate (#11) | TC-RK-015 (replay) | — | replay only | — | Abuse: economic duplicate with new intent id |

All new test IDs are proposals; the Backend Lead assigns final IDs in docs/TEST_CASES and IVA confirms coverage.

## 7. RTM rows to add or correct

| Req | Architecture element | Implementation owner | Control | Test IDs (quartet) | Evidence | Gate | Status |
|---|---|---|---|---|---|---|---|
| FR-11 (correct) | Risk service `decide()` | Backend Lead | Deterministic decision, fail closed on missing AND stale inputs; decision time is an explicit input | TC-RK-001..004, TC-RK-010..016, TC-RK-017 (account staleness), TC-RK-018 (tenant), property suite | determinism report + this review | C | Proposed — corrects existing row; not started |
| FR-11a (new) | Risk service exposure projection | Backend Lead | Open orders and reservations projected into #6-9/#16; risk-reducing rule | TC-RK-019 (split across instruments), TC-RK-020 (reducing order), TC-RK-021 (negative NAV) | decision records in evidence bundle | C | Proposed — new row; not started |
| FR-11b (new) | Risk service pre-trade loss/drawdown | Backend Lead | RK-LOSS-*/RK-DRAWDOWN pre-trade mirror of runtime controls | TC-RK-022 | — | C | Proposed — new row; not started |
| FR-17a (new) | Runtime monitors -> Kill Switch | Backend Lead / SRE Lead | Every runtime code produces a blocking activation with concrete target; undefined limit fails closed; heartbeat dead-man's switch | TC-RK-016 (extend), TC-KS-006 (parametrise over 10 codes), TC-OB-00x (heartbeat) | monitor drill log | C | Proposed — new row; not started |
| FR-17 (correct) | Kill Switch service | Backend Lead | Persist-first engagement; per-hook failure recorded; two-person restore; durable state | TC-KS-001..006, TC-KS-007..010 | drill evidence incl. hook-failure drill | C | Proposed — corrects existing row; not started |
| FR-17b (new) | Emergency/liquidation policy | Backend Lead (code), Trading Risk Committee (policy) | Reduce/flatten disabled until O-08; approved-policy registry lookup | TC-KS-011 | O-08 decision pack | E (disabled state evidenced at C) | Proposed — new row; not started |
| FR-01a (new) | Limit/policy change control | Backend Lead (code), Chief Risk Agent (policy owner, not approver) | Signed policy artefact; MakerChecker is sole writer; role checks in service; tighten-now/loosen-after-cooling | TC-ID-00x (limits), TC-RK-023 (unsigned policy -> HALT) | LIMIT_MATRIX change log | C | Proposed — new row; not started |
| FR-12a (new) | OMS approval execution path | Backend Lead | Re-decision at approval; missing snapshot -> HALTED; explicit execution-target allowlist gated by `environment_tag`/`approved_for_production` | TC-AP-00x, TC-EX-00x | approval logs | C | Proposed — new row; not started |
| FR-01b (new) | Account state machine | Backend Lead | Authorised-human-only status/halt; restore never above pre-halt mode | TC-ID-00x | audit chain | C | Proposed — new row; not started |

## 8. RAID entries to open

| ID (proposed) | Type | Item | Owner | Needed by | Status |
|---|---|---|---|---|---|
| R-09 | Risk | Kill Switch engagement not fail-closed (hooks before state; exception leaves switch un-engaged; in-memory state) — Objection 1, F-18 | Backend Lead (fix), IVA (verify) | Gate C | Open |
| R-10 | Risk | Fail-open defaults on execution path (approval with missing snapshot -> LIVE; TARGET_FOR_MODE default LIVE; kill-switch state cannot express unknown; account staleness unchecked) — Objection 2 | Backend Lead | Gate C | Open |
| R-11 | Risk | Cross-instrument order splitting evades gross/concentration/leverage/correlated limits; no reservation between decision and fill — Objection 3 | Backend Lead, Integration Architect (links R-02) | Gate C | Open |
| R-12 | Risk | RT-DRIFT and RT-VENUE halts block nothing ("*" targets); runtime loss/drawdown fail open when limits undefined; hard-coded RuntimeThresholds — Objection 3, F-05 | Backend Lead, SRE Lead | Gate C | Open |
| R-13 | Risk | Liquidation path executable with any non-empty `liquidation_policy_ref`; emergency policy fields not under maker-checker — F-01 | Backend Lead; Trading Risk Committee (O-08) | Gate C (disable), Gate E (enable) | Open |
| R-14 | Risk | Halt/restore cycle promotes PAPER -> SUPERVISED without Gate D; agent can set trading status and halt — F-02, F-03 | Backend Lead | Gate C | Open |
| R-15 | Risk | Limit maker-checker disconnected from policy store; unsigned YAML is the real write path; `approved_for_production`/`environment_tag`/`cooling_period_end` unenforced — F-04 | Backend Lead (code), MCP Security Agent (signing), Chief Risk Agent (change log) | Gate C | Open |
| D-01 | Decision | Risk-reducing order rule and open-order projection semantics (RISK_POLICY change; §5.2) | Trading Risk Committee (Chief Risk Agent proposes, does not approve) | Gate C | Open |
| D-02 | Decision | Decision contract to include decision time; correct "fail-fast" wording; LIMIT_MATRIX rows for volatility, correlated group, runtime thresholds, loss-% base, freshness placement — F-06, F-19, F-21, F-23 | Trading Risk Committee | Gate C | Open |
| D-03 | Decision | Cooling period asymmetry: tighten immediately (two persons), loosen after cooling — F-24 | Trading Risk Committee | Gate C | Open |
| A-01 | Assumption | Gate C authorises PAPER only; findings rated Critical for live capital are treated as Gate C blockers because the same code path serves LIVE by default (Objection 2) | Program Orchestrator | Gate C | Open |
| R-07 (existing) | Risk | Sim fixture values mistaken for thresholds — this review adds: `approved_for_production` is consumed by no code path today (F-04), so the guard named in R-07 is not yet a guard | Chief Risk Agent, Backend Lead | Gate C | Open |
| O-22 (existing) | Decision | Extend asymmetric signing to the risk policy artefact (F-04, R-15) | Security Architect, MCP Security Agent | Gate B/C | Open |
| O-07 (existing) | Gap | Every numeric value in sim-policy-v0.1.yaml and RuntimeThresholds remains a fixture; this review takes no position on any number | Trading Risk Committee | Gate C | Open |
| O-08 (existing) | Gap | Add condition: reduce/flatten must be hard-disabled in code until closed (R-13) | Trading Risk Committee | Gate E | Open |
| O-19 (existing) | Gap | Named deputies: KILL_SWITCH_ACTIVATORS in `rtcore/lines.py:149-158` includes RUNTIME_MONITOR but no deputy roles; document before Gate C | Program Orchestrator | Gate C | Open |

ID note [Committee]: proposed IDs R-09..R-15 and D-01..D-03 follow the RAID_LOG state as of 2026-09-07 (R-05..R-08 and O-20..O-25 were added concurrently by other sessions); the Program Orchestrator assigns final IDs.

Assumptions: the sim platform (`build_sim_platform`) is representative of the deployment wiring for hook order and snapshot construction [Committee]; distributed race conditions were reasoned about, not executed (single-process sim) [Open].

## 9. Verdict

**RECOMMEND REJECT for Gate C entry in the current state** — resubmission expected to reach ACCEPT WITH CONDITIONS once R-09, R-10, R-11, R-12, R-13 (disable path), R-14 and R-15 are closed with IVA-verified quartet tests, and D-01/D-02 are decided by the Trading Risk Committee.

Rationale [Committee]: the deterministic core is sound and well tested, but the fail-closed property that blueprint 05 makes non-negotiable is violated at three places that sit outside `decide()` yet on the path to real orders: Kill Switch engagement (Objection 1), the approval-to-execution path (Objection 2) and runtime halts that do not block (Objection 3). Two of the ten runtime controls are no-ops today; that alone contradicts the RTM row FR-17 "drill evidence". Rejecting now costs a remediation cycle; accepting would carry a Kill Switch that may not engage into paper trading, where drills are supposed to prove it does.

Conditions for resubmission (all must be evidenced, none self-certified):
1. Persist-first Kill Switch with per-hook failure recording and engine-side unknown-state HALT (R-09); TC-KS-007..010 green and reviewed by IVA.
2. Approval path re-decides and fails closed; execution target allowlist gated by policy environment (R-10).
3. Open orders projected into exposure; risk-reducing rule decided by the Committee and implemented (R-11, D-01).
4. All ten runtime codes proven to block the next intent; undefined runtime limits fail closed; thresholds sourced from policy (R-12).
5. Reduce/flatten disabled until O-08; account emergency fields under maker-checker (R-13).
6. Restore never above pre-halt mode; status/halt authorisation fixed (R-14).
7. Signed policy artefact consumed by the engine; MakerChecker is the only writer (R-15).

Confidence: **high** on the existence and reproducibility of every finding (each is tied to a file:line and, where marked, to a probe in Appendix A that was executed on 2026-09-07 against the current tree); **medium** on severity calibration relative to Gate C scope (paper), stated in A-01. Numeric thresholds: no position taken [Open: O-07, O-03].

Provenance: sources read and executed are listed in §2; test run `55 passed`; probes are reproducible from the code in Appendix A using the `pythonpath` entries in `pyproject.toml`. No repository file other than this document was created or modified by the reviewer.

---

## Appendix A — Adversarial probes executed (read-only, sim platform, 2026-09-07)

| Probe | Setup | Observed | Finding |
|---|---|---|---|
| P1 | NAV = -1000 | gross/net/single-name = -990.6 PASS; only RK-LEV (Infinity) fails | F-07 |
| P2 | account `as_of` = now - 1 day | APPROVED, no reason code | Objection 2 |
| P3 | NAV 100k; four open BUY orders 40k each on other instruments; new BUY | gross 9.9% of NAV; APPROVED | Objection 3 |
| P4 | position 300% of NAV; SELL 100 (reducing) | REJECTED: RK-CAP-POS, RK-EXP, RK-EXP-NET, RK-CONC, RK-CONC-CCY, RK-LEV, RK-CORR | Objection 3 |
| P5 | snapshot tenant != intent tenant | APPROVED | Objection 2 |
| P6 | same inputs, `now` + 1 h | same decision_id; APPROVED -> REJECTED (RK-EXPIRED, RK-FRESH) | F-06 |
| P7 | PAPER account halted; two-person restore with default target | mode = SUPERVISED | F-02 |
| P8 / P8b | AGENT calls `set_trading_status`; AGENT with RISK_OFFICER role calls `halt` | both accepted | F-03 |
| P9 | `cancel_open_orders` hook raises | exception; `active() == ()`; `blocks() False`; no audit | Objection 1 |
| P10 | `emergency_policy_for` returns (CANCEL_AND_FLATTEN, "garbage-ref") | `apply_liquidation` executed; recorded as `CANCEL_AND_FLATTEN:garbage-ref` | F-01 |
| P11 | RT-DRIFT + RT-VENUE fire via `evaluate_monitors` | flags `strategies=('*',)`, `venues=('*',)`; next intent APPROVED | Objection 3 |
| P12 | daily-loss/drawdown limits removed; 90% loss | zero HALT events | Objection 3 |
| P13 | `TARGET_FOR_MODE.get(mode, LIVE)` for SUPERVISED/BOUNDED/HALTED/OBSERVE | LIVE for all | Objection 2 |
| P14 | daily_pnl = -50% NAV, monitor not run | APPROVED | Objection 3 |
| P15 | protective_stop = 0.01 on ~99 entry | PASS | F-09 |
| P16 | SELL_SHORT, buying_power = 0, shortable instrument | APPROVED; buying_power PASS | F-10 |
| P17 | economically identical intent, new intent_id | no RK-DUP; APPROVED | F-11 |
| P18 | SUPERVISED account | REQUIRES_HUMAN_APPROVAL with approval id (expected) | — |
| P19 | PM proposes limit, AUDITOR checks, cooling elapsed | EFFECTIVE; policy unchanged; version unchanged | F-04 |
| P20 | STRATEGY limit, different tenant/account | 50k applies | F-13 |
| P21 | venue session HALTED | REJECTED RK-SESS (expected) | — |
| P22 | `age_seconds` return type | float | F-20 |

Probe harness (for IVA reproduction): `PYTHONPATH=<pyproject pythonpath> python3 -c "from web_bff.platform import build_sim_platform, ...; ..."` — the exact statements are the ones described per row; no repository file was modified.
