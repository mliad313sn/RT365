# Risk review — decision pack O-170 / O-171 / O-172 (2nd line, Chief Risk Agent)

**Subject:** `docs/SESSIONS/COUNCIL_2026-09-09_O-170_O-172_mcp_security_agent.md`, read in full.
**Commissioned by:** D-068; the RAID rows name the Chief Risk Agent as decider-side counterpart on O-170 and O-171 [Source: docs/RAID_LOG.md:231-232].
**This document is a review. It records no approval, no decision, no gate pass and no risk acceptance, and it sets no number.** No acceptance exists until it is in `docs/DECISION_LOG.md` [Source: CLAUDE.md:7; docs/PRODUCT_OWNER.md:13].

| Prepared by | Author of the pack | Recommending body | Decider | Status |
|---|---|---|---|---|
| Chief Risk Agent (2nd line) — reviews, recommends, **never approves** [Source: docs/RISK_POLICY.md:5] | MCP Security Agent (2nd line) — I am not the author and have not edited the pack | Trading Risk Committee (O-170 values, O-171 blast radius); Security & Privacy Board (mechanisms) [Source: docs/PO_DECISION_QUEUE.md:88] | Product Owner / delegate under D-039/D-040 [Source: docs/PRODUCT_OWNER.md:22] | **Review complete — nothing approved** |

**Reading rules.** `[Source: path:line]` is a fact read on this worktree at `0510dd0`, 2026-09-09. `[Committee]` is my opinion or recommendation. `[Open]` is not established anywhere, with the source that would settle it named. Profit is an objective, never a promise [Source: CLAUDE.md:3].

**Provenance note on the pack.** The pack cites the tree at `442cebd`. HEAD is now `0510dd0`. The diff between them touches documents only — no file under `mcp/`, `apps/`, `libs/`, `services/`, `observability/` or `scripts/` changed [Source: `git diff --stat 442cebd..0510dd0`, 2026-09-09]. **Every code citation in the pack still holds.** One documentation citation has already been superseded: the pack's finding §8.7 (the `O-81` mis-citation in `docs/MCP_TOOL_CATALOG.md`) was corrected by its owner on this commit and now reads `[Open: O-172]` with the correction stated in line [Source: docs/MCP_TOOL_CATALOG.md:34].

---

## 0. What I verified independently, and what I take from the pack

I re-read the pack's load-bearing claims against the tree rather than accepting them. The pack is **accurate on every mechanical claim I checked** and, in two places, it *understates* the position. My conditions below rest on facts I read myself; where I rely on the pack's reading without re-checking I say so.

Verified independently: `revoke_agent_identity`'s implementation, key and reach; the absence of any agent-level restore; the egress alert payload; the alert-router dispatch and `required=` semantics; the registry schema's unconstrained fields; the divergence between `observability/alerts.yaml` and `docs/ALERT_CATALOG.md`; which auto-actions are bound today and whether their payloads satisfy them.

---

## 1. O-171 — blast radius of `revoke_agent_identity`, verified from the tree

The pack asks me to confirm the blast radius deliberately (C-171-3), as O-137 asks the Trading Risk Committee to do for the audit-halt case [Source: docs/RAID_LOG.md:198]. I did. **The pack's characterisation is right in direction and materially incomplete in three respects.** Two of them are new preconditions.

### 1.1 What the action actually does

The chain is: `alerts.on("revoke_agent_identity", lambda a: issuer.revoke_agent(str(a.payload["agent"]), by="alert_router", ...), required=("agent",))` [Source: apps/web/web_bff/platform.py:1378-1381] → `IdentityIssuer.revoke_agent` → `RevocationList.revoke("agent", agent_id, ...)` [Source: mcp/servers/mcp_servers/identity.py:197-199] → appended to a JSON-lines journal that every issuer and runtime replays at start-up [Source: mcp/servers/mcp_servers/revocation.py:33-41, :50-56].

The revocation bites at `IdentityIssuer.verify`, at `if self._revocations.is_revoked("agent", ident.agent_id)` [Source: mcp/servers/mcp_servers/identity.py:178], which sits **before** the tenant / account / strategy scope loop [Source: mcp/servers/mcp_servers/identity.py:179-186] and before signature and replay checks. The tool call then returns `deny("IDENTITY", ...)` [Source: mcp/servers/mcp_servers/runtime.py:203-208].

### 1.2 BR-1 — the revocation key is a bare, caller-supplied string with no tenant namespace

`agent_id` is a free `str` parameter of `IdentityIssuer.issue` [Source: mcp/servers/mcp_servers/identity.py:103], defaulted to a single literal by the composition root [Source: apps/web/web_bff/platform.py:606] and passed straight through from the command line by `rt365 mcp-serve` [Source: apps/cli/rt365_cli/main.py:198]. Nothing derives it from, or checks it against, tenant, account or strategy. `Revocation.target` for kind `agent` is that bare string [Source: mcp/servers/mcp_servers/revocation.py:21-25; identity.py:198].

Therefore the effective radius is **every identity ever minted, in every tenant, in every account, under that string — including tokens minted after the revocation**. TC-AI-008 proves the "after" half directly: a rebuilt platform mints a *fresh* identity under the revoked id and the call is still denied `IDENTITY` [Source: test/quartets/test_tc_ai_mcp.py:236-243; docs/TEST_CASES/TC-AI.md:29].

The pack's §2.2 Option C states the radius as "Nothing else: no Kill Switch, no order path, **no other tenant**, no other agent" [Source: docs/SESSIONS/COUNCIL_2026-09-09_O-170_O-172_mcp_security_agent.md:123]. The "no other tenant" clause is a property of a **naming convention that is enforced nowhere**. In the shipped fixture every identity defaults to the same literal, so today a single egress denial by any handler would revoke the identity every session, every test and every tenant-sim caller uses. This is a cross-tenant control acting on an unauthenticated, unvalidated string — the same class of defect as R-22's "tenant is not an authenticated claim", which was remediated for the read and write paths but not for this key [Source: docs/RAID_LOG.md:135].

**This is a third precondition, and it is not optional.** Contrast: `revoke_tool_for_scope` composes its key as `tenant/account/strategy/tool` [Source: mcp/servers/mcp_servers/allowlist.py:59 via `grant_key`], and tenant revocation is keyed by tenant. Agent revocation is the only one of the four whose key carries no scope at all.

