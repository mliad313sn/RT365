# IVA Re-validation of remediation commit 0cbc895 (head c0bb1fb) — 2026-09-07

Author: Independent Validation Agent (3rd line) [Source: 13]. This is a re-validation of the build-defect findings of GATE_B_2026-09-07.md and GATE_C_2026-09-07.md (written against `09a6e71`) against the builder's remediation commit `0cbc895` ("Remediate IVA cycle-1 build defects: gateway authorisation and permission oracle"); the validated head is `c0bb1fb`, which adds documentation only on top of `0cbc895` [Verified: `git log --oneline -5`; `git show --stat 0cbc895`]. Every verdict below is a recommendation to the Committee; the human approver of record is pending; all evidence was produced in dev/sim on a simulated broker and authorises no promotion beyond the environment it was produced in [Source: 00, 12]. Nothing in this report implies production readiness, regulatory permission, data licensing, broker functionality, market access or profitability.

Method: the IVA did not build the change, does not fix it, and did not rely on the builder's tests for any verdict. Three adversarial probe scripts (p1_gateway.py: 54 cases; p2_controls.py: 49 cases; p3_followup.py: 8 cases) were written and executed by the IVA against the head, kept outside the repository, and their outputs are quoted below as [Verified: pN <case>]. The builder's tests were read only to confirm the claimed identifiers exist. Findings are tagged [Verified: …] where the IVA executed or read the evidence, [Source: NN] for blueprint requirements, [Committee] for committee derivations and [Open] for unresolved items. Working tree was clean before and after every run [Verified: `git status --porcelain` empty before/after].

## 1. Mechanised checks (head c0bb1fb, RT_ENV=sim)

| Check | Command | Result |
|---|---|---|
| Full test suite | `python -m pytest -q` | **147 passed**, 0 failed (2 deprecation warnings from starlette/anyio) [Verified] |
| Lint | `ruff check .` ; `ruff format --check .` | All checks passed; 119 files already formatted [Verified] |
| Typecheck | `python -m mypy libs services mcp connectors observability apps` | Success: no issues in 90 source files [Verified] |
| Schema drift | `python scripts/export_event_schemas.py --check` | OK: 21 event schemas match the models (order.command.v1 now carries `authorisation`) [Verified] |
| Network-policy invariants | `python scripts/check_network_policies.py` | OK: network policies satisfy plane invariants (TC-NET) [Verified] |
| Registry verify (sim) | `python scripts/verify_tool_registry.py` | OK: registry 0.1.0 (dev key), 6 tools, policies consistent; NOTE registry is a sim FIXTURE [Verified] |
| Registry verify (production) | `python scripts/verify_tool_registry.py --production` | FAIL (expected, fail closed): "no RT_MCP_REGISTRY_KEY configured and RT_ENV='production' is not a dev/sim environment; refusing the dev key" [Verified] |
| Secret scan | `python scripts/secret_scan.py` | OK: 363 files, no findings [Verified] |
| Claimed test identifiers present | `grep -rhoE "TC-(EX-009\|RK-021\|AP-005\|ID-005\|AI-011\|E2E-AUTH)" test/` | All six identifiers present in test/quartets and test/e2e [Verified] |
| Governance rows present | grep of docs/ | R-36..R-40, D-028..D-031, T-38..T-43, O-53..O-56 present; ADR-015 exists with **Status: Proposed** [Verified] |

`make evidence` was deliberately not run: it rewrites files outside docs/GATE_REPORTS/, which the IVA may not touch.

## 2. Re-execution of the cycle-1 findings

### V-C1 — Kill Switch / halt did not supersede an already-authorised command at the gateway (GATE_C veto ground; GATE_B IVA-01)

