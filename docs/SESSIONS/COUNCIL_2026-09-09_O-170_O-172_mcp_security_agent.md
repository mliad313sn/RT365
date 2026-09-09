# /goal — Decision pack O-170 / O-171 / O-172: what a signed registry may **say**, what an egress denial **does**, and what covers the **policy files** beside the registry

> **Where this file should live, and why it does not.** This is the decision pack commissioned for `goals/decisions/O-170_O-172_decision_pack.md`. The write-scope guard refused that path for this seat — `agent_guard: agent 'mcp-security-agent' may not edit goals/decisions/O-170_O-172_decision_pack.md` [Source: .claude/agents/roster.json:280-290; scripts/agent_guard.py] — and this seat did not route around the guard through Bash. The pack is therefore filed in `docs/SESSIONS/`, which this seat owns. Moving or copying it to `goals/decisions/` is the delegating role's act, not mine [Committee].

| Prepared by | Reviewer (different line) | Recommending body | Decider | First gate | Status |
|---|---|---|---|---|---|
| MCP Security Agent (2nd line) — prepares, recommends, **never approves** [Source: docs/PRODUCT_OWNER.md:13; docs/MCP_TOOL_CATALOG.md:5] | Security Architect (1st line) for the mechanisms; Chief Risk Agent (2nd line) for every blast radius and every number | Security & Privacy Board (recommends) [Source: docs/PO_DECISION_QUEUE.md:88] | Product Owner / delegate under D-040 [Source: docs/PRODUCT_OWNER.md:22] | O-170, O-171: Gate C; O-172: Gate C (shadow) [Source: docs/RAID_LOG.md:231-233] | **Pack ready — nothing here is approved, decided or signed** |

**Reading rules for this pack.** Every statement carries `[Source: path:line]` (a fact read from this tree at `442cebd`, 2026-09-09), `[Committee]` (an opinion or a recommendation of this seat) or `[Open]` (not established anywhere; the source that would settle it is named). No number in this pack is proposed as an approved threshold. Nothing here authorises promotion beyond dev/sim, and nothing here is a regulatory, broker, vendor or licensing statement. Profit is an objective, never a promise [Source: CLAUDE.md:3].

---

## 0. The three questions, one sentence each

| Item | Question to close |
|---|---|
| **O-170** | Should the approved tool catalogue become machine-checkable **ceilings per tool** (quota, payload limit, timeout, masking, and — proposed — class and output provenance) that a verifier and the registry loader compare a loaded registry against, so that a *validly signed* registry which widens a limit is refused? |
| **O-171** | What auto-action, if any, does `mcp.egress_denied` carry — decided explicitly, rather than `none` winning by silence? |
| **O-172** | Before shadow: does the registry signature cover the policy directory, does each policy file get its own pin, or does a separate signed policy manifest cover them — and who owns it? |

The RAID rows as written [Source: docs/RAID_LOG.md:231, :232, :233]; their origin is the E09 builder's escalation E09-PO-4/5/6 [Source: docs/SESSIONS/BUILD_E09_2026-09-08_egress_and_trust_anchor.md:205-207] and the red team's rows T-90 and T-91 [Source: docs/THREAT_MODEL.md:108-109] and case RT-08 [Source: docs/RED_TEAM_PLAN.md:27].

---

## 1. O-170 — the registry's **contents** are unchecked

### 1.1 What is true today

1. The verifier checks the registry's **shape**, not its **values**: the six allowed names [Source: scripts/verify_tool_registry.py:59-69], exactly one write-class tool [Source: scripts/verify_tool_registry.py:70-72], the write tool's scope containing the word "queue" [Source: scripts/verify_tool_registry.py:73-74], and that quota, timeout and payload limit are **positive** [Source: scripts/verify_tool_registry.py:85-87]. Positive is the only constraint on any number.
2. The schema behind the loader enforces the same floor and no ceiling: `"minimum": 1` on `quota_per_minute`, `timeout_s` and `payload_limit_bytes`, and `masking` is a free `"type": "string"` [Source: mcp/servers/mcp_servers/registry.py:84-86, :83].
3. `tool_registry.json` is compared with the signed copy [Source: scripts/verify_tool_registry.py:55-58] — which, as the builder reported, a forger who re-signs both files satisfies [Source: docs/SESSIONS/BUILD_E09_2026-09-08_egress_and_trust_anchor.md:205].
4. The catalogue states in terms that its numbers are not thresholds: "No number in this catalogue is a decided threshold: quotas, timeouts and payload limits are the fixture registry's values [Open]" [Source: docs/MCP_TOOL_CATALOG.md:47].
5. The values live only in the signed artefact: `submit_trade_intent` = `write`, quota 10/min, timeout 2 s, payload 32768 B, masking `none` [Source: mcp/policies/tool_registry.json:361-368]; `read_account_state` masking `identifiers masked; balances rounded per policy` [Source: mcp/policies/tool_registry.json:90]. The loader turns those integers into a `ToolSpec` with no comparison at all [Source: mcp/servers/mcp_servers/registry.py:309-326], and the runtime then enforces exactly what the artefact said — quota [Source: mcp/servers/mcp_servers/runtime.py:231-232], payload [Source: mcp/servers/mcp_servers/runtime.py:236-237], deadline [Source: mcp/servers/mcp_servers/runtime.py:254].
6. The same policy checks are **duplicated**, not shared: `rt365 check` re-implements the six-name, write-class, egress and runtime checks in its own code [Source: apps/cli/rt365_cli/main.py:110-125] alongside `scripts/verify_tool_registry.py:59-84`. Any ceiling check written in one of the two exists in one of the two.
7. `docs/MCP_TOOL_CATALOG.md` has **no CODEOWNERS entry**; `/mcp/policies/` is owned by this seat alone [Source: .github/CODEOWNERS:8, whole file read 2026-09-09]. So the document that would become the ceiling is editable without 2nd-line approval, and the directory that would hold a ceiling file is owned by the same seat that owns the catalogue.
8. The catalogue's ceiling-bearing column is prose, not data: "per-tenant quota, 2s, 1 MB", "rate limit per strategy, 2s, 32 KB", masking "—" for four tools [Source: docs/MCP_TOOL_CATALOG.md:13-18], while the registry carries one integer per tool and the runtime keys the window by `(tenant, account, strategy, tool)` [Source: mcp/servers/mcp_servers/runtime.py:231]. The prose numbers happen to equal the fixture's numbers today (compare docs/MCP_TOOL_CATALOG.md:13-18 with mcp/policies/tool_registry.json:16-18, :91-93, :178-180, :246-248, :324-326, :366-368), but the scope words have no field to land in [Committee; the quota-keying defect is REVIEW_C3 F-06, Source: docs/SESSIONS/REVIEW_C3_mcp_security_agent.md:115, tracked as O-33].