### 1.3 BR-2 — there is no agent-level restore in the code, and the two-person claim is documentation only

The pack states "Restoring is a two-person act [Source: mcp/policies/README.md:11]" [Source: docs/SESSIONS/COUNCIL_2026-09-09_O-170_O-172_mcp_security_agent.md:110]. That is true of the **written procedure** [Source: mcp/policies/README.md:11-12] and **false of the tree**:

- `IdentityIssuer` has `revoke_agent` and `revoke_scope` and `restore_scope`. **There is no `restore_agent`** [Source: mcp/servers/mcp_servers/identity.py:197-236, whole class read].
- `restore_scope` enforces two distinct named approvers and refuses otherwise [Source: mcp/servers/mcp_servers/identity.py:226-229] — but only for kind `"scope"` [Source: :231].
- Every other revocation kind has a service-layer restore: registry [Source: mcp/servers/mcp_servers/runtime.py:134], tenant [Source: mcp/servers/mcp_servers/allowlist.py:152], grant [Source: mcp/servers/mcp_servers/allowlist.py:59]. Kind `agent` has none.
- The only way to undo it is to call the raw store method `RevocationList.lift("agent", agent_id, by=..., at=...)` [Source: mcp/servers/mcp_servers/revocation.py:58-61] — which takes a free-form `by` string, **enforces no two-person rule, emits no audit event, and has no BFF endpoint** (`grep -rn "restore_agent|\.lift(" --include=*.py`, 2026-09-09: no product call site for kind `agent`).
- **No test restores an agent revocation.** TC-AI-004 and TC-AI-015 restore the *registry*; TC-TEN and TC-KS restore *scopes* [Source: docs/TEST_CASES/TC-AI.md:28, :30; test/quartets/test_tc_ten_tenancy.py:259-262; test/quartets/test_tc_ks_killswitch.py:91, :216]. TC-AI-008 revokes an agent and proves only that it stays revoked.

This fails in **both** directions, which is why I will not waive it:

- **Fail-open on recovery.** A single actor with process access can lift a revocation that two humans were supposed to lift, and the lift is written to the journal but raises no `mcp.identity.restored` audit event to match the `mcp.identity.revoked` one [Source: mcp/servers/mcp_servers/identity.py:199 — the revoke side audits; the lift side has no service wrapper to audit from]. Under the journal defect already recorded — no digest, no chain, a deleted line silently un-revokes [Source: mcp/policies/README.md:22; Open: O-55, O-118, O-128] — the recovery path is the softest part of the whole control.
- **No supported recovery.** The pack's C-171-5 asks that the revocation be exercised in the emergency revocation drill. A drill cannot exercise a restore that does not exist. Binding this auto-action before the restore exists means the first false positive produces an outage whose remedy is an undocumented direct call to a store primitive.

My standing heuristic applies without qualification: **a control whose recovery path is not built, not owned and not tested is not a control, it is an outage waiting for a trigger.** The control quartet exists precisely to force the recovery leg (CLAUDE.md line 4).

### 1.4 BR-3 — what it does *not* reach, which is the proportionality argument in its favour

I checked the other direction too, because a blast-radius finding that only lists harms is not a risk opinion.

- The revocation list is consulted **only on the MCP tool-call path**: `IdentityIssuer.verify` and `ToolRuntime.call` [Source: mcp/servers/mcp_servers/identity.py:178; runtime.py:200, :219, :222]. `grep -rn "is_revoked" services/ libs/ apps/web/web_bff/` returns no product call site outside the composition root, 2026-09-09.
- **An intent already in the queue is unaffected.** `submit_trade_intent` records `submitted_by=f"agent:{p.agent_id}"` [Source: mcp/servers/mcp_servers/tools.py:146] and nothing downstream re-checks revocation. Revocation is purely prospective.
- It engages no Kill Switch level, cancels no resting order, suspends no account's autonomy and changes no limit.

So the action is **narrow on the trading axis and wide on the identity axis**. It costs analysis and intent-submission capability for a name; it does not touch the book. For an `EGRESS_NOT_ALLOWLISTED` event — an identity asking for a destination it may never have — that is the right shape: it narrows, never widens, in compliance with the standing rule [Source: docs/ALERT_CATALOG.md:36].

I also disagree, usefully, with the pack's own C-171-6. The runtime's per-token deny bucket is keyed on `token_id` [Source: mcp/servers/mcp_servers/runtime.py:206, :214], so a re-mint resets it; the agent revocation survives a re-mint (§1.2). **Revocation is therefore a strictly stronger bound than `DENY_RATE`, and repeat revocations are idempotent in effect.** The "alert storm" is a pager and journal-growth problem (with O-55/O-111 compaction), not a control problem. C-171-6 can be narrowed to that, which removes one open item from the critical path.

### 1.5 BR-4 — the revocation record cannot be joined to the call that caused it

The egress decision object carries `correlation_id` and `tenant` [Source: mcp/servers/mcp_servers/egress.py:82-85] and passes both to the audit sink [Source: mcp/servers/mcp_servers/egress.py:174], but `EgressDecision.payload()` — the dict handed to the alert — **drops both** [Source: mcp/servers/mcp_servers/egress.py:86-95]. `revoke_agent` then journals under `correlation_id: f"agent:{agent_id}"` [Source: mcp/servers/mcp_servers/identity.py:199]. There is consequently no key joining the revocation to the tool call, the tenant or the destination that triggered it.

This is a BCBS 239 point, not a nicety: a risk action whose record cannot be reconstructed against its trigger cannot be evidenced to a supervisor or reviewed after a loss event. `correlation_id` and `tenant` must join `agent` in the payload contract of C-171-1, in the same act.

### 1.6 Comparison against the platform's existing auto-actions

`revoke_agent_identity` is **already bound to three catalogued alerts** and fires today: `plane.deny`, `mcp.canary_in_output`, `killswitch.agent_attempt`, plus `risk.integrity_violation` [Source: observability/alerts.yaml:5, :7, :9, :23]. I checked whether their payloads satisfy the action, since the pack raises that defect for egress: they do — the runtime's `deny()` builds `{"tool", "tenant", "code", **scope}` and `scope` carries `agent`, `account`, `strategy` [Source: mcp/servers/mcp_servers/runtime.py:178-185, :212]. **The payload defect is specific to the egress guard, which builds its own payload and bypasses `deny()`.** The pack's §8.3 is correct and correctly scoped.