Attack model reproduced from cycle 1: a command that the pipeline has already authorised and signed is captured before the gateway sees it (the IVA wrapped the pipeline's `sign_command` hook to keep the signed `OrderCommand` and abort — this is exactly what a bus delivery pending during a Kill Switch looks like), the switch is thrown by a human SRE, and one second later an executor named `executor-restarted` re-acquires the account lease and submits the captured command inside the Control plane.

| Case | Observed | [Verified] |
|---|---|---|
| Baseline: captured signed command with nothing blocking | ACCEPTED, ACKNOWLEDGED, broker submissions +1 (proves the capture is a valid authorised command) | p1 BASE-1 |
| ACCOUNT Kill Switch, re-acquired lease | `ExecutionBlocked: kill switch engaged for this scope`, broker +0 | p1 V-C1 ACCOUNT |
| STRATEGY / ASSET (instrument) / ASSET (asset class EQUITY) / VENUE / TENANT / PLATFORM levels | all `ExecutionBlocked`, broker +0 | p1 V-C1 ×6 |
| Account HALTED by a human risk officer, no Kill Switch | `ExecutionBlocked: account HALTED/ACTIVE`, broker +0 | p1 V-C1 HALTED |
| `trading_status` SUSPENDED / CLOSED | `ExecutionBlocked: account PAPER/SUSPENDED`, `…/CLOSED`, broker +0 | p1 V-C1 SUSPENDED, CLOSED |
| Retry path: broker down at submit (order SUBMITTED), ACCOUNT switch thrown, broker back, `retry_submit` with a fresh lease | order already CANCELLED by the switch's cancel hook; retry returns CANCELLED, broker +0 | p1 V-C1 retry |
| Retry path variant where the broker was **down during the switch** (ack lost, cancel hook failed) | order adopted as ACKNOWLEDGED and left OPEN at the broker under an active ACCOUNT switch — **new finding IVA-19** (§4) | p1 N5 |

Reading `gateway.py`: `_assert_executable` is called at `submit()` after the fencing check (line 222, last gate before the adapter) and at `retry_submit()` only on the `not status.known` branch (line 306); the oracle in `platform.py` lines 626-660 applies Kill Switch > halt/status > tenant > target/mode > decision provenance and is injected from the composition root; a gateway constructed without the oracle refuses everything ("no execution permission oracle configured (fail closed)") [Verified: p1 "verify only"].

**Verdict: CLOSED (dev/sim)** for the reported scenario at every Kill Switch level, for halt and for non-ACTIVE status, at submit and at the unknown-order retry path. Residual: IVA-19 (retry adoption of a broker-known order skips the oracle and does not cancel) touches the same non-negotiable and is opened as a new finding; it is narrower than V-C1 (requires the cancel hook to have failed) but must be closed before Gate C is reconvened [Committee].

### V-C2 — Gateway submitted commands it could not prove were authorised (GATE_C veto ground; GATE_B IVA-02)

| Case | Observed | [Verified] |
|---|---|---|
| Forged command (no MAC, `decision_id="dec_forged"`, `authorised_by="FORGED"`) from a caller inside the Control plane with a valid lease | `CommandNotAuthorised: command carries no control-plane authorisation`, broker +0 | p1 V-C2 forged |
| Forged decision_id with a bogus 64-hex MAC | `CommandNotAuthorised: command authorisation invalid` | p1 |
| Signed command with `quantity` ×10 (MAC kept) | refused | p1 altered |
| Command B carrying the decision_id of intent A (MAC kept) | refused at the MAC layer | p1 |
| Same, re-signed with the pipeline's key (white-box test of the oracle alone) | `ExecutionBlocked: decision does not belong to this intent/policy version` | p1 oracle layer |
| Replay of a live signed command with a new idempotency key | refused at the MAC layer (key is bound) | p1 replay |
| Replay of the identical signed command while the first order is live | idempotency dedupe returns the existing record, broker +0 | p1 |
| Re-signed replay with a new key while the first order is live | `DuplicateIntentOrder` (per-intent invariant) | p1 |
| Crafted `ApprovalRecord` for a **DECLINED** approval fed to `pipeline.on_approval` (the pipeline signs it) | `ExecutionBlocked: approval record does not authorise this decision`, broker +0 | p1 DECLINED |
| Crafted record for an **EXPIRED** approval | refused on re-decision (`RK-EXPIRED`, `RK-FRESH`), broker +0 | p1 EXPIRED |
| Crafted record for a **PENDING** (never approved) approval | `ExecutionBlocked: approval record does not authorise this decision` | p1 PENDING |
| Gateway constructed with no hooks / verify only / oracle only | fail closed in all three (`no command authoriser configured`, `no execution permission oracle configured`) | p1 ×3 |
| Every one of the 22 non-MAC `OrderCommand` fields mutated one at a time (incl. `approval_id` None→value, `limit_price`/`stop_price` None→value, `authorised_at` +1 s, `execution_target`) | all 22 refused; no field of the model is outside the digest | p1 N2 |
| Command signed by a BACKTEST throwaway platform submitted to the live platform's gateway, and the reverse | both refused; the two platforms hold different keys | p1 N7 |

**Verdict: CLOSED (dev/sim)** for forgery, alteration, cross-intent decisions, replay with a new key, and approval-record misuse. Residual design weaknesses of the shared-HMAC mechanism are opened as new findings IVA-20 (digest non-injective), IVA-21 (authorisation not one-shot and unbounded in time) and IVA-22 (signer reachable by introspection); O-53 (asymmetric key, HSM) remains [Open].

### IVA-03 — `max_position_per_instrument` ignored open orders

Probed by calling `risk_engine.engine.decide` on synthetic `AccountSnapshot`s (positions and open orders set directly) and reading the `max_position_per_instrument` evaluated check, which isolates the check from the other 15 families. Cap = 2,000,000 ccy (sim policy platform level); est_price is the engine's reference price.

| Book | Order | Position check | [Verified] |
|---|---|---|---|
| flat + resting BUY at cap | BUY at cap | FAIL (value 4,000,042 vs 2,000,000) — the cycle-1 evasion no longer passes | p2 |
| long 1000 + resting SELL 1000 | SELL 1500 | value = 1500 × price (true −150 % projection now measured) | p2 |
| long 1000 + resting SELL 1000 | SELL cap+1000 | FAIL | p2 |
| flat + resting BUY half-cap | BUY half-cap + 1 | FAIL | p2 |
| long 100 | SELL cap+100 (flip to short over cap) | FAIL | p2 |
| long over cap (cap+5000) | SELL 1000 (true risk-reducing) | PASS via exemption "risk-reducing: 2,495,321 → 2,396,261" | p2 |
| long over cap + resting SELL 1000 | SELL 1000 | PASS (exemption; `current` now uses the committed quantity) | p2 |

One probe row ("exactly at cap") reported FAIL only because the IVA sized the order from `last_price` while the check uses the reference price (2,000,021 > 2,000,000); it is not a defect. `is_risk_reducing` still compares against positions only, not the committed book; the exemption remains bounded by `value <= current` so it cannot grow exposure [Verified: engine.py lines 76-83, 119-135].

**Verdict: CLOSED (dev/sim).**

### IVA-04 — strategy owner could approve their own strategy's intent

`ApprovalItem.strategy_owner_id` is now populated (`quant.fixture`) from the strategy registry; the owner acting as PORTFOLIO_MANAGER, RISK_OFFICER or TRADER is refused ("approver must differ from the maker/strategy owner"), the item stays PENDING, an independent RISK_OFFICER then approves (control), and owner-as-maker-and-approver is refused [Verified: p2 IVA-04 ×7]. `strategy_owner()` returns None for an unregistered strategy/version, leaving only the maker rule; the pipeline never signs for an unregistered strategy (it is REJECTED at risk) [Verified: p3 N3b strategy_id].

**Verdict: CLOSED (dev/sim).**

### IVA-05 — `MakerChecker.reject()` accepted an AGENT actor

AGENT reject and an AGENT spoofing a 2nd-line role are refused ("only humans may reject controlled changes"); the change stays PENDING; rejecting a CHECKED change is refused ("is CHECKED") [Verified: p2 IVA-05 ×5]. Observation: the maker may reject their own pending change (a withdrawal) — acceptable [Committee].

**Verdict: CLOSED (dev/sim).**

### IVA-06 — BFF header auth fail-open when `RT_ENV` unset

`create_app()` executed in a subprocess per value: unset, empty string, `SIM`, `"sim "`, `" sim"`, `paper` → `RuntimeError: RT_ENV is not 'sim' …` (refuses to start); exactly `sim` → starts [Verified: p2 IVA-06 ×7; app.py line 44]. Header-asserted principals themselves remain the sim-only mechanism (R-06 open) — unchanged by design.

**Verdict: CLOSED (dev/sim)** for the fail-open default; R-06 (IdP/MFA) remains [Open].

### IVA-07 — dev registry key not black-listed

A production-tagged non-fixture registry signed with the published dev key was loaded with the key supplied (a) via `RT_MCP_REGISTRY_KEY` and (b) via `load_registry(key=)`, under `RT_ENV` = production, paper, dev, sim and unset: all ten combinations refused (black-list message outside dev/sim; environment-tag mismatch inside dev/sim); the shipped sim fixture via `key=DEV_KEY` in paper is refused [Verified: p2 IVA-07 ×11]. O-22 stands: any other key string configured as `RT_MCP_REGISTRY_KEY` self-signs a production registry with `dev_key_in_use=False` (symmetric HMAC) [Verified: p2 IVA-07 O-22].

**Verdict: CLOSED (dev/sim)** for the dev-key deny-list; O-22 asymmetric/KMS signing remains [Open].

### IVA-08 — nonce store process-local, lost on restart

The mechanism works in isolation: same-process replay refused; replay across an issuer restart with the JSONL journal reloaded and the identity `adopt()`ed refused; nonce reuse under a re-issued token for the same agent refused (nonces now keyed per agent); restart without adopt refuses as unknown identity [Verified: p2 IVA-08 ×4]. Two gaps: (1) **the sim composition root does not wire the journal** — `build_sim_platform` constructs `IdentityIssuer(revocations=…, audit=…)` with `nonce_path=None`, so the running platform is still process-local exactly as in cycle 1 [Verified: platform.py line 706; p2 "nonce_path=None"]; (2) the journal is never pruned by the 60 s replay window and the loader reloads every historical nonce (unbounded growth; O-55). No shared store across replicas (R-05).

**Verdict: PARTIALLY CLOSED.** Remaining: wire `nonce_path` in the composition root; bound the journal by `CALL_MAX_AGE`; replicated store before more than one runtime process exists (paper).

### IVA-09 — audit chain anchored in-process only

No change to the audit service between `09a6e71` and head (`git diff --stat 09a6e71..HEAD -- services/audit libs/core/rtcore` shows only the unrelated `order.py` addition) [Verified: p2 IVA-09]. The builder did not claim a fix; it is recorded as O-54 in RAID_LOG ("External anchoring of the audit ChainHead … needed before Gate C") [Verified].

**Verdict: NOT CLOSED (not claimed; documented O-54).** Remains a Gate C condition.

## 3. New attacks on the new mechanism

| # | Attack | Result | [Verified] |
|---|---|---|---|
| N1 | Reach the authorisation key from an MCP tool handler, `platform.runtime`, SimPlatform fields or module globals by attribute walk | No module-global key or authoriser. **From `platform.runtime` (the MCP `ToolRuntime`) a `CommandAuthoriser` with a working `sign()` is reachable in ten hops**: `runtime._alert → AlertRouter.actions['suspend_signals'] closure → platform → killswitch.hooks.evidence_snapshot closure → gateway → _verify_command.__self__`. The holder re-signed an altered command (quantity 999) and the gateway ACKNOWLEDGED it. Not reachable from tool-handler closures directly; reachable via the alert router. → IVA-22 | p1 N1; deep-walk depth 14 |
| N2 | Digest coverage: mutate each field one at a time | All 22 fields covered; none uncovered | p1 N2 |
| N3 | `model_copy` equivalence classes: `Decimal("100.0")`, `side` as plain str, naive `authorised_at`, same instant in +01:00, `execution_target` as str | Decimal "100.0", naive datetime and +01:00 forms are refused (digest differs — fail-safe over-refusal, not a bypass); enum-vs-str forms produce the identical digest and are semantically identical (benign) | p1 N3 |
| N3b | Digest injectivity: `"|".join(f"{k}={v}")` over sorted keys | **Two different commands share a digest and a MAC**: `account_id="acct-A|approval_id=P", approval_id="Q"` vs `account_id="acct-A", approval_id="P|approval_id=Q"`; likewise `correlation_id`/`decision_id` and `strategy_id`/`tenant_id` boundaries; the MAC of the first verifies the second. Reachability: the intent queue accepts `|`/`=` in agent-supplied `strategy_id` and `account_id`; the pipeline REJECTS the unregistered strategy before signing and raises an unhandled `KeyError` for the unknown account. → IVA-20 (design), IVA-24 (robustness) | p1 N3b; p3 |
| N4 | Oracle: `execution_target` LIVE (and SIM) for a PAPER account; unknown decision; tenant mismatch; approval_id on an APPROVED decision; unknown account; 30-day-old `authorised_at` | LIVE and SIM refused ("does not match account mode PAPER"); unknown decision, tenant mismatch and stray approval_id refused; unknown account raises `KeyError` (fail closed by exception, no audit row); **30-day-old authorisation is PERMITTED by the oracle** (only the MAC binds the timestamp) → IVA-21 | p1 N4 |
| N5 | `retry_submit` when `query_order` reports the order as known, after an ACCOUNT Kill Switch whose cancel hook failed (broker down during the switch, ack of the original submit lost) | Gateway state SUBMITTED→ACKNOWLEDGED, broker status OPEN, `hook_failures=['cancel_open_orders: BrokerUnavailable']`, no oracle call, no cancel: a live broker order under an active ACCOUNT Kill Switch → IVA-19 | p1 N5 |
| N6 | Per-intent invariant bypass: KS-cancelled signed command resubmitted after the switch is lifted (two-person) and the halt restored (two-person) | Same gateway: idempotency dedupe returns the CANCELLED record, broker +0. **Across a gateway restart (in-memory dedupe lost, same oracle/decision store): ACCEPTED and ACKNOWLEDGED, broker +1, and again three days later** — no re-decision, intent tracker not consulted → IVA-21 | p1 N6; p3 N6-restart, +3d |
| N7 | BACKTEST throwaway platform's authoriser signs for the live platform | Refused both directions; keys differ | p1 N7 |
| N8 | Idempotency dedupe precedes authentication | An unauthenticated command carrying a live idempotency key receives the full existing `OrderRecord` and is audited as `duplicate_ignored`, not `unauthorised`; no broker effect → IVA-25 | p1 N8 |
| Obs | Alert auto-action on `execution.unauthorised_command` | Any forged command throws the ACCOUNT Kill Switch on the **attacker-chosen `account_id`** (a non-existent `acct-victim` produced an activation; the real account was HALTED and a subsequent legitimate intent was HALTED); activation recorded under synthetic actor `risk-officer.system` with role `risk_officer` → IVA-23 | p1 NEW-OBS ×2; p3 |
| Obs | Kill Switch cancel hook raising while the broker is down | `cancel_open` preempts the lease as `killswitch` and the exception exits before the release loop: the lease stays held for the 30 s TTL (fail-safe) and the intent tracker is not synced to CANCELLED (shows ACKNOWLEDGED) | p1 N5 trace; p3 |

## 4. New findings

| ID | Severity (dev/sim → bus topology) | Finding | Evidence | Proposed control | Owner (RACI) |
|---|---|---|---|---|---|
| IVA-19 | **High** | `retry_submit` adopts a broker-known OPEN/PARTIAL order as ACKNOWLEDGED without consulting the permission oracle and without cancelling; when the Kill Switch's cancel hook failed (broker outage during activation, ack lost) the order is left live at the broker under an active ACCOUNT switch. Same non-negotiable as V-C1 [Source: 00]. | p1 N5; gateway.py lines 293-298 | After adopting a known live order in `retry_submit`, call `_assert_executable`; if blocked, cancel at the broker and record `order.cancelled.v1` (KS supersedes). `KillSwitchService` must re-drive a failed `cancel_open_orders` hook until the broker confirms (hook_failed alert already S1); reconciliation rule "open order inside an active Kill Switch scope" as an S1 break. Quartet abuse/recovery tests for the ack-lost + outage race. | Backend Lead / Trading Domain Lead; 2nd line Chief Risk Agent |
| IVA-20 | **Medium** (design) | `OrderCommand.authorised_digest()` is not injective: `"|".join(k=v)` lets a value containing `|k2=` absorb the next field, so two different commands share one MAC. Exploitable only if the pipeline can be made to sign an identifier containing `|`/`=`; today identifiers must exist in registries, so exploitability is low, but the canonical form must be injective by construction. | p1 N3b (three collisions, cross-verified MAC) | Canonical JSON (sorted keys, no whitespace, explicit types) or length-prefixed encoding for the digest; identifier character whitelist in the intent/command schemas; fixed test vectors in the contract tests. Part of O-53. | Integration Architect; 2nd line Security Architect |
| IVA-21 | **Medium** in single-process sim → **High** on the ADR-005 bus/restart topology | Authorisation is neither one-shot nor time-bounded: the oracle does not check `authorised_at` freshness, intent lifecycle state, or whether the decision was already consumed; the only replay defence is the gateway's in-memory idempotency map. A Kill-Switch-cancelled signed command replayed after the switch was lifted and the halt restored was executed across a gateway restart, and again three days later, with no re-decision. | p3 N6-restart, N6-restart+3d; p1 N4 30-day case | Oracle to require `now - authorised_at <= policy window` (e.g. 60 s), intent tracker state == AUTHORISED (never CANCELLED/terminal), and one-shot consumption of the decision record persisted with the inbox (ADR-003); post-Kill-Switch resumption only via pipeline re-decision, never replay. | Backend Lead; 2nd line Chief Risk Agent |
| IVA-22 | **Medium** (single-process dev/sim; mitigated by process separation on the target topology) | The signer is reachable by object-graph introspection from the MCP `ToolRuntime` (via the shared `AlertRouter` closures over `platform`) and from anything holding the gateway (`verify_command=authoriser.verify` exposes `sign` through `__self__`). Symmetric HMAC means any verifier can sign. Violates "no AI/MCP component holds the key" at the object level, though no handler code performs introspection. | p1 N1 (path quoted in §3) | O-53 asymmetric signature (gateway holds only the public key; private key in HSM/KMS); interim: pass a verify-only closure, give the MCP runtime its own alert sink instead of the platform-wide router, and keep MCP servers in a separate process/pod (NetworkPolicy already models this, H-05). | MCP Security Agent; Security Architect |
| IVA-23 | **Low–Medium** | Alert auto-action `killswitch_account` on `execution.unauthorised_command` takes the account from the **unauthenticated** command: any Control-plane caller can halt any account (including non-existent ids that pollute the switch state) by sending one forged command; the activation is recorded as actor `risk-officer.system`, role `risk_officer` (a system actor carrying a human role). Fail-closed by intent, but a denial-of-service primitive in a multi-tenant deployment. | p1 NEW-OBS ×2; p3 | Key the auto-action on the lease holder/executor identity or the account of the lease, not the command payload; require the account to exist; record the actor as `ActorKind.SYSTEM`; alert but rate-limit repeated forgeries from one caller. | SRE Lead; Security Architect |
| IVA-24 | **Low** | The pipeline raises an unhandled `KeyError` for an intent whose `account_id` is not in the registry (no eligibility reason code, no audit row of the refusal). Fail closed by crash. | p3 N3b account_id | Eligibility to refuse unknown accounts with a reason code and audit row; contract test. | Backend Lead |
| IVA-25 | **Low** | Idempotency dedupe runs before authentication: an unauthenticated command carrying a live key receives the full `OrderRecord` (information disclosure inside the Control plane) and the event is audited as `duplicate_ignored` rather than `unauthorised`. | p1 N8; gateway.py lines 177-190 | Verify the MAC before the dedupe lookup (or return only the order id on dedupe). | Backend Lead |

Observations (non-blocking): Kill Switch hook failure leaves the `killswitch` lease held for the 30 s TTL without release (fail-safe); the intent tracker is not synced to CANCELLED after a Kill Switch cancel until the next `settle`; the nonce journal is unbounded (O-55).

## 5. Effect on the cycle-1 verdicts

**Gate B (was ACCEPT WITH CONDITIONS at 09a6e71).** On the evidence above the build-defect conditions IVA-01, IVA-02, IVA-05, IVA-06 and IVA-07 are closed in dev/sim, and IVA-08 is partially closed; the IVA recommends that these no longer stand as Gate B conditions in their cycle-1 form. The architecture now specifies Kill Switch/halt verification inside the execution plane and command authentication (ADR-015), but ADR-015 is Proposed, not Accepted, and the residual design findings IVA-20, IVA-21 and IVA-22 are architecture-level and should replace IVA-01/02 as conditions on the authorisation design (canonical form, one-shot/time-bounded authorisation, asymmetric key O-53). IVA-11 (plane guard per-process, NetworkPolicy never applied), IVA-12 (threat-model rows citing non-existent tests), IVA-13 (ADRs Proposed, boards' approvals) and IVA-14 (CI advisory-only, unsigned SBOM) are unchanged by this commit and remain conditions; R-06 (IdP/MFA) and O-22 (registry KMS signing) remain open. The Gate B recommendation remains ACCEPT WITH CONDITIONS, and the entry criterion — Gate A — is still not met: the Gate A veto grounds (jurisdiction hypothesis O-11/H-03, charter H-02, outcome targets O-16) are human decisions the build cannot close [Committee].

**Gate C (was REJECT at 09a6e71).** The two build-defect veto grounds are lifted in dev/sim by this re-validation: V-C1 (Kill Switch supersedes an already-authorised command at the gateway at every level, for halt and for non-ACTIVE status, at submit and at the unknown-order retry) and V-C2 (the gateway refuses every forged, altered, cross-intent, replayed-with-new-key or approval-misusing command and fails closed without its hooks). The lifting is conditional on closing IVA-19 — the retry-adoption race leaves a live broker order under an active Kill Switch, which is the same non-negotiable V-C1 named — and IVA-21 before Gate C is reconvened; the IVA would veto again on IVA-19 alone. V-C3 (no broker sandbox certification; simulated broker only) and V-C4 (no approved numeric limits) are untouched by the build and remain Committee/human decisions, as does IVA-09/O-54 (external audit anchoring, a Gate C condition). The Gate C recommendation therefore remains REJECT pending those items; when it is eventually passed it would authorise shadow and paper environments only and no market, strategy or autonomy [Source: 12]. Risk determinism and sim reconciliation, confirmed in cycle 1, are unaffected (147 tests still pass; TC-RK-021 added).

## 6. Per-finding verdict table

| Finding | Cycle-1 status | Re-validation verdict | Evidence |
|---|---|---|---|
| V-C1 Kill Switch/halt not enforced at gateway (IVA-01) | Veto (Gate C); condition (Gate B) | **CLOSED (dev/sim)** — residual IVA-19 opened (retry adoption after failed cancel) | p1 V-C1 ×12, N5 |
| V-C2 Forged/unauthenticated commands accepted (IVA-02) | Veto (Gate C); condition (Gate B) | **CLOSED (dev/sim)** — residual IVA-20/21/22 opened on the HMAC design; O-53 open | p1 V-C2 ×15, N1–N3b, N7 |
| IVA-03 Position cap ignored open orders | Condition (Gate C) | **CLOSED (dev/sim)** | p2 IVA-03 ×9 |
| IVA-04 Strategy owner could approve own intent | NOT MET (Gate C) | **CLOSED (dev/sim)** | p2 IVA-04 ×7 |
| IVA-05 Agent could `reject()` limit changes | Condition (Gate B) | **CLOSED (dev/sim)** | p2 IVA-05 ×5 |
| IVA-06 BFF fail-open when RT_ENV unset | Condition (Gate B) | **CLOSED (dev/sim)**; R-06 open by design | p2 IVA-06 ×7 |
| IVA-07 Dev registry key not black-listed | Condition (Gate B) | **CLOSED (dev/sim)**; O-22 symmetric HMAC open | p2 IVA-07 ×11 |
| IVA-08 Nonce store process-local | Observation (B) → condition (C) | **PARTIALLY CLOSED** — mechanism verified; journal not wired in the composition root (`nonce_path=None`); unbounded; no replica store | p2 IVA-08 ×6; platform.py line 706 |
| IVA-09 Audit anchor in-process only | Observation (B) → condition (C) | **NOT CLOSED** (not claimed; documented O-54; no code change) | p2 IVA-09; git diff |

## 7. Sign-off

| Role | Name | Status |
|---|---|---|
| Author | Independent Validation Agent (AI) | 2026-09-07 |
| Reviewer | pending | — |
| Approver | pending (Committee chair) | — |

Verdicts are recommendations; nothing here is self-certified and no gate passes on this document. Probe scripts p1_gateway.py, p2_controls.py and p3_followup.py and their outputs are held outside the repository by the IVA and can be reproduced on request against `c0bb1fb` with the environment stated in §1.