### 1.2 Options

| # | Option | What it costs | What it breaks / does not cover |
|---|---|---|---|
| **A** | **Do nothing; rely on the key and the anchor.** Record that the signature plus the trust anchor is the whole control. | Nothing to build. | Leaves T-91 open with no control at all [Source: docs/THREAT_MODEL.md:109]. Every insider or process that can obtain a legitimate signature — the dev HMAC key today [Source: mcp/policies/README.md:3], the ceremony key after H-20 — can widen the write tool's quota, payload limit and any masking string, and nothing in the platform notices. It also makes the key ceremony (H-20) the single control for two different questions ("who may publish a registry" and "what may a registry say"), which is exactly the concentration blueprint 13 separates [Committee]. |
| **B** | **Ceiling table as a *data file* beside the registry** (e.g. `mcp/policies/ceilings.yaml`), compared by `scripts/verify_tool_registry.py`. | Small: one file, one loop in the verifier. | The ceiling then lives in the same directory, with the same owner [Source: .github/CODEOWNERS:8], as the artefact it constrains — an attacker or a mistaken edit that reaches one reaches both, and it inherits O-172 wholesale (an unsigned, unpinned YAML) [Source: docs/RAID_LOG.md:233]. It also refuses only where the verifier runs (`make policy-check`, CI) [Source: Makefile:27-30; .github/workflows/ci.yml:33], never on the serving path: a widened registry still loads in a running process. |
| **C** | **Ceiling table compiled into the build, checked at load** — the catalogue stays the human record; a module (proposed `mcp_servers/ceilings.py`, the Backend Lead's file, new CODEOWNER pair) carries the same table as code; `load_registry` refuses a registry that exceeds it, so no widened `ToolSpec` is ever produced; the verifier and `rt365 check` report field by field; a CI check refuses any divergence between the catalogue table and the module. | Largest of the three: a loader change, a module, a catalogue table rewritten from prose to data, a CI equality check, two CODEOWNERS lines, and a quartet. Every legitimate widening becomes a code change with a review — deliberately. | Does not defend against whoever can change the build (that boundary is code review, CODEOWNERS and artefact signing — O-83, H-30) [Committee]. Does not decide any number: the values remain the Chief Risk Agent's and the Product Owner's [Open]. Makes an honest widening slower; a developer who raises a quota locally now fails `make policy-check` until the table and the catalogue move together. |

### 1.3 Recommendation — Option C, with conditions

**Recommend Option C** [Committee]. Confidence: **high** on the mechanism (it is the same fail-closed pattern already built and tested for the trust anchor [Source: mcp/servers/mcp_servers/registry.py:106-111; docs/TEST_CASES/TC-AI.md:14, :19]); **none** on any value, which is not mine to set.

Conditions, all of which must hold before this is called done:

- **C-170-1** The ceiling **values** are decided by the Chief Risk Agent with the Product Owner, not by this seat and not by the builder [Source: docs/RAID_LOG.md:231]. Until that decision exists, the honest seed is *"no wider than the values committed at `442cebd`"*, quoted from mcp/policies/tool_registry.json:16-18, :91-93, :178-180, :246-248, :324-326, :366-368 — freezing an existing artefact value, **not** approving a threshold. The catalogue must keep saying that no number in it is a decided threshold [Source: docs/MCP_TOOL_CATALOG.md:47] until a risk decision replaces that sentence.
- **C-170-2** `docs/MCP_TOOL_CATALOG.md` becomes a protected path with a CODEOWNER pair (proposed: Chief Risk Agent + MCP Security Agent), because a ceiling nobody must approve to change is not a ceiling [Source: .github/CODEOWNERS — no entry exists; Committee].
- **C-170-3** The ceiling module is **not** under `/mcp/policies/` and not owned by this seat alone; author ≠ approver applies to the ceiling exactly as it applies to the tools [Source: docs/MCP_TOOL_CATALOG.md:5].
- **C-170-4** A ceiling breach must fail closed for **every** caller. Because the CLI, the verifier, the stdio host and the composition root all catch `RegistryUnsigned` [Source: scripts/verify_tool_registry.py:32-34; apps/cli/rt365_cli/main.py:100-104], the new error is a **subclass** of it, the way `TrustAnchorRefused` already is [Source: mcp/servers/mcp_servers/registry.py:106-111].
- **C-170-5** The catalogue's prose column becomes structured data, and the two open interpretations are recorded rather than silently resolved: masking "—" in the catalogue [Source: docs/MCP_TOOL_CATALOG.md:15-18] versus `"none"` in the registry [Source: mcp/policies/tool_registry.json:177, :245, :323, :365]; and the quota **scope** words ("per-tenant", "per-account", "per strategy") which have no field in the registry today [Source: docs/MCP_TOOL_CATALOG.md:13-18 vs mcp/servers/mcp_servers/registry.py:63-77] — that is O-33's territory and this decision must not pretend to close it [Open: O-33].
- **C-170-6** This is registration hygiene, not registration: O-35 (no tool is approved) is untouched, and a ceiling check must never be reported as an approval of the six tools [Source: docs/MCP_TOOL_CATALOG.md:7, :22].

### 1.4 The exact shape of the ceiling check

**(a) Which fields become ceilings, and in which direction.** A "ceiling" is not always a maximum; each field carries its comparator, and the registry value must satisfy it *against the catalogue row for that tool*:

| Catalogue field (docs/MCP_TOOL_CATALOG.md:11-18) | Registry field [Source: mcp/servers/mcp_servers/registry.py:63-94] | Comparator | Note |
|---|---|---|---|
| Quota (number part) | `quota_per_minute` | `registry <= ceiling` | The scope word ("per-tenant" / "per-account" / "per strategy") is **not** checkable until a scope field exists [Open: O-33] |
| Timeout | `timeout_s` | `registry <= ceiling` | Reminder for the reader: the deadline is caller-side, not pre-emptive [Source: docs/MCP_TOOL_CATALOG.md:44] |
| Payload | `payload_limit_bytes` | `registry <= ceiling` | |
| Masking | `masking` | `registry` must be **no weaker than** the catalogue class | Requires a closed, ordered set of masking classes; until that exists, the only honest comparator is **exact equality** with the catalogue string [Committee] |
| Class | `class` | `registry == ceiling` (`write` only for `submit_trade_intent`) | Moves the check that exists in two places [Source: scripts/verify_tool_registry.py:70-72; apps/cli/rt365_cli/main.py:112-113] onto the load path |
| Scope | `scope` | `registry == ceiling` (and, for the write tool, must still name the queue) | Keeps scripts/verify_tool_registry.py:73-74 |
| Output provenance (**proposed addition to the catalogue**) | `output_provenance` | `registry ∈ allowed set for that tool` | A registry that relabels a tool's output as trusted-for-decisions is an injection-defence failure, and nothing checks it today [Source: mcp/servers/mcp_servers/registry.py:91-94 permits any of six values for any tool] [Committee] |
| Owner, approval record | `owner`, `approval_record` | not ceilings — **bindings**: the approval record must match the DECISION_LOG entry for that tool once O-35 closes | Today every record reads "pending" and the signer refuses to sign non-fixture content while it does [Source: mcp/servers/mcp_servers/registry.py:229-239] |
| The tool set itself | `tools[].name` | exactly the six, no more, no fewer | Already enforced in three places [Source: mcp/servers/mcp_servers/registry.py:45-47, :79; scripts/verify_tool_registry.py:59-69; apps/cli/rt365_cli/main.py:31-33] |

**(b) Where the comparison belongs.** Both places, with different jobs:

- **`mcp/servers/mcp_servers/registry.py`, inside `load_registry`, after signature verification and before the `ToolSpec` dict is built** [Source: mcp/servers/mcp_servers/registry.py:296-326] — this is the load-bearing half. Every path to a tool goes through it (CLI, verifier, stdio host, BFF composition; there is no third path to a tool [Source: docs/MCP_TOOL_CATALOG.md:41]), so a widened `ToolSpec` is never constructed — the property TC-AI-030 already asserts for the *outsider* case [Source: test/quartets/test_tc_ai_egress_trust.py:419-424].
- **`scripts/verify_tool_registry.py` (and `rt365 check`)** — the human-readable half: report every field with its value, its ceiling and the ceiling's source, so CI names what exceeded rather than only that something did [Source: scripts/verify_tool_registry.py:88-93; apps/cli/rt365_cli/main.py:110-126]. Because these two duplicate each other today (§1.1.6), the comparison itself must live in **one** module both import; a check written only in the script is invisible to a running process, and a check written only in the CLI is invisible to CI.
- **Not** in `mcp/policies/`: the ceiling must not be an artefact that the actor who can rewrite the registry can rewrite in the same act [Committee].

**(c) The refusal.** Reason codes follow the existing hyphenated, prefix-by-concern convention of the trust anchor (`TRUST-ANCHOR-ABSENT`, `-ADJACENT`, `-UNPINNED`, `-PIN-MISMATCH`, `-PURPOSE`, `-MALFORMED`) [Source: libs/core/rtcore/trust.py:186-206; mcp/servers/mcp_servers/registry.py:190-201]:

| Proposed code | Raised when | Message must carry |
|---|---|---|
| `REGISTRY-CEILING-EXCEEDED` | a numeric field is wider than its ceiling | tool, field, registry value, ceiling, ceiling source (module + catalogue row) |
| `REGISTRY-CEILING-WEAKER` | masking, class, scope or output provenance is weaker than / different from the ceiling row | tool, field, both values |
| `REGISTRY-CEILING-ABSENT` | the registry names a tool with **no** ceiling row | tool name — an unknown tool has no ceiling, so it is refused, never defaulted |
| `REGISTRY-CEILING-UNPINNED` *(only if the ceiling is ever externalised to a file)* | the ceiling source is absent or does not match its pin | path, digest, expected digest |

All raised as a proposed `RegistryOverCeiling(RegistryUnsigned)`, so every existing caller keeps failing closed with no change — the pattern `TrustAnchorRefused` already uses and documents [Source: mcp/servers/mcp_servers/registry.py:106-111].

**(d) Ownership of the work.** The loader and the module are the **Backend Lead's** files; this seat may not author an MCP server [Source: .claude/agents/mcp-security-agent.md "YOU MAY NOT: author MCP servers"]. The catalogue table and the reason-code semantics are this seat's; the values are the Chief Risk Agent's; the CODEOWNERS lines are the Security Architect's / Product Owner's; nobody approves their own [Committee].

### 1.5 What test would prove it (proposed ids in the existing TC-AI area; highest existing id is TC-AI-031 [Source: docs/TEST_CASES/TC-AI.md:27])

| Quartet | Proposed id | Case |
|---|---|---|
| positive | **TC-AI-032** | The committed registry, at or below every ceiling, loads unchanged; `verify_tool_registry.py` prints each field with its value, its ceiling and the ceiling's source; the six `ToolSpec`s are identical to today's. |
| negative | **TC-AI-033** | A ceiling table that is absent, that omits a tool present in the registry, or that is malformed refuses with `REGISTRY-CEILING-ABSENT`; the refusal is a `RegistryUnsigned`, so the CLI, the verifier and the composition root all still fail closed. |
| abuse | **TC-AI-034** | The T-91 case with a **trusted** key (not the outsider key of TC-AI-030): a registry signed by a key in the trust set that sets `submit_trade_intent` quota to 100000/min, payload to 10 MB, `read_account_state` masking to `none` and an output provenance the tool is not entitled to, is refused with `REGISTRY-CEILING-EXCEEDED` / `-WEAKER`; **no widened `ToolSpec` is produced**; and the same registry is refused by `make policy-check` and by `rt365 check`. |
| recovery | **TC-AI-035** | A legitimate ceiling change is **one reviewed act**: catalogue row and compiled table change together (CI refuses divergence), after which the previously refused registry loads and the previous ceiling no longer admits anything; reverting the table alone re-refuses. |

---

## 2. O-171 — `mcp.egress_denied` fires and nothing happens

### 2.1 What is true today

1. `mcp.egress_denied` is catalogued S1 with `auto_action: none`, runbook "credential compromise" [Source: observability/alerts.yaml:26]; `plane.deny` — the same class of event on the network side — is S1 with `revoke_agent_identity` [Source: observability/alerts.yaml:5].
2. `revoke_agent_identity` revokes the agent by `agent_id` and journals it [Source: apps/web/web_bff/platform.py:1379-1382; mcp/servers/mcp_servers/identity.py:197-199]; the revocation survives a restart [Source: docs/TEST_CASES/TC-AI.md:29, TC-AI-008]. Restoring is a two-person act [Source: mcp/policies/README.md:11].
3. **The payload does not fit either strong auto-action.** The egress alert payload carries `host, reason_code, pattern, policy, actor, tool, allowed` [Source: mcp/servers/mcp_servers/egress.py:86-95, :172]; `actor` is the string `"agent:<agent_id>"`, not a bare id [Source: mcp/servers/mcp_servers/runtime.py:207, :250]. `revoke_agent_identity` requires the key `agent` [Source: apps/web/web_bff/platform.py:1382] and `revoke_tool_for_scope` requires `tool, account, strategy` [Source: apps/web/web_bff/platform.py:1383]. A missing key does not silently no-op — it raises `alert.autoaction_failed` (S1, no action) [Source: observability/rtobs/alerts.py:101-115; observability/alerts.yaml:24]. **So binding a strong auto-action today would produce a second S1 and revoke nothing.**
4. **One alert name covers two very different events.** `EGRESS_NOT_ALLOWLISTED` (a handler asked for a destination the allowlist does not name) and `EGRESS_NO_POLICY` (no policy is loaded at all — a deployment fault) raise the *same* alert [Source: mcp/servers/mcp_servers/egress.py:148-172, :35-38], and the router keys auto-actions on the alert **name** only [Source: observability/rtobs/alerts.py:90, :101]. A strong action bound to the name therefore also fires on a missing or unreadable policy file.
5. Nothing can raise it today from a shipped handler: no MCP handler performs network I/O and none can [Source: mcp/servers/mcp_servers/egress.py:7-14; docs/TEST_CASES/TC-AI.md:18, TC-AI-026]. The guard is the seam a *future* handler would use.
6. The standing rule for any auto-action: "an auto-action may halt, suspend, revoke, cancel or narrow; it may never approve, enable, widen or resume" [Source: docs/ALERT_CATALOG.md:36].
7. **`mcp.egress_denied` has no row in `docs/ALERT_CATALOG.md`** even though `observability/alerts.yaml` declares itself a mirror of it [Source: observability/alerts.yaml:1; docs/ALERT_CATALOG.md:7-26, read in full 2026-09-09 — no egress row].

### 2.2 Options

| # | Option | Blast radius | What it costs | What it breaks |
|---|---|---|---|---|
| **A** | **`none` — page only**, but decided rather than inherited, with the reason written into the catalogue row. | Zero automatic effect. The call is already refused and nothing egresses [Source: mcp/servers/mcp_servers/egress.py:171-176]. | Nothing to build except the missing catalogue row. | Leaves the asymmetry the builder flagged: an S1 that stops nothing, in a control whose whole claim is "forbidden means structurally impossible" [Source: docs/SESSIONS/BUILD_E09_2026-09-08_egress_and_trust_anchor.md:206]. A handler that probes destinations in a loop is bounded only by the per-token deny rate on *subsequent* calls [Source: mcp/servers/mcp_servers/runtime.py:214-215, :226]. |
| **B** | **`revoke_tool_for_scope`** — revoke the offending tool's grant for that (tenant, account, strategy). | Narrowest useful: one tool, one strategy, one account, one tenant [Source: apps/web/web_bff/platform.py:1352-1366]. | Payload must gain `account` and `strategy` (the runtime has them in `scope` [Source: mcp/servers/mcp_servers/runtime.py:209] and does not pass them to the guard [Source: mcp/servers/mcp_servers/runtime.py:250]). | An identity that tried to reach a forbidden destination keeps its other five tools and its identity. If the cause is a compromised or injected agent, revoking one grant is close to no response [Committee]. It also inherits the tenant-availability concern already recorded for grant revocation by alert [Source: docs/PO_DECISION_QUEUE.md:158, PC-E01-6]. |
| **C** | **`revoke_agent_identity`, matching `plane.deny`** — and split the deployment fault out under its own name (proposed `mcp.egress_no_policy`, S1, `none`). | The agent identity is refused everywhere it acts, across a restart, until a two-person restore [Source: mcp/servers/mcp_servers/identity.py:197-199; mcp/policies/README.md:11]. Nothing else: no Kill Switch, no order path, no other tenant, no other agent. | Payload must carry a bare `agent` key; a second catalogued alert name and its router row; a catalogue row for both; a quartet. | Costs analysis capability for that agent immediately on a single event, so a false positive (a mis-typed host in a future handler) takes the agent out until two humans restore it. Requires the `EGRESS_NO_POLICY` split, or a missing policy file becomes a revocation storm. |
| **D** | **A Kill Switch auto-action** (`killswitch_account` / `killswitch_platform`). | Largest of any catalogued alert [Source: docs/RAID_LOG.md:198, O-137]. | — | **Not recommended in any form** [Committee]: an egress denial says an identity asked for something it may not have; it says nothing about order flow, and the account in the payload is not necessarily the account at risk. It would also let a low-privilege loop halt the platform — precisely red-team case RT-09 [Source: docs/RED_TEAM_PLAN.md:29]. |

### 2.3 Recommendation — Option C, split by reason code, with conditions

**Recommend Option C** [Committee]: `mcp.egress_denied` (the `EGRESS_NOT_ALLOWLISTED` case) carries **`revoke_agent_identity`** at S1, matching `plane.deny`; the `EGRESS_NO_POLICY` case moves to its own catalogued alert at S1 with `auto_action: none` (page; restore the policy, then serve). Confidence: **medium-high** on the direction (the event class is identical to `plane.deny`, the action only ever narrows, and nothing can raise it today, so the action would be in place *before* the first handler that could ask); **low** on the operational cost, because there is no notification channel, no acknowledgement path and no drill record anywhere [Source: docs/ALERT_CATALOG.md:33-34; mcp/policies/README.md:13].

Conditions:

- **C-171-1** No auto-action is bound until the payload contract carries what the action requires — a bare `agent` id (and, if Option B is preferred instead, `account` and `strategy`). Binding first produces `alert.autoaction_failed` and revokes nothing [Source: observability/rtobs/alerts.py:103-115]. Owner of the payload change: **Backend Lead** (`mcp_servers/egress.py`, `runtime.py`); this seat may not author it.
- **C-171-2** The `EGRESS_NO_POLICY` split is part of the decision, not a later refinement: without it, deleting `mcp/policies/egress.yaml` revokes every agent that makes a call [Source: mcp/servers/mcp_servers/egress.py:149-151, :171-172]. Owner: **SRE Lead** (alert catalogue and `observability/alerts.yaml`), reviewer Chief Risk Agent.
- **C-171-3** The Chief Risk Agent confirms the blast radius deliberately, as O-137 asks for the audit-halt case [Source: docs/RAID_LOG.md:198]; this seat recommends and does not decide it.
- **C-171-4** `docs/ALERT_CATALOG.md` gains the missing `mcp.egress_denied` row in the same act [Source: docs/ALERT_CATALOG.md:7-26], because the yaml claims to mirror it [Source: observability/alerts.yaml:1].
- **C-171-5** Restore stays a two-person act, and the revocation is exercised in the emergency revocation drill that has never been run [Source: mcp/policies/README.md:10-22; Open: H-19].
- **C-171-6** Alert-storm bound: a handler may call the guard many times inside one call, and each denial alerts [Source: mcp/servers/mcp_servers/egress.py:166-176]. Revocation is idempotent in effect but not in the journal; the router-side bound is the SRE Lead's to specify [Open].

### 2.4 What test would prove it

| Quartet | Proposed id | Case |
|---|---|---|
| positive | **TC-OB-014** (highest existing TC-OB is 013 [Source: docs/TEST_CASES/TC-OB.md]) | The catalogued `mcp.egress_denied` row resolves to a **bound** auto-action with a **complete** payload: the router runs it and `alert.autoaction_failed` is not raised. |
| negative | **TC-AI-036** | `EGRESS_NO_POLICY` raises the deployment alert, **revokes nothing**, and the agent's next allowlisted tool call still succeeds once the policy is restored. |
| abuse | **TC-AI-037** | A handler that asks for a forbidden destination has its identity revoked; every subsequent tool call by that agent is refused, **including after a runtime restart**; no other agent, tenant, account or tool is affected; no Kill Switch level is engaged. |
| recovery | **TC-AI-038** | A single approver cannot restore the identity; two distinct named approvers can; after restore the same agent's allowlisted calls work and the egress policy itself is unchanged (the property TC-AI-027 asserts for the policy [Source: docs/TEST_CASES/TC-AI.md:26]). |

---

## 3. O-172 — the unsigned policy files beside the signed artefact

### 3.1 What is true today

1. Four kinds of file are loaded as plain YAML at start-up: `mcp/policies/egress.yaml` [Source: apps/web/web_bff/platform.py:1123; mcp/servers/mcp_servers/egress.py:48-51], `mcp/policies/runtime.yaml` (read only by the two checkers, never by the runtime) [Source: scripts/verify_tool_registry.py:79-84; apps/cli/rt365_cli/main.py:118-123], `mcp/policies/allowlist.<tenant>.yaml` [Source: mcp/servers/mcp_servers/allowlist.py:80-105], and `observability/alerts.yaml` [Source: apps/web/web_bff/platform.py:756].
2. None is signed and none is pinned; only `tool_registry.signed.json` is [Source: mcp/policies/README.md:3-8]. The catalogue says the same for the allowlists [Source: docs/MCP_TOOL_CATALOG.md:34].
3. The per-tenant allowlist **is** an approval record, and the two-person tenant revocation depends on it [Source: mcp/policies/README.md:6; mcp/servers/mcp_servers/runtime.py:221-227].
4. `alerts.yaml` is where O-171's answer would live; an unsigned alert catalogue means the auto-action decided in §2 can be edited back to `none` by anyone who can write the file [Source: observability/rtobs/alerts.py:60-63; Committee].
5. A pinning mechanism already exists, is generic over a "purpose", is tested, and fails closed on absent / unpinned / mismatched / wrong-purpose / malformed [Source: libs/core/rtcore/trust.py:155-206; docs/TEST_CASES/TC-AI.md:10, :14, :27]. The compiled pin table is empty and the operator variable is the only source today [Source: libs/core/rtcore/trust.py:144-147].
6. The bundle already carries `mcp/policies` and `observability/alerts.yaml` as resource-root paths [Source: apps/cli/rt365_cli/main.py:23-29], so a manifest over exactly those paths is expressible with what exists.
7. Residual that no option here closes: whoever controls the process environment controls `RT365_HOME` and the pin variables [Source: docs/SESSIONS/BUILD_E09_2026-09-08_egress_and_trust_anchor.md:204 (T-92); docs/RED_TEAM_PLAN.md:31 (RT-10)].

### 3.2 Options

| # | Option | What it costs | What it breaks |
|---|---|---|---|
| **A** | **Stretch the registry signature over the policy directory**: the signed content gains a manifest of `mcp/policies/*` digests; the loader verifies each file against it. | One envelope change, one re-sign per policy edit. | Couples two different approval cadences and two different meanings. The registry signature carries tool-approval semantics (`approval_record`, `fixture`, "signing would fake approval") [Source: mcp/servers/mcp_servers/registry.py:229-241]; putting a per-tenant allowlist inside it would place an unapproved tenant policy inside an artefact whose signature means the tools are approved — the exact failure the catalogue already warns about [Source: docs/MCP_TOOL_CATALOG.md:34]. It makes **tenant onboarding a signing ceremony**, and it cannot cover `observability/alerts.yaml`, which is outside the directory and owned by the SRE Lead [Source: apps/cli/rt365_cli/main.py:24; docs/ALERT_CATALOG.md:5]. |
| **B** | **Per-file digest pin**, reusing `rtcore.trust`'s purpose-and-pin mechanism: one purpose per policy file, digest in the compiled pin table or named by an operator; absent / unpinned / mismatched fails closed. | Buildable now: no key, no ceremony, existing reason codes and existing test shapes [Source: libs/core/rtcore/trust.py:183-206]. Every legitimate policy edit needs its pin updated in the same reviewed act. | Pins are only as strong as the start-up environment (T-92) [Source: docs/SESSIONS/BUILD_E09_2026-09-08_egress_and_trust_anchor.md:204]. A per-tenant file per tenant means a pin per tenant — workable at one tenant, awkward at many [Committee]. If a `make`-style target ever regenerates pins automatically, the control becomes theatre [Committee]. |
| **C** | **A separate signed policy manifest under its own purpose key** (proposed `rt365.mcp-policy-manifest.v1`): one manifest listing path → sha256 for `mcp/policies/*` **and** `observability/alerts.yaml`, signed in the same ceremony as the registry key but as a distinct purpose; loaders verify the manifest, then each file's digest against it. | A second purpose in the trust set, a manifest artefact with its own CODEOWNER, a verifier change, packaging (the manifest must travel in the bundle, as the trust anchor must [Source: docs/RAID_LOG.md:202, O-126]) — and it is blocked on the key ceremony, which is a human act [Open: H-20]. | Nothing runs before the ceremony. Adds a second thing that, if lost, stops the platform — the pattern the register already flags [Source: docs/PO_DECISION_QUEUE.md:182, PC-A-4]. |

### 3.3 Recommendation — B now, C as the target; explicitly **not** A

**Recommend**: adopt **Option C as the target shape** — a policy manifest signed under its own purpose, distinct from the registry signature — and **Option B as the interim** that is buildable before shadow without a key: pin `egress.yaml`, `runtime.yaml`, each `allowlist.<tenant>.yaml` and `observability/alerts.yaml` by digest, one purpose each, fail closed on absent / unpinned / mismatched. Explicitly **reject A**: the registry signature must keep meaning "these tools, these ceilings, this approval", and nothing else [Committee]. Confidence: **medium-high** on rejecting A (the argument is the artefact's own approval semantics, which are in code [Source: mcp/servers/mcp_servers/registry.py:238-241]); **medium** on B-then-C (a sequencing judgement, and the ceremony date is not mine); **none** on any deployment claim, because no deployed topology exists [Open: H-05].

Conditions:

- **C-172-1** The interim pin does not close T-90; it raises the attacker's cost from "edit a YAML" to "edit a YAML and the pin, in two files with two owners". The register must say so [Source: docs/THREAT_MODEL.md:108].
- **C-172-2** The pin record's CODEOWNER must differ from the policy files' CODEOWNER, or the same seat authors both halves [Source: .github/CODEOWNERS:8; Committee]. This is the same unresolved separation already recorded for the trust-set file itself [Source: docs/MCP_TOOL_CATALOG.md:29, MSA-9].
- **C-172-3** `runtime.yaml` is a **declaration**, not an enforcement point [Source: docs/MCP_TOOL_CATALOG.md:9; mcp/policies/README.md:8]. Pinning it makes the declaration tamper-evident; it does not make the sandbox real [Open: H-05, MSA-3].
- **C-172-4** Per-tenant allowlists: whether a second tenant ever ships under `mcp/policies` stays O-123 [Source: docs/RAID_LOG.md:184]; this decision must not pre-empt it, and a signed manifest must not become the reason to ship an unapproved tenant policy.
- **C-172-5** `observability/alerts.yaml` is in scope precisely because O-171's answer lives there; its owner is the SRE Lead and the manifest must not silently transfer ownership [Committee].
- **C-172-6** Before shadow, red-team case RT-08 is run against whatever is built [Source: docs/RED_TEAM_PLAN.md:27], by a seat that did not specify it [Source: docs/PO_DECISION_QUEUE.md:186, PC-S-4].

### 3.4 What test would prove it

| Quartet | Proposed id | Case |
|---|---|---|
| positive | **TC-AI-039** | Every pinned policy file at its pinned digest loads; the platform composes; `rt365 check` and `make policy-check` both report the pin source per file. |
| negative | **TC-AI-040** | Absent file, unpinned file, mismatched digest, malformed pin and wrong purpose are each refused with their own reason code, and each refusal stops start-up rather than degrading to "load it anyway". |
| abuse | **TC-AI-041** | RT-08 as a test: adding `vault.security.svc.cluster.local` to `egress.yaml` [Source: mcp/policies/egress.yaml:10], adding a tool to a tenant's grants [Source: mcp/policies/allowlist.tenant-sim.yaml:6-9], flipping `filesystem: read-only` [Source: mcp/policies/runtime.yaml:2] and setting an auto-action to `none` in `alerts.yaml` are each refused **before any tool call**, and no widened grant is ever in memory. |
| recovery | **TC-AI-042** | A legitimate policy change is one reviewed act: file and pin move together, the platform composes, the previous digest no longer loads; and losing the pin fails closed rather than trusting the newer file (the property TC-AI-031 already asserts for the trust anchor [Source: docs/TEST_CASES/TC-AI.md:27]). |
| packaging | **TC-PKG-006** (highest existing TC-PKG is 005 [Source: docs/TEST_CASES/TC-PKG.md]) | The installed wheel and the one-file executable carry the pin record / manifest with the policies, and a bundle without it fails closed. |

---

## 4. Threat-model delta (proposed to the Security Architect, who owns `docs/THREAT_MODEL.md`)

| Row | Change proposed | Basis |
|---|---|---|
| T-91 (masking / quota widening) | Control column becomes: "None today; O-170 recommends a compiled ceiling table compared inside `load_registry`, so no widened `ToolSpec` is constructed; values remain undecided [Open: O-170, C-170-1]". The test column names TC-AI-032..035 **only once they exist** [Source: docs/PO_DECISION_QUEUE.md:185, PC-S-3 — no row may name a test that does not exist]. | docs/THREAT_MODEL.md:109 |
| T-90 (unsigned policy files) | Control column becomes: "Interim proposed: per-file digest pin reusing `rtcore.trust`; target: a separately signed policy manifest; the registry signature is deliberately **not** stretched over the directory [Open: O-172, H-20]". | docs/THREAT_MODEL.md:108 |
| **New (proposed) — auto-action payload mismatch** | An alert whose payload does not satisfy its auto-action's required keys revokes nothing and raises a second S1; today `mcp.egress_denied`'s payload satisfies neither strong action. Control: the payload contract is part of the auto-action decision (C-171-1). | observability/rtobs/alerts.py:103-115; mcp/servers/mcp_servers/egress.py:86-95; apps/web/web_bff/platform.py:1379-1383 |
| **New (proposed) — one alert name, two causes** | `EGRESS_NOT_ALLOWLISTED` (attack) and `EGRESS_NO_POLICY` (deployment fault) share an alert name, so any auto-action bound to the name fires on both. | mcp/servers/mcp_servers/egress.py:148-172; observability/rtobs/alerts.py:90 |
| **New (proposed) — the ceiling record is unprotected** | `docs/MCP_TOOL_CATALOG.md` has no CODEOWNER, and `/mcp/policies/` has a single-seat owner, so the artefact that would define the ceiling and the artefact it constrains share a seat. | .github/CODEOWNERS:8 and the absence of a catalogue line |

---

## 5. Draft decision-record text (for the ledger owner; **no D-id assigned, no approval recorded here**)

1. **O-170** — *Adopt the approved catalogue as machine-checkable ceilings, enforced at load.* Alternatives considered: rely on the signature and the trust anchor (rejected — leaves T-91 with no control and concentrates two questions on one key); a ceiling file beside the registry (rejected — same directory, same owner, unsigned, and off the serving path). Conditions C-170-1..6. **No ceiling value is approved by this decision**; the values are the Chief Risk Agent's with the Product Owner and stay [Open].
2. **O-171** — *`mcp.egress_denied` (not-allowlisted case) carries `revoke_agent_identity`; the no-policy case becomes its own S1 with no auto-action.* Alternatives: keep `none` (rejected — an S1 that stops nothing in the one control whose claim is structural impossibility); `revoke_tool_for_scope` (rejected as the primary — too narrow for a compromised identity, though it remains the fallback if the Chief Risk Agent judges the identity-level radius too large); any Kill Switch action (rejected — disproportionate and a denial-of-service lever, RT-09). Conditions C-171-1..6.
3. **O-172** — *The registry signature does not cover the policy directory; policy integrity is carried by per-file digest pins now and by a separately signed policy manifest before any real tenant.* Alternatives: extend the registry signature (rejected — conflates tool approval with policy integrity and makes tenant onboarding a ceremony); do nothing (rejected — T-90 and RT-08 are open and the egress guard is now load-bearing). Conditions C-172-1..6.

## 6. Artefact edits each recommendation implies, by owning role (**nothing was edited in preparing this pack**)

| Artefact | Edit | Owner | Reviewer (different line) |
|---|---|---|---|
| `docs/MCP_TOOL_CATALOG.md` | Ceiling table as structured data; masking classes; provenance column; the sentence at line 47 replaced only when a risk decision exists | MCP Security Agent | Chief Risk Agent / Security Architect |
| `mcp/servers/mcp_servers/registry.py`, proposed `ceilings.py` | Ceiling comparison in `load_registry`; `RegistryOverCeiling(RegistryUnsigned)`; reason codes | Backend Lead | MCP Security Agent |
| `scripts/verify_tool_registry.py`, `apps/cli/rt365_cli/main.py` | Import the shared comparison; field-by-field report; catalogue/module equality check | Backend Lead | MCP Security Agent |
| `mcp/servers/mcp_servers/egress.py`, `runtime.py` | Egress alert payload carries the scope keys; `EGRESS_NO_POLICY` raises its own alert name | Backend Lead | MCP Security Agent |
| `observability/alerts.yaml`, `docs/ALERT_CATALOG.md` | The decided auto-action; the missing `mcp.egress_denied` row; the new no-policy row | SRE Lead | Chief Risk Agent |
| `libs/core/rtcore/trust.py` (or a sibling), pin record | Policy-file purposes and pins; later, the manifest purpose | Security Architect | MCP Security Agent |
| `.github/CODEOWNERS` | A line for `docs/MCP_TOOL_CATALOG.md`; a line for the ceiling module; a line splitting the pin record from the policy files | Security Architect / Product Owner | Independent Validation |
| `docs/RAID_LOG.md`, `docs/DECISION_LOG.md`, `docs/REQUIREMENTS_TRACEABILITY.md` (FR-09 [Source: docs/REQUIREMENTS_TRACEABILITY.md:19], NFR-SEC-01 [Source: :31]), `docs/THREAT_MODEL.md` | Mark O-170..O-172 "Pack ready"; record the decision; add the test ids **after** they exist | ledger owners | Independent Validation |

## 7. Human acts these decisions depend on

| Act | Why it blocks | Reference |
|---|---|---|
| **H-20** key ceremony (three distinct humans, KMS-held key) | Option C for O-172 cannot start; and until then the registry is HMAC-signed under the published dev key, so in dev/sim whoever can verify can still forge — a ceiling check is the *only* thing that would refuse a widened dev-signed registry | docs/MCP_TOOL_CATALOG.md:27, :29; mcp/policies/README.md:3 |
| **H-19** emergency revocation drill (never run) | C-171-5: an identity-revocation auto-action that has never been drilled is a mechanism, not a capability | mcp/policies/README.md:13; docs/MCP_TOOL_CATALOG.md:32 |
| **O-35** tool registration decision | The ceiling check is hygiene on an artefact whose six tools are still unapproved; nothing here registers or approves a tool | docs/MCP_TOOL_CATALOG.md:7, :22; docs/PO_DECISION_QUEUE.md:38 |
| Chief Risk Agent confirmation of blast radius (O-171) and of every ceiling value (O-170) | Both are risk decisions, not security-mechanism decisions | docs/RAID_LOG.md:231-232 |

## 8. What I found that contradicts, or qualifies, what O-170..O-172 assert

1. **O-170 is accurate, but one half of it is already tested — for a different attacker.** TC-AI-030 forges exactly the described registry (quota 100000/min, payload 10 MB, masking downgraded) and it *is* refused — because the attacker's key is not in the trust set, not because any value is compared to a ceiling [Source: test/quartets/test_tc_ai_egress_trust.py:391-424; docs/TEST_CASES/TC-AI.md:19]. The uncovered case is the **insider or key-holder** case, and that is what TC-AI-034 must exercise. A reader could otherwise cite TC-AI-030 as evidence that T-91 is closed. It is not.
2. **O-170's example tool is the weaker illustration for masking.** `submit_trade_intent` already carries `masking: none` in the committed fixture [Source: mcp/policies/tool_registry.json:365], so "masking off" changes nothing on that tool; the masking downgrade that matters is `read_account_state` [Source: mcp/policies/tool_registry.json:90] — as the E09 packet itself notes [Source: docs/SESSIONS/BUILD_E09_2026-09-08_egress_and_trust_anchor.md:86]. The quota and payload halves of the row are exactly as stated.
3. **O-171 understates the defect: `none` is not merely the inherited answer — no strong auto-action would work if it were bound today.** The egress alert payload carries `actor` (`"agent:<id>"`), not `agent`, and no `account`/`strategy` [Source: mcp/servers/mcp_servers/egress.py:86-95; mcp/servers/mcp_servers/runtime.py:207, :209, :250], while the router's required keys are `agent` and `tool, account, strategy` [Source: apps/web/web_bff/platform.py:1379-1383]. Binding `revoke_agent_identity` now would raise `alert.autoaction_failed` and revoke nothing [Source: observability/rtobs/alerts.py:103-115].
4. **O-171 does not mention that one alert name covers two causes.** `EGRESS_NO_POLICY` — a deployment fault — raises the same alert as an attack [Source: mcp/servers/mcp_servers/egress.py:148-172], and the router dispatches on the name alone [Source: observability/rtobs/alerts.py:90, :101]. Any decision that binds a strong action to the name without splitting it turns a missing file into a revocation storm.
5. **`mcp.egress_denied` is not in `docs/ALERT_CATALOG.md` at all**, although `observability/alerts.yaml` line 1 declares itself a mirror of that document [Source: observability/alerts.yaml:1, :26; docs/ALERT_CATALOG.md:7-26]. The document of record for "what an alert does" does not contain the alert this decision is about.
6. **O-172's `alerts.yaml` is not in `mcp/policies/`**, so no formulation of "the registry signature covers the policy directory" can reach it [Source: apps/web/web_bff/platform.py:756; apps/cli/rt365_cli/main.py:24]. Whatever is decided must name paths, not a directory.
7. **A mis-citation in an artefact I own.** `docs/MCP_TOOL_CATALOG.md:34` attributes "a signature over per-tenant allowlists before any real tenant" to **[Open: O-81]**, but RAID O-81 is "Asymmetric registry verification path, trust set, algorithm allowlist… dev key literal rename" [Source: docs/RAID_LOG.md:98]. There is no open item for signing per-tenant allowlists other than O-172 itself. The catalogue's citation needs correcting to O-172 by its owner — **I did not edit it in this session**, as instructed.
8. **`runtime.yaml` is checked by nothing that runs the runtime.** Both checkers read it [Source: scripts/verify_tool_registry.py:79-84; apps/cli/rt365_cli/main.py:118-123]; the MCP runtime does not read it at all. Pinning it under O-172 makes an unenforced declaration tamper-evident, which is worth doing and is not the same as enforcing it [Source: docs/MCP_TOOL_CATALOG.md:9].

## 9. Assumptions, confidence, provenance, and what I could not verify

- **A-1 [Source: this tree at `442cebd`, 2026-09-09]** Every `[Source: path:line]` in this pack is a file read on this worktree today. One file was dirty in the working tree (`docs/DATA_FLOWS.md`); nothing in this pack cites it.
- **A-2 [Committee]** I ran no test and changed no file other than this pack. The test ids TC-AI-032..042, TC-OB-014 and TC-PKG-006 are **proposed** in existing areas (highest existing: TC-AI-031, TC-OB-013, TC-PKG-005); none exists, and no document may cite them as coverage until they do [Source: docs/PO_DECISION_QUEUE.md:185].
- **A-3 [Open]** No number in this pack is proposed as a threshold. The ceiling **values** for O-170, the alert-storm bound for O-171 and any staleness or cadence figure for O-172 have no approved source. The source that would settle them is a Chief Risk Agent proposal decided by the Product Owner, in the manner O-07 is queued for the limit matrix [Source: docs/PO_DECISION_QUEUE.md:86].
- **A-4 [Open]** Nothing here is verified against a deployed topology, a cluster NetworkPolicy, a KMS, a real tenant or a real handler that performs I/O — none exists [Source: docs/MCP_TOOL_CATALOG.md:9, :45; docs/RED_TEAM_PLAN.md:29-31]. The whole of O-171's operational cost is therefore unmeasured.
- **A-5 [Committee]** I am the specifying seat for the tool catalogue and for `mcp/policies/`; I may not approve any of these three recommendations, and this document records no approval, no decision, no gate pass and no risk acceptance [Source: docs/MCP_TOOL_CATALOG.md:5; docs/PRODUCT_OWNER.md:20].
- **Confidence:** O-170 **high** on the mechanism and its placement, **none** on values. O-171 **medium-high** on direction, **high** on the payload defect (it is mechanical), **low** on operational cost. O-172 **medium-high** on rejecting Option A, **medium** on B-then-C sequencing, **none** on anything requiring the ceremony or a deployment.
- **Provenance:** docs/RAID_LOG.md:231-233; docs/SESSIONS/BUILD_E09_2026-09-08_egress_and_trust_anchor.md §11 (E09-PO-4/5/6); docs/THREAT_MODEL.md:108-109; docs/RED_TEAM_PLAN.md:27-31; docs/MCP_TOOL_CATALOG.md; mcp/policies/*; mcp/servers/mcp_servers/{registry,egress,runtime,identity,allowlist}.py; scripts/verify_tool_registry.py; apps/cli/rt365_cli/main.py; apps/web/web_bff/platform.py; observability/{alerts.yaml,rtobs/alerts.py}; libs/core/rtcore/trust.py; docs/ALERT_CATALOG.md; docs/TEST_CASES/TC-AI.md; test/quartets/test_tc_ai_egress_trust.py; .github/CODEOWNERS; Makefile; .github/workflows/ci.yml.