Ranked by blast radius, the platform's bound auto-actions are: `killswitch_platform` (2 alerts) > `killswitch_account` (4) > `revoke_agent_identity` (4, and cross-tenant per §1.2) > `suspend_signals` (strategy scope) > `revoke_tool_for_scope` (1 tool, 1 scope) > `autonomy_to_supervised` / `account_to_supervised` / `cancel_only` [Source: observability/alerts.yaml, whole file read 2026-09-09]. `revoke_agent_identity` sits in the upper-middle of a ladder that already exists. **Adding a fourth binding to an action that already carries three is a marginal change, not a novel one** — which is a point in the recommendation's favour and one the pack did not make.

### 1.7 The accumulation argument (O-126, O-134, O-137, O-165) — and the one interaction nobody has stated

The programme now carries these fail-closed conditions, each individually correct: an absent or malformed trust set refuses every asymmetric signature [Source: docs/RAID_LOG.md:187, O-126]; an unpinned or mismatched trust anchor refuses the registry [Source: docs/RAID_LOG.md:231 context, O-169]; a corrupted audit store halts trading platform-wide [Source: docs/RAID_LOG.md:198, O-137]; a control store whose head the audit chain cannot confirm will not open, so the platform will not start [Source: docs/RAID_LOG.md:226, O-165]; `risk.fail_open_attempt` halts the platform [Source: observability/alerts.yaml:4]. The delegate has already recorded that "the platform can now be stopped by losing a file" and that these are new single points of availability failure [Source: docs/PO_DECISION_QUEUE.md, PC-A-4]. Red-team case RT-09 is written precisely to use the fail-closed controls as the weapon [Source: docs/RED_TEAM_PLAN.md:29].

O-170 and O-172 each add one more: a ceiling breach refuses the registry, a pin failure refuses start-up. O-171 adds one of a *different* kind — the only one of the three that is not a start-up condition but a **persistent, journalled, in-flight state change with no built recovery** (§1.3).

**CROSS-1 — the interaction none of the three items states, and my most important finding on the pack as a whole.** O-172 Option B pins `observability/alerts.yaml` by digest [Source: pack §3.3]. O-171's answer *lives in* `observability/alerts.yaml` [Source: observability/alerts.yaml:26; pack §3.1.4]. Once the file is pinned, the operator's obvious mitigation during a misfiring revocation — set the auto-action back to `none` while the cause is found — becomes a two-file change across two 2nd-line owners (the SRE Lead owns the catalogue [Source: docs/ALERT_CATALOG.md:5], the pin record is proposed to the Security Architect [Source: pack §6]), and until it lands the platform refuses to start against the old file. **The de-escalation lever for the new auto-action is itself placed behind a new fail-closed control, by a sibling decision, and neither item mentions it.** That is the accumulation risk made concrete. It does not argue against either item; it argues that they must be decided as one thing with a stated incident procedure, and that O-172's pin for `alerts.yaml` is a *precondition of O-171 having any durable effect* (an unsigned, unpinned catalogue means the decision can be edited back to `none` by anyone who can write the file — the pack says this at §3.1.4 but does not draw the sequencing conclusion).

### 1.8 Is the recommendation proportionate?

**Yes, in direction, and the two preconditions are not sufficient.** The event class is genuinely identical to `plane.deny`; the action only ever narrows; nothing can raise the alert today from a shipped handler [Source: mcp/servers/mcp_servers/egress.py:7-14; docs/TEST_CASES/TC-AI.md:18], so the action would be in place before the first handler that could ask — which is the right sequencing and I endorse it. Option D (any Kill Switch action) is correctly and emphatically rejected; I would have rejected it in the same terms. Option A leaves an S1 that stops nothing in the one control whose claim is structural impossibility, which is not tenable once a handler can perform I/O. Option B is the right fallback if the delegate judges the identity radius too large after §1.2 is fixed.

**A third and a fourth precondition are required** (§1.2 scoping of the revocation key, §1.3 a built and tested restore). Conditions in full at §6.

---

## 2. O-170 — is the ceiling the right control, what it must cover, and how the numbers get set

### 2.1 The mechanism is right

**Yes, from a risk standpoint, and this is the highest-confidence part of my review.** A ceiling table compared at load is structurally the same control as the limit hierarchy I own: a bound set at a higher level that a lower level cannot widen, with `effective = min` [Source: docs/LIMIT_MATRIX.md:7]. `registry <= ceiling` **is** `effective = min` expressed for one field. The pack's Option C places the comparison at the point the value becomes effective — inside `load_registry`, before the `ToolSpec` is constructed [Source: pack §1.4b] — which is the load-bearing placement; a check only in `scripts/verify_tool_registry.py` or `rt365 check` is a CI opinion about a file, not a control over a running process, and I would not accept it. C-170-4 (a `RegistryUnsigned` subclass so every existing catcher still fails closed) is correct.

C-170-2 (a CODEOWNER pair on the ceiling record) and C-170-3 (the ceiling module not owned by the seat that owns the registry) are the maker-checker half and are non-negotiable from my seat: **a limit whose author is its own approver is not a limit** [Source: CLAUDE.md:4-5; docs/RISK_POLICY.md:38].

The pack's §8.1 finding matters and I endorse it: TC-AI-030 refuses the forged registry because the *key* is outside the trust set, not because any value was compared [Source: test/quartets/test_tc_ai_egress_trust.py:391-424; docs/TEST_CASES/TC-AI.md:19]. **No document, gate pack or board minute may cite TC-AI-030 as evidence that T-91 is closed.** The insider and key-holder case has no control today.

### 2.2 What a ceiling must cover that the pack does not list

Four gaps. The first two are the ones I would refuse a decision without.

**G-1 — a validly signed registry can disable the exfiltration-marker control without touching a single number.** `canary_tokens` is read as `content.get("canary_tokens", ())` — **optional, defaulting to empty** — and the schema places no constraint on it beyond "array of string" [Source: mcp/servers/mcp_servers/registry.py:57, :330]. The runtime iterates whatever it finds [Source: mcp/servers/mcp_servers/runtime.py:239-241]. A signed registry that simply omits the key silently disables `mcp.canary_in_input` — and, with it, an auto-action already in force [Source: observability/alerts.yaml:8]. **This is the T-91 class exactly, it is arguably worse than a quota widening because it is silent and requires no suspicious value, and it is not in the pack's ceiling table** [Source: pack §1.4a, whole table read].

**G-2 — a validly signed registry can neutralise input validation the same way.** `input_schema` is typed `{"type": "object"}` [Source: mcp/servers/mcp_servers/registry.py:89] and passed straight to `jsonschema.validate` [Source: mcp/servers/mcp_servers/runtime.py:243-246]. An empty object validates everything. Also absent from the ceiling table.

**G-3 — aggregate ceilings live outside the registry entirely and would remain uncapped.** `ToolRuntime.__init__` carries `tenant_ceiling_per_minute` and `deny_limit_per_minute` as **constructor defaults**, not registry fields [Source: mcp/servers/mcp_servers/runtime.py:88-89, :103-104, :233]. They are in no catalogue row, no ceiling table and no approval record [Open: O-07]. A ceiling covering only registry-carried fields caps the per-tool number and leaves the aggregate a caller argument. In my lane the aggregate is what matters: six tools each at a capped rate still compose an exposure nobody bounded. The decision must either bring aggregate ceilings into scope or **record explicitly that it does not, and name the item that carries them**, so that "the registry is ceiling-checked" is never read as "MCP call volume is bounded". I set no value for either and I do not propose one here.

**G-4 — the comparator must be declared data, and a row without one must be refused.** The pack states comparators in a prose table in the pack [Source: pack §1.4a]. This programme has already been bitten by exactly this: two SLIs were judged in the inverted direction because the code inferred the dangerous direction, and the adopted rule is that **the direction of a control is settled before the number it compares against, and one that omits it is refused** [Source: docs/RAID_LOG.md, O-174]. The ceiling artefact must carry the comparator per field as data, and a row lacking one must refuse rather than default to `<=`.

Two smaller notes, not conditions: the write-tool scope check is a substring test for the word "queue" [Source: scripts/verify_tool_registry.py:73-74], which is shape, not semantics, and remains a residual under O-170; and the ceiling must carry **no override or exemption field**, because an exemption converts `effective = min` into `effective = whatever the artefact says`.

**CROSS-2 — an operator-facing consequence of C-170-4.** Making `RegistryOverCeiling` a subclass of `RegistryUnsigned` is right for fail-closed and wrong for the operator unless handled: a ceiling breach and a forged signature have **opposite recoveries** — one is "change the catalogue with two reviewers", the other is "you are under attack" — and every existing `except RegistryUnsigned` handler will present the first as the second [Source: scripts/verify_tool_registry.py:32-34; apps/cli/rt365_cli/main.py:100-104]. The reason code must be distinguishable in structured form, not only in a message string, and the operator wording is the Support & Training Lead's and Frontend Lead's, not the builder's — the same defect class as O-166 [Source: docs/RAID_LOG.md, O-166].

### 2.3 The process that should set the numbers later — no number set now

I set no value here and none may be inferred from anything below. The **process** I recommend, which is a mechanism and not a threshold:

1. **Join it to O-07; do not run it in parallel.** Ceilings on MCP tool quotas, payloads, timeouts and aggregate call rates are limits. They belong in `docs/LIMIT_MATRIX.md` under the same hierarchy and the same `effective = min` rule as every other limit [Source: docs/LIMIT_MATRIX.md:7], recommended by the Trading Risk Committee and decided by the Product Owner in the manner already queued for O-07 [Source: docs/PO_DECISION_QUEUE.md:86]. A second, parallel threshold-setting process with a different owner is how thresholds get copied from another asset class.
2. **Owner, harm and basis before value.** Each ceiling row carries, before any number is proposed: the owner, the harm it bounds, the comparator/direction (G-4), the basis (a measurement, a policy choice, or a protocol/vendor constraint), and the approval record. **A row without an owner and a basis is not proposed and is not decidable.**
3. **Direction before number** (the O-174 rule), and **shape before value**: the pack is right that the catalogue's prose column must become structured data first (C-170-5); a number cannot be approved into a field that does not exist.
4. **The interim seed is a freeze, not an approval.** C-170-1's "no wider than the values committed at `442cebd`" is the correct interim and must be labelled in the artefact as a freeze of an existing fixture with the same `approved_for_production: false` semantics the sim risk policy already carries [Source: docs/LIMIT_MATRIX.md:26; services/risk/policies/sim-policy-v0.1.yaml]. The catalogue's sentence "No number in this catalogue is a decided threshold" [Source: docs/MCP_TOOL_CATALOG.md:47] stays until a recorded risk decision replaces it, and only the Product Owner's decision may replace it.
5. **Maker-checker *and* a cooling period.** The pack has the maker-checker half (C-170-2, C-170-3) and **is missing the cooling period**, which `docs/RISK_POLICY.md` requires of every limit change [Source: docs/RISK_POLICY.md:38]. A ceiling **widening** must not be effective in the same act that authors it. The length of the cooling period is a Trading Risk Committee recommendation and a Product Owner decision [Open: O-07]; I name none. A **narrowing** may be immediate — narrowing is always the safe direction.
6. **A ceiling change is a limit change and must emit `limit.changed`**, which already exists as a catalogued alert [Source: observability/alerts.yaml:28]. This gives the change a monitored trace without inventing anything.
7. **Values are set per environment rung and are never widened by promotion alone** [Source: CLAUDE.md:6].
8. **Nothing here registers or approves a tool.** C-170-6 is correct: O-35 is untouched and a passing ceiling check must never be reported as tool approval [Source: docs/RAID_LOG.md:52].

---

## 3. O-172 — is the risk correctly characterised, and is the window acceptable

### 3.1 Characterisation: correct, and it under-ranks the highest-value target

The pack's factual account is right: four kinds of unsigned, unpinned YAML load beside one signed artefact; the pin mechanism already exists, is generic over a purpose and already fails closed on absent/unpinned/mismatched/wrong-purpose/malformed [Source: libs/core/rtcore/trust.py:155-206]; the bundle already carries the paths [Source: apps/cli/rt365_cli/main.py:23-29]. Rejecting Option A is right and the argument is the correct one: the registry signature carries **tool-approval** semantics, and stretching it over a per-tenant allowlist would place an unapproved tenant policy inside an artefact whose signature asserts approval [Source: mcp/servers/mcp_servers/registry.py:229-241; docs/MCP_TOOL_CATALOG.md:34]. B-then-C is the right sequencing.

**One risk-ranking correction the pack does not make and the register does not record.** The four files are not equivalent targets. Three are **grants or declarations**: `egress.yaml` and the allowlists widen what an identity may reach; `runtime.yaml` is a declaration nothing enforces at runtime (the pack's §8.8, verified: both checkers read it [Source: scripts/verify_tool_registry.py:79-84; apps/cli/rt365_cli/main.py:118-123] and the MCP runtime does not). `observability/alerts.yaml` is a **control decision** — it is the file that says what every alert *does*. An attacker who can write it can set `killswitch_platform` on `audit.chain_verification_failed` to `none` [Source: observability/alerts.yaml:15], set `killswitch_platform` on `risk.fail_open_attempt` to `none` [Source: observability/alerts.yaml:4], and disable every `revoke_agent_identity` binding, in one edit, with no signature to forge. **`alerts.yaml` is the highest-value of the four by a wide margin and should be pinned first if the four are not pinned together.** I would state this in the register.

The pack's own qualification stands and I would not soften it: the interim pin's integrity rests on the start-up environment, and the compiled pin table is empty today with the operator variable the only source [Source: libs/core/rtcore/trust.py:144-147]. For `alerts.yaml` specifically, the attacker who can write the file and the attacker who controls the environment are largely the same actor (T-92, RT-10 [Source: docs/RED_TEAM_PLAN.md:31]), so the interim raises the cost **less** for the most valuable file than for the other three. That does not make it not worth doing; it makes "pinned" a weaker word here than a reader would assume, and C-172-1 must say so about `alerts.yaml` by name.

### 3.2 Does "pin by digest now, signed manifest at H-20" leave an unacceptable window before shadow?

**No — conditionally, and the conditions are load-bearing.** My reasoning:

Arguments that the window is tolerable: nothing is deployed, there is no real tenant, no real handler that performs I/O and no broker route [Source: docs/RED_TEAM_PLAN.md:29-31; Open: H-05]; the pin mechanism is buildable now without a key and reuses tested code paths; and the alternative — waiting for a key ceremony that is a human act with no date [Open: H-20] — means shipping into shadow with **nothing at all**, which is strictly worse.

Arguments that it is not nil: shadow is not a vacuum. A widened `egress.yaml` is precisely the exfiltration path for market data and account state, and a widened allowlist lets a tool submit intents. Shadow carries realistic data. The residual is data and analysis exposure, not order flow — but it is real, and calling it zero because shadow places no orders would be the kind of comfortable framing that my seat exists to refuse.

So the window is acceptable **only** if all four of these hold, and I do not concur without them:

(a) the interim pin covers **all four kinds of file, `alerts.yaml` first**, not "some before shadow";
(b) RT-08 is actually run against what is built, by a seat that did not specify it [Source: docs/RED_TEAM_PLAN.md:27; docs/PO_DECISION_QUEUE.md, PC-S-4] — the pack's C-172-6, which I adopt unchanged;
(c) the residual is **recorded as accepted by the Product Owner with a named owner and a review date**, not inherited by silence — this is the whole point of the item;
(d) no document, gate pack or board minute describes T-90 or RT-08 as closed by the interim [Source: docs/THREAT_MODEL.md:108; docs/PO_DECISION_QUEUE.md, PC-S-3].

And the sequencing point from §1.7 (CROSS-1): **O-172's pin for `alerts.yaml` is a precondition of O-171 having any durable effect.** Deciding O-171 without it produces a control decision that anyone with file write can revert, and deciding O-172 without O-171's incident procedure produces a de-escalation lever behind a fail-closed gate. They are one decision with two artefacts.

---

## 4. The pack's findings — which change a severity or create a new risk

The pack presents **eight** numbered findings in §8 and **three** new proposed threat rows in §4; the commission says ten. I read all eleven and treat that as the finding set; the count discrepancy is noted, not material.

| Finding | My reading | Severity effect |
|---|---|---|
| §8.1 TC-AI-030 covers the outsider case only | Verified [Source: test/quartets/test_tc_ai_egress_trust.py:391-424]. Not a severity change but an **evidence-integrity** constraint: T-91's control column is empty today and a passing test must not be cited as closing it. Same defect class as PC-S-3. | Wording constraint on T-91 and O-170; no severity change |
| §8.2 `submit_trade_intent` is the weaker masking illustration; `read_account_state` is the one that matters | Verified [Source: mcp/policies/tool_registry.json:90, :365]. Correct; sharpens the example. | None |
| §8.3 no strong auto-action would work if bound today (payload mismatch) | Verified, and correctly scoped to the egress guard, which builds its own payload and bypasses `deny()` (§1.6). | **New risk — Medium.** See NR-1 |
| §8.4 one alert name, two causes | Verified [Source: mcp/servers/mcp_servers/egress.py:148-172; observability/rtobs/alerts.py:90, :101]. Generalises: the router keys on **name** alone, so any alert whose name spans an attack and a deployment fault mis-fires. | **New risk — Medium.** See NR-2 |
| §8.5 `mcp.egress_denied` has no row in `docs/ALERT_CATALOG.md` | Verified — **and the defect is far larger than one row.** See NR-3. | **Raises O-171's context materially; new risk — High.** |
| §8.6 `alerts.yaml` is outside `mcp/policies/`, so no directory formulation reaches it | Verified [Source: apps/cli/rt365_cli/main.py:24]. Correct; the decision must name paths. | None (absorbed into O-172) |
| §8.7 `O-81` mis-citation in the tool catalogue | **Already corrected by the owner on this commit** [Source: docs/MCP_TOOL_CATALOG.md:34]. | None — closed |
| §8.8 `runtime.yaml` is checked by nothing that runs the runtime | Verified. The register must not let "pinned" be read as "enforced"; the sandbox remains unbuilt [Open: H-05, MSA-3]. | Wording constraint on O-172; no severity change |
| §4 row 3 (auto-action payload mismatch) | Should be a RAID **Risk**, not only a threat row — see NR-1. | See NR-1 |
| §4 row 4 (one name, two causes) | Same — see NR-2. | See NR-2 |
| §4 row 5 (the ceiling record is unprotected) | Verified: `docs/MCP_TOOL_CATALOG.md` has no CODEOWNERS entry and `/mcp/policies/` has a single-seat owner [Source: .github/CODEOWNERS:8]. This is the maker-checker defect in my own vocabulary and it is a condition of O-170, not a nice-to-have. | Folded into O-170 as a blocking condition (C-170-2/3) |

### New risks I would register

I do not write RAID rows in this review. These are proposed to the ledger owner, with the severity I would give each.

- **NR-1 — `required=` does not make a silent no-op impossible; it only catches *missing* keys. Severity: Medium.**
  The catalogue asserts "a silent no-op remains impossible" [Source: docs/ALERT_CATALOG.md:36] and the router's docstring says the same [Source: observability/rtobs/alerts.py:65]. Both are overstated in two ways I verified. First, a key that is **present but useless** passes: `revoke_grant_for_scope` reads `a.payload.get("tenant") or platform.tenant_for(...)`, and the runtime's pre-identity `tenant` default is the string `"-"`, which is truthy [Source: apps/web/web_bff/platform.py:1352-1353; mcp/servers/mcp_servers/runtime.py:164]. Second, the action itself returns without acting: `if allowlist is None: return` [Source: apps/web/web_bff/platform.py:1354-1356] — no exception, no `alert.autoaction_failed`, no record that nothing happened. Today no raise site reaches that path (both `mcp.non_allowlisted_tool` sites fire after `tenant = ident.tenant_id` [Source: mcp/servers/mcp_servers/runtime.py:206, :218, :228]), so this is **latent, not live**. It becomes live the moment a raise site is added before identity resolution, or a tenant's allowlist is not loaded. The general control: an auto-action that completes without acting must be as loud as one that could not start. I am the named reviewer of `docs/ALERT_CATALOG.md` [Source: docs/ALERT_CATALOG.md:5] and I would not sign the line at :36 as it stands.

- **NR-2 — auto-actions are dispatched on alert *name* alone, so a name that spans an attack and a fault mis-fires by construction. Severity: Medium.**
  The pack found the egress instance; the mechanism is general [Source: observability/rtobs/alerts.py:90, :101]. The control is a rule, not a patch: **no alert name may span two causes with different correct responses**, and adding an auto-action to an existing name requires re-examining every raise site of that name. Owner: SRE Lead, reviewer Chief Risk Agent.

- **NR-3 — `observability/alerts.yaml` and `docs/ALERT_CATALOG.md` have diverged, and five auto-actions are in force at runtime with no row in the document of record. Severity: High.**
  `alerts.yaml` declares itself a mirror of the catalogue [Source: observability/alerts.yaml:1]. It carries thirty alerts; the catalogue carries eighteen rows, eleven of them under prose labels with no machine name, so **no automated check can verify the mirror claim** [Source: docs/ALERT_CATALOG.md:7-26; observability/alerts.yaml, both read in full 2026-09-09]. Twelve alert names in the yaml have no counterpart in the catalogue under any label, and **five of those carry auto-actions that fire today**: `mcp.canary_in_output` → `revoke_agent_identity`, `killswitch.agent_attempt` → `revoke_agent_identity`, `risk.integrity_violation` → `revoke_agent_identity`, `mcp.canary_in_input` → `revoke_tool_for_scope`, `execution.unexpected_fill` → `killswitch_account` [Source: observability/alerts.yaml:7, :8, :9, :23, :27; and `grep -in` for each name against docs/ALERT_CATALOG.md returns nothing].
  This changes how O-171 should be read. **The council is deliberating whether to add a fourth `revoke_agent_identity` binding while three undocumented ones already fire, and while an account-level Kill Switch binding sits outside the document of record.** That is a governance defect in the catalogue, not an egress defect, and it is larger than the one missing row the pack reports. The catalogue is my review lane and I would open this against the SRE Lead as owner with me as reviewer, with a CI check that the two files agree by machine name as the control. Severity High because the document that the Trading Risk Committee, the boards and any gate pack would read to learn what the platform does automatically **does not describe five things it does automatically**, three of them cross-tenant identity revocations (§1.2).

- **NR-4 — agent-level revocation has no restore path, no two-person enforcement, no audit event and no test. Severity: High.**
  §1.3 in full. Independent of whether O-171 is adopted: three alerts already bind this action [Source: observability/alerts.yaml:5, :7, :9], so the missing recovery leg is a **live** gap today, not one O-171 would create. It is the counterexample to the claim in `mcp/policies/README.md:11` that restoring is a two-person act, and it must be fixed there or in code, not left as prose. Owner: Backend Lead (code), MCP Security Agent (semantics), reviewer Chief Risk Agent.

- **NR-5 — the agent revocation key carries no tenant, account or strategy scope. Severity: High.**
  §1.2 in full. Also live today, for the same three bindings. Related to R-22's tenant-authenticity remediation, which did not reach this key [Source: docs/RAID_LOG.md:135].

- **NR-6 — CROSS-1: pinning `alerts.yaml` places the de-escalation lever for every auto-action behind a fail-closed control. Severity: Medium.**
  §1.7 in full. Not an argument against either item; an argument that O-171 and O-172 must be decided together with a written incident procedure for changing an auto-action under a pin, owned by the SRE Lead and reviewed by me, before either is called done. This is the concrete instance of the accumulation the delegate already flagged at PC-A-4 and that O-126, O-134 and O-165 each contribute to.

- **NR-7 — a validly signed registry can disable the canary control and neutralise input validation without breaching any numeric ceiling. Severity: Medium-High.**
  G-1 and G-2 in §2.2 [Source: mcp/servers/mcp_servers/registry.py:57, :89, :330; runtime.py:239-246]. This belongs to T-91 and to O-170's scope; if the ceiling ships covering only the pack's listed fields, T-91 is narrowed and not closed, and the register must say which half remains open.

---

## 5. Control quartet — the two controls this review would make load-bearing

**Control: agent identity revocation as an automatic response (O-171).** The pack's TC-AI-036..038 and TC-OB-014 are well-shaped and I adopt them. I add the legs my conditions require, in the pack's proposed numbering space [A-2 constraint: none of these exists; nothing may cite them as coverage until they do — Source: docs/PO_DECISION_QUEUE.md, PC-S-3].

| Leg | Case I require |
|---|---|
| positive | The bound action runs with a payload carrying `agent`, `correlation_id` and `tenant`; the revocation record joins to the triggering tool call by `correlation_id` (§1.5) |
| negative | `EGRESS_NO_POLICY` revokes nothing (pack TC-AI-036); **and** an agent id that does not resolve to a scoped identity raises `alert.autoaction_failed` rather than revoking a bare string (§1.2) |
| abuse | Pack TC-AI-037; **plus**: two identities in **two different tenants** minted under the same `agent_id` string — revoking one must not deny the other, or the decision must state that cross-tenant revocation is intended (§1.2) |
| recovery | **A built `restore_agent`**: a single approver is refused, two distinct named approvers succeed, the restore emits its own audit event, and the restored identity's allowlisted calls work after a restart (§1.3). This leg cannot be waived; without it the control has no recovery. |

**Control: the registry ceiling (O-170).** The pack's TC-AI-032..035 are the right four. I add to the abuse leg: a registry that **omits `canary_tokens`** and one that sets `input_schema` to an empty object must each be refused (G-1, G-2); and to the negative leg: a ceiling row with no declared comparator must be refused, not defaulted (G-4).

---

## 6. Verdicts

### O-171 — `mcp.egress_denied` → `revoke_agent_identity` for the `EGRESS_NOT_ALLOWLISTED` case

## CONCUR WITH CONDITIONS

The direction is right, the action only narrows, the Kill Switch options are correctly rejected, and binding it before any handler can raise it is the right sequencing. The blast radius is **narrow on the trading axis and wide on the identity axis** (§1.4), and the action already carries three bindings, so this is a marginal addition and not a novel one (§1.6). **The pack's two preconditions are necessary and not sufficient.** Conditions, in full:

1. **CR-171-1** — I adopt the pack's C-171-1 (payload carries a bare `agent`) **and extend it**: the payload contract must also carry `correlation_id` and `tenant`, both of which exist on the egress decision object and are dropped by `EgressDecision.payload()` [Source: mcp/servers/mcp_servers/egress.py:82-95]. A risk action whose record cannot be joined to its trigger is not evidenceable (§1.5). Owner: Backend Lead.
2. **CR-171-2** — I adopt C-171-2 (the `EGRESS_NO_POLICY` split) unchanged and without exception. Owner: SRE Lead, reviewer me.
3. **CR-171-3 (new, blocking)** — **The revocation key must carry scope.** Either `agent_id` is namespaced and validated per tenant at mint, or the revocation target composes tenant with agent id as `revoke_tool_for_scope` already does [Source: mcp/servers/mcp_servers/allowlist.py:59]. Until then the action is a cross-tenant control keyed on an unvalidated string and the pack's "no other tenant" claim is unsupported (§1.2). Owner: Backend Lead, reviewer MCP Security Agent.
4. **CR-171-4 (new, blocking)** — **A restore path must exist, enforce two distinct named approvers, emit its own audit event, and be exercised by a recovery test, before this auto-action is bound.** Today none of the four is true (§1.3). Owner: Backend Lead (code), MCP Security Agent (semantics), reviewer me. This is not satisfied by the H-19 drill; a drill cannot exercise a restore that is not built.
5. **CR-171-5** — I adopt C-171-4 (the missing `mcp.egress_denied` catalogue row) and **enlarge it to NR-3**: the row is added as part of a reconciliation of `docs/ALERT_CATALOG.md` against `observability/alerts.yaml` by machine name, with a CI check that they agree. Adding one row to a document that is missing five live auto-actions repairs the symptom and leaves the defect (§4, NR-3). Owner: SRE Lead, reviewer me.
6. **CR-171-6** — I adopt C-171-5 (restore stays two-person; exercised in the H-19 drill) with CR-171-4 as its prerequisite.
7. **CR-171-7** — C-171-6 (alert-storm bound) is **narrowed**: revocation is a strictly stronger bound than the per-token deny rate and repeat revocations are idempotent in effect, so the residual is journal growth and pager volume, not control failure (§1.4). Fold it into O-55/O-111 rather than blocking on it. No number is set.
8. **CR-171-8** — This decision and O-172 are taken **together**, with a written incident procedure for changing an auto-action while `alerts.yaml` is pinned (NR-6, §1.7). Owner: SRE Lead, reviewer me.
9. **CR-171-9** — The decision record states the blast radius **as verified in §1.1-1.6**, not as summarised in the pack, and states explicitly that the action reaches no Kill Switch level, no order path, no resting order and no queued intent (§1.4). A blast-radius confirmation that overstates *or* understates is equally unusable to the Trading Risk Committee.

**Fallback position.** If the delegate judges the identity-level radius too large after §1.2, `revoke_tool_for_scope` (the pack's Option B) is the right narrower choice and its payload requirement is already known [Source: apps/web/web_bff/platform.py:1383]. I would not accept Option A (`none`) as the permanent answer once a handler can perform I/O, and I concur with the pack that no Kill Switch action is acceptable here in any form.

### O-170 — the approved catalogue as machine-checkable ceilings, enforced at load

## CONCUR WITH CONDITIONS

The mechanism is the right control and it is the same control I own in `docs/LIMIT_MATRIX.md` expressed for one artefact: a higher-level bound that a lower level cannot widen, enforced where the value becomes effective, with the bound owned by someone other than the author of the thing it bounds. Confidence **high** on the mechanism; **none** on any value, and I set none. Conditions:

1. **CR-170-1** — I adopt C-170-1..C-170-6 unchanged. C-170-2 and C-170-3 (the CODEOWNER pair, and the ceiling module not owned by the seat that owns the registry) are the maker-checker requirement and are non-waivable from my seat.
2. **CR-170-2 (new)** — The ceiling must cover **`canary_tokens` (minimum content, not merely well-formedness) and `input_schema` (a schema that constrains, not an empty object)**. Both are widenable today by a validly signed registry without touching any number, and `canary_tokens` silently disables a control that already carries an auto-action (G-1, G-2). If they are excluded, the decision must say so and the register must record that T-91 is narrowed, not closed (NR-7).
3. **CR-170-3 (new)** — The decision must state whether **aggregate ceilings** (`tenant_ceiling_per_minute`, `deny_limit_per_minute`, today constructor defaults with no catalogue row and no approval record [Source: mcp/servers/mcp_servers/runtime.py:88-89]) are in scope. If not, it must name the item that carries them, so that "the registry is ceiling-checked" is never read as "MCP call volume is bounded" (G-3). No value is set here or implied.
4. **CR-170-4 (new)** — **The comparator is declared data per field, and a row without one is refused** — the O-174 rule, already adopted on this programme (G-4). No override or exemption field may exist: `effective = min`, with no escape hatch.
5. **CR-170-5 (new)** — A ceiling change is a limit change: **maker-checker *and* a cooling period on any widening**, per `docs/RISK_POLICY.md:38`, which the pack omits. Narrowing may be immediate. The cooling period's length is a Trading Risk Committee recommendation and a Product Owner decision [Open: O-07]; **I name no length.** A ceiling change emits `limit.changed` [Source: observability/alerts.yaml:28].
6. **CR-170-6 (new)** — `RegistryOverCeiling` subclassing `RegistryUnsigned` is right for fail-closed and must not present a ceiling breach to an operator as a signature forgery; the two have opposite recoveries. The reason code must be structurally distinguishable and the operator wording is the Support & Training Lead's and Frontend Lead's (CROSS-2, the O-166 defect class).
7. **CR-170-7 (new)** — The numbers are set by the process at §2.3: joined to O-07, owner and basis before value, direction before number, the interim seed labelled a freeze of a fixture and not an approval, recommended by the Trading Risk Committee and decided by the Product Owner in `docs/DECISION_LOG.md` with the values landing in `docs/LIMIT_MATRIX.md`. **Never first in code and never first in the catalogue.**
8. **CR-170-8** — No document may cite TC-AI-030 as evidence that T-91 is closed (§2.1, pack §8.1), and no ceiling check may be reported as tool approval (O-35 is untouched).

### O-172 — per-file digest pins now, a separately signed policy manifest as the target; not the registry signature

## CONCUR WITH CONDITIONS

The risk is correctly characterised, the rejection of Option A is right and rests on the artefact's own approval semantics, and B-then-C is the right sequencing. The window before shadow is **acceptable**, because the alternative is shipping into shadow with nothing while waiting on a human ceremony with no date — but only under all of the following. Conditions:

1. **CR-172-1** — I adopt C-172-1..C-172-6 unchanged. C-172-6 (RT-08 run by a seat that did not specify it) is the one I would not trade.
2. **CR-172-2 (new)** — **`observability/alerts.yaml` is pinned first**, and the register records why: it is the only one of the four whose content is a control decision, and a single edit to it can set `killswitch_platform`, `revoke_agent_identity` and `revoke_tool_for_scope` bindings to `none` with no signature to forge (§3.1). The other three are grants or an unenforced declaration.
3. **CR-172-3 (new)** — C-172-1's residual statement must name `alerts.yaml` **specifically**: for that file the actor who can edit it and the actor who controls the start-up environment are largely the same, so the interim raises the attacker's cost least for the file that matters most (T-92, RT-10). "Pinned" must not be allowed to read as "protected" for it.
4. **CR-172-4 (new)** — The interim covers **all four kinds of file before shadow**, not a subset, and the residual is **recorded as accepted by the Product Owner with a named owner and a review date** — not inherited by silence (§3.2 (a), (c)).
5. **CR-172-5 (new)** — This decision and O-171 are taken together with the incident procedure required by CR-171-8 (NR-6).
6. **CR-172-6** — No document, gate pack or board minute describes T-90 or RT-08 as closed by the interim (§3.2 (d)); and per the pack's §8.8, the register must not let "pinned" read as "enforced" for `runtime.yaml`, which no runtime reads [Open: H-05, MSA-3].

---

## 7. Assumptions, confidence, provenance

- **A-1 [Source: this worktree at `0510dd0`, 2026-09-09]** Every `[Source: path:line]` above is a file I read today. The diff `442cebd..0510dd0` touches documents only; no code the pack cites has changed.
- **A-2 [Committee]** I ran no test and edited no file other than this review. Every test id named here is **proposed** and none exists; no document may cite them as coverage until they do [Source: docs/PO_DECISION_QUEUE.md, PC-S-3].
- **A-3 [Open]** **I set no number.** Every ceiling value, cooling period, storm bound, aggregate quota, staleness figure and cadence remains undecided; the source that would settle them is a Trading Risk Committee recommendation decided by the Product Owner and recorded in `docs/LIMIT_MATRIX.md` and `docs/DECISION_LOG.md` [Open: O-07].
- **A-4 [Open]** Nothing here is verified against a deployed topology, a KMS, a real tenant, a real broker or a handler that performs I/O — none exists. The operational cost of O-171 is therefore unmeasured, exactly as the pack states, and my "medium" confidence on that point is the same as the pack's "low".
- **A-5 [Committee]** I am the reviewing seat and I approve nothing. I did not author the pack and have not edited it. `docs/RISK_POLICY.md` and `docs/LIMIT_MATRIX.md` are unchanged by this review; the process at §2.3 is a recommendation to the Trading Risk Committee and the Product Owner, not an amendment.
- **Confidence:** O-170 **high** on the mechanism and its placement, **high** on G-1/G-2 (mechanical, read from the schema and the loader), **none** on values. O-171 **high** on the blast-radius findings §1.2 and §1.3 (both mechanical and both confirmed by the absence of any call site or test), **medium-high** on the direction, **medium** on the operational cost. O-172 **high** on the `alerts.yaml` ranking, **medium-high** on rejecting Option A, **medium** on the window judgement, which is a sequencing opinion and not a measurement.
- **Provenance:** docs/SESSIONS/COUNCIL_2026-09-09_O-170_O-172_mcp_security_agent.md; docs/RAID_LOG.md:15, :52, :98, :135, :184, :187, :195, :198, :202, :226, :231-233, O-166, O-174; docs/RISK_POLICY.md; docs/LIMIT_MATRIX.md; docs/ALERT_CATALOG.md; docs/MCP_TOOL_CATALOG.md; docs/PO_DECISION_QUEUE.md; docs/THREAT_MODEL.md:108-109; docs/RED_TEAM_PLAN.md:27-31; docs/TEST_CASES/TC-AI.md; observability/alerts.yaml; observability/rtobs/alerts.py; mcp/policies/README.md; mcp/policies/tool_registry.json; mcp/servers/mcp_servers/{identity,revocation,runtime,egress,allowlist,registry,tools}.py; apps/web/web_bff/platform.py; apps/cli/rt365_cli/main.py; scripts/verify_tool_registry.py; libs/core/rtcore/trust.py; test/quartets/{test_tc_ai_mcp,test_tc_ai_egress_trust,test_tc_ten_tenancy,test_tc_ks_killswitch}.py; .github/CODEOWNERS.
