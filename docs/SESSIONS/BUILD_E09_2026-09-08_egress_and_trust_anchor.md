# BUILD_E09_2026-09-08 — the egress allowlist and the trust anchor

| Session | Date | Builder | Line | Status |
|---|---|---|---|---|
| Build agent E09 (MCP / AI governance) remediating REVIEW_2026-09-08_threat_model_redteam RT-F1 and RT-F6 | 2026-09-08 | build-e09 (1st line, AI) | 1st | **Built and tested. Not reviewed, not approved, no gate passed.** Reviewer of record: MCP Security Agent (2nd line); the Independent Validation Agent may veto the evidence; the Product Owner decides (D-039) |

Branch `build/e09-egress-and-trust-anchor` off `claude/project-owner-agent-setup-hi3xqu` at `b912249`. Commits: `0bc7beb` (quartets, red) and `451931a` (implementation, green). Not pushed. Register item E-6. Nothing in this session promotes any environment beyond dev/sim [Source: 12]. Profit is an objective, never a promise [Source: 00]. No regulatory position, data licence, broker capability, vendor capability or threshold is asserted; every such point is tagged [Open] with the act that would settle it.

## 1. Roles and segregation

| Role | Seat | This session |
|---|---|---|
| Builder / author of the code and its tests | Build agent E09 (1st line) | **this packet**; author is never the approver |
| Reviewer of record (2nd line) | MCP Security Agent | **not yet asked**; owns `/mcp/policies` (CODEOWNER) and the registration review REVIEW_C3 / O-35 |
| Finder of both defects (3rd line) | Red-Team & Pen-Test Lead | RT-F1, RT-F6, probe 04; owns `docs/PENTEST/` — **I could not edit his probe** (§9) |
| Owner of THREAT_MODEL rows T-13, T-89, T-91 | Security Architect | rows proposed in §6, not written by me |
| Owner of RAID / RTM / DECISION_LOG ids | Program Orchestrator / Product Owner delegate | rows proposed in §5 and §7 with **no ids assigned** |
| Decider | Product Owner (D-039; delegate D-040) | §11 |

I edited only paths inside this role's write scope: `mcp/servers/mcp_servers/`, `libs/core/rtcore/trust.py`, `apps/web/web_bff/platform.py`, `apps/cli/rt365_cli/main.py`, `scripts/verify_tool_registry.py`, `observability/alerts.yaml`, `test/quartets/`, `docs/TEST_CASES/` (generated) and this packet. **I edited no ledger** — not RAID, not the RTM, not DECISION_LOG, not THREAT_MODEL, not `mcp/policies/`. Guard note for the record: the PreToolUse guard refused one edit to `docs/PENTEST/probes/rt_probe_04_trust_anchor.py` (`agent_guard: agent 'build-e09' may not edit ...`) and one write to a scratch path outside the repository; I did not route around either through Bash, and the probe patch is delivered as text in §9 for its owner.

## 2. Purpose

Two controls this epic claims did not exist in code. The Red-Team & Pen-Test Lead defeated one of them in under a minute. This session builds both, tests first, and corrects what the model may claim about them.

- **RT-F1 [Verified: grep over `mcp/`, `apps/`, `services/`, `libs/` at `b912249`]** — `EgressPolicy.check()` was called by no product code. The object was loaded at `platform.py:1007` and exposed as `platform.egress`; its only caller was TC-AI-005, which called `egress.check(host)` itself. THREAT_MODEL T-13 lists the egress allowlist as a delivered control with no `[Open]` tag.
- **RT-F6 / probe 04 [Verified: probe re-run by me, §8]** — `load_trust_set()` resolved the trust set from the *artefact's own directory* (`<registry dir>/trust/registry_keys.json`). ADR-019's verification is sound and every claim in T-69..T-73 held under attack; nothing said who may write the file that says which keys to trust. An attacker key, an attacker trust set beside a forged registry, and the registry was accepted with the write-class tool's quota widened from 10 to 100000 per minute and its payload limit from 32 KiB to 10 MB.

## 3. Design decision — defect 1 (egress)

**Chosen: prove the capability is absent, and enforce the allowlist at the point where a future handler would acquire a client.** This is the reviewer's second option, and it is chosen because it is the only one that is true today.

Verified, not assumed: **no MCP tool handler performs network I/O and none can.** The six handlers in `mcp_servers/tools.py` work on in-process objects (the bitemporal market store, the intent queue, the strategy registry). The transitive first-party import closure of `mcp_servers` is **32 modules** and contains no `socket`, `ssl`, `http`, `urllib`, `requests`, `httpx`, `aiohttp`, `asyncio`, `subprocess` or web-framework import [Verified: TC-AI-026 (a), which walks the closure]. Running all six tools under a sentinel over `socket.socket` and `socket.create_connection` produces no attempt [Verified: TC-AI-026 (b)].

What was built:

1. `EgressGuard` (`mcp/servers/mcp_servers/egress.py`) — the only sanctioned way a handler may acquire an outbound destination. It authorises and **never connects**: the caller passes a client factory, and the factory is not called on a denial. It cannot connect even if it wanted to, because nothing in `mcp_servers` may import a network module (TC-AI-005).
2. `ToolRuntime` binds a guard **per tool call** and publishes it to the handler through a context variable that is copied into the handler's pool thread (`contextvars.copy_context()`), so `current_egress()` inside a handler carries that call's `correlation_id`, tenant, actor and tool. Outside a call, `current_egress()` returns the process-wide `DENY_ALL`.
3. Every decision is an audit row with a reason code, the host, the matched allowlist pattern and the policy file: `mcp.egress.allowed` / `mcp.egress.denied`, reason codes `EGRESS_ALLOWED`, `EGRESS_NOT_ALLOWLISTED`, `EGRESS_NO_POLICY`. A denial raises `PlaneViolation`, the runtime turns it into the tool-call denial code `EGRESS_DENIED`, and the guard raises the catalogued alert `mcp.egress_denied` (S1, `auto_action: none` — **the auto-action is a control decision and is not the builder's to take**; proposed to the MCP Security Agent and the Chief Risk Agent in §5).
4. **A guard with no policy denies everything.** An MCP runtime built without an egress guard gets one with no policy, not an unfiltered path.
5. The composition root now passes the loaded `EgressPolicy` into the guard and the guard into the runtime, so the object it loads is on a call path (`platform.egress_guard`, asserted by TC-AI-024).

Alternatives considered:

- **Wire `EgressPolicy.check()` into a real outbound path.** Rejected: there is no outbound path to wire it into. Inventing one — an HTTP client in `mcp_servers` so the check has something to guard — would add exactly the capability this epic exists to deny, and would break TC-AI-005.
- **Block the network with a process-level sentinel at runtime** (patch `socket` while a handler runs). Rejected as a *product* control: it would require `mcp_servers`, or a module it imports, to import `socket`, which is the import the epic rule forbids; and a sentinel installed in-process is defeated by anything running in the same process. It is used where it belongs — as the abuse half of the test (TC-AI-026 b).
- **Leave the allowlist unwired and correct T-13 only** (the reviewer's first-order fix). Rejected as insufficient: honest, but it leaves the next handler author with no seam and no denial, so the control would have to be invented again under time pressure.

**What the model may now say about T-13**: proposed row text in §6. It must not say the allowlist filters traffic; it may say that no handler can reach the network, that this is proved by TC-AI-026, and that the allowlist is enforced at the acquisition seam.

## 4. Design decision — defect 2 (trust anchor)

**Chosen: a trust set resolved from the resource root, *and* pinned by a fingerprint held outside the file — with a trust set found beside an artefact refused rather than ignored.** Two of the reviewer's three options, together, because separately each leaves a hole.

| Reason code | Refused when |
|---|---|
| `TRUST-ANCHOR-ADJACENT` | a trust set sits beside the artefact and is not the anchor (a bundle carrying both a forged registry and a matching trust set — probe 04) |
| `TRUST-ANCHOR-NO-ROOT` | there is no resource root, so there is no anchor |
| `TRUST-ANCHOR-ABSENT` | no file at `<resource root>/mcp/policies/trust/registry_keys.json` |
| `TRUST-ANCHOR-UNPINNED` | the anchor exists but no fingerprint is pinned for its purpose |
| `TRUST-ANCHOR-PIN-MALFORMED` | the pin is not 64 hex characters (an operator who cannot name the digest has not performed the act) |
| `TRUST-ANCHOR-PIN-MISMATCH` | the anchor's sha256 is not the pinned one |
| `TRUST-ANCHOR-PURPOSE` | the file declares a purpose other than `tool-registry` |
| `TRUST-ANCHOR-MALFORMED` | the file cannot be read as a trust set |

The pin lives in `rtcore.trust.PINNED_TRUST_SETS` (a compiled-in constant, **empty today**, because no ceremony key exists — H-20) or, failing that, in `RT365_TRUST_SET_SHA256_TOOL_REGISTRY`, which an operator sets to the exact digest as a recorded act. **A pin is a public digest, so this control requires no secret and no key custody.** `TrustAnchorRefused` subclasses `RegistryUnsigned`, so the CLI, `verify_tool_registry.py`, the composition root and the stdio host all keep failing closed with no change. A trust set passed explicitly by a composition root (`load_registry(..., trust_set=...)`, `build_sim_platform(registry_trust_set=...)`) is still accepted: that is code the process was started with, not a file found next to an artefact.

Alternatives considered:

- **Resolve from the resource root only, no pin.** Rejected: it defeats the probe (the artefact's directory is no longer consulted) but not the threat the row names — an actor who can write the resource root writes the anchor, which is precisely T-89's premise.
- **Pin only, still resolved from the artefact's directory.** Rejected: a bundle attack ships a trust set *and* the digest of that trust set is whatever the attacker chose; the pin only means something when the thing it pins has one fixed location.
- **Require the trust set to be signed.** Rejected as circular for the root of trust: the signature over the trust set would be verified against — a trust set. A ceremony signature over the anchor is worth adding **above** the pin later (it makes rotation reviewable by a third party); it does not replace the pin. Proposed to the Security Architect in §6.
- **Refuse any trust set not named on the command line by an operator at every start.** Rejected: it makes every restart a manual act, which fails the availability side and pushes operators towards a wrapper script that supplies the value automatically — the same act with the evidence removed. The environment pin is that act, once, with a digest that can be checked against the ceremony record.
- **Ship a trust set now.** Not mine to do: `mcp/policies/` is CODEOWNER'd by the MCP Security Agent and there is no ceremony key (H-20). The absent anchor is therefore fail-closed by design and by fact.

## 5. Proposed RAID entries and catalogue rows (ids by their owners; I assigned none, and I edited no ledger)

| Type | Proposed text | Owner | Gate |
|---|---|---|---|
| Gap (closes the reviewer's egress gap in part) | `EgressPolicy` is now consulted: `EgressGuard` is bound per MCP tool call and audits every decision (TC-AI-024..027). What remains open is that **no handler makes an outbound call**, so the guard has no live traffic to filter, and the deployed half (NetworkPolicy) is checked against manifests for a cluster that does not exist [Open: H-05] | Backend Lead / Security Architect | B (wording) / C (deployment) |
| Decision needed | `mcp.egress_denied` is catalogued S1 with `auto_action: none`. Whether an MCP handler reaching for a non-allowlisted destination should revoke the agent identity (as `plane.deny` does) is a control decision the builder must not take | MCP Security Agent / Chief Risk Agent | C |
| Gap | **Nothing cross-checks a loaded registry's tool parameters against an approved catalogue.** `verify_tool_registry.py` checks shape only (the six names, one write-class tool, positive quota/timeout/payload) and that `tool_registry.json` equals the signed copy — which a forger who re-signs both files satisfies. `docs/MCP_TOOL_CATALOG.md` carries values in prose and says explicitly that none of them is a decided threshold [Open]. So a validly signed registry can still widen a quota or turn masking off, and the only defence is the integrity of the signing key and its trust anchor (T-91). **Reported as a finding, not built here**: a floor in code would be inventing thresholds the Product Owner and the MCP Security Agent have not set | MCP Security Agent / Backend Lead | C |
| Gap | The trust anchor's pin can be supplied by the start-up environment (`RT365_TRUST_SET_SHA256_TOOL_REGISTRY`), and the resource root itself by `RT365_HOME`. An actor who controls the process environment therefore still controls both. This is the start-up-configuration threat the reviewer raised as T-92 / RT-PO-6 and it is **not** closed by this work | Backend Lead / SRE Lead | C |
| Gap | `mcp/policies/egress.yaml`, `runtime.yaml` and the per-tenant allowlists remain unsigned and unpinned (the reviewer's T-90). With the guard now enforcing, an actor who can add a host to `egress.yaml` widens what a future handler may reach | MCP Security Agent | C |
| Note | Two TC-SIG assertions that encoded the old adjacency behaviour were changed to assert the refusal (§7). Neither was weakened; the trust-set round trip, the rotation overlap and the retirement checks are unchanged | Backend Lead | B |
| Note | Precision on probe 04: the committed fixture already has `masking: none` for `submit_trade_intent` (a write tool whose output is ids), so that part of the forgery changed nothing on that tool. The masking downgrade that matters is `read_account_state` (`identifiers masked; balances rounded per policy`), which TC-AI-030 forges explicitly. The quota (10 → 100000/min) and payload-limit (32 KiB → 10 MB) halves of the finding are exactly as reported | Red-Team & Pen-Test Lead / Security Architect | B |

Proposed DECISION_LOG entries (**no ids assigned; the ledger owner allocates**):
1. *Egress enforcement point*: the MCP egress allowlist is enforced at the client-acquisition seam (`EgressGuard`) and the absence of any network capability in the handler closure is a tested control; alternatives: wire the checker into an invented outbound path (rejected — it would add the capability the epic denies); correct T-13 and build nothing (rejected — leaves no seam).
2. *Trust-anchor integrity*: the tool-registry trust set is an artefact of the resource root, trusted only when its sha256 matches a pin held in code or named by an operator; alternatives: root resolution alone (rejected — does not answer T-89); pin alone (rejected — meaningless without a fixed location); a signature over the trust set (deferred — circular as the root, valuable above the pin).

## 6. Proposed THREAT_MODEL rows (owner: Security Architect; I did not edit the document)

- **T-13** — control column: "canary tokens and tenant-filtered reads **delivered** (TC-AI-003, TC-TEN-003); egress: **no MCP tool handler performs network I/O and none can** — the transitive first-party import closure of `mcp_servers` contains no network module and every tool runs under a socket sentinel with no attempt (TC-AI-026); the allowlist is enforced at the client-acquisition seam `EgressGuard`, bound per call, audited with a reason code, deny-all without a policy (TC-AI-024/025/027). The deployed NetworkPolicy half is manifest-checked only [Open: H-05]. The row must not read as if live traffic is filtered — there is no live traffic."
- **T-89 (trust-anchor substitution)** — control column becomes: "Interim (delivered): the trust set is resolved from the resource root, never from an artefact's directory; a trust set adjacent to an artefact is refused; the anchor is trusted only when its sha256 matches a pin in `rtcore.trust.PINNED_TRUST_SETS` or in `RT365_TRUST_SET_SHA256_TOOL_REGISTRY`; absent, unpinned or mismatched all fail closed (TC-AI-028..031). Residual: the pin and the root are both start-up inputs, so T-92 (start-up configuration) subsumes this for an actor who controls the environment; no ceremony key, no committed anchor, no CODEOWNER for the file yet [Open: H-20, O-126, O-127]." Test column: TC-AI-028, TC-AI-029, TC-AI-030 (the probe as a test), TC-AI-031.
- **T-91 (masking downgrade)** — add to the residual: "nothing cross-checks a loaded registry's quota, payload limit, timeout or masking against an approved catalogue; `verify_tool_registry.py` checks shape only and `MCP_TOOL_CATALOG.md` states that none of its numbers is a decided threshold [Open]."
- **T-69..T-73** — cross-reference T-89 with one clause: "the verifier's copy of the trust set is now anchored and pinned (TC-AI-028..031); these five rows still assume the *pin* is authentic."
- **T-95 (retirement not durable)** — unchanged in substance, but note that a retirement written into the anchored file now also requires the pin to be updated in the same act, which is what TC-AI-031 exercises.

Proposed RTM rows (owner: Program Orchestrator; requirement → architecture → owner → control → test → evidence → gate):

| Requirement | Architecture | Owner | Control | Test | Evidence | Gate |
|---|---|---|---|---|---|---|
| NFR-SEC-01 (egress) | `mcp_servers.egress.EgressGuard` bound per call by `ToolRuntime`; `EgressPolicy` loaded by the composition root | Backend Lead / MCP Security Agent | no handler can reach the network (import closure + socket sentinel); a non-allowlisted destination is refused, audited with the call's correlation id and alerted; no policy means no destination | TC-AI-024..027 | `docs/TEST_CASES/TC-AI.md`; this packet §8 | B (dev/sim) / C (deployed NetworkPolicy, H-05) |
| NFR-SEC-01 (signing / trust root) | trust anchor at `<resource root>/mcp/policies/trust/registry_keys.json`, pinned by digest; `rtcore.trust.load_pinned_trust_set` | Security Architect / Backend Lead | a trust set beside an artefact, absent, unpinned or mismatched is refused; rotation is one reviewed act | TC-AI-028..031 (with TC-SIG-001..004) | `docs/TEST_CASES/TC-AI.md`, `TC-SIG.md`; probe 04 before/after §8 | C |

## 7. Control quartets

| Control | Positive | Negative | Abuse | Recovery |
|---|---|---|---|---|
| **A. Egress allowlist on the MCP call path** | **TC-AI-024** — the composition root's policy *is* the runtime's guard; an allowlisted destination is acquired once; one `mcp.egress.allowed` row carries the call's correlation id, tenant, host, matched pattern, policy file and reason code | **TC-AI-025** — a guard with no policy denies every host including ones the shipped file allows (`EGRESS_NO_POLICY`); an empty allowlist denies everything; outside a tool call the ambient guard is `DENY_ALL`; the client factory is never called on a denial | **TC-AI-026** — (a) no network module anywhere in the 32-module first-party closure the handlers reach; (b) all six tools run under a socket sentinel with zero attempts; (c) a handler that asks for the vault, the execution gateway, a broker or the open web is refused, the call is denied `EGRESS_DENIED`, the denial is audited under the call's correlation id and `mcp.egress_denied` fires four times; nothing is submitted anywhere | **TC-AI-027** — a denial mutates no policy and revokes nothing: the same guard immediately allows an allowlisted host again under a fresh correlation id, the tools keep working, and a guard rebuilt without its policy still fails closed |
| **B. Trust-anchor integrity** | **TC-AI-028** — a registry signed by a key in the anchored, pinned trust set loads with `dev_key_in_use=False`; the anchor is resolved from the resource root whatever directory the artefact sits in; an explicit in-process trust set still works; the committed dev/sim HMAC path is unchanged | **TC-AI-029** — absent, unpinned, pin-mismatched, pin-malformed, wrong-purpose and no-resource-root each refused with their own reason code, and every refusal is a `RegistryUnsigned` so existing callers still fail closed | **TC-AI-030** — the reviewer's probe as a test: attacker key, forged registry (quota 10 → 100000, payload 32 KiB → 10 MB, `read_account_state` masking → none) plus the attacker's trust set beside it → `TRUST-ANCHOR-ADJACENT`; the same attacker writing both into the resource root → `TRUST-ANCHOR-PIN-MISMATCH`; removing the pin → `TRUST-ANCHOR-UNPINNED`, never a silent restoration of trust; no widened `ToolSpec` is ever produced | **TC-AI-031** — a genuine rotation is one act: file and pin move together (moving the file alone fails closed), both keys verify during the overlap, retirement written into the anchored file refuses the old key absolutely, and losing the pin returns to fail-closed |

Existing tests changed (declared): `test_tc_sig_signing.py` TC-SIG-001 — `assert load_registry(signed, at=T0).key_id == "reg-sim-a"  # default trust set: <dir>/trust/registry_keys.json` becomes `pytest.raises(RegistryUnsigned, match="TRUST-ANCHOR-ADJACENT")`, and the platform build there now passes `registry_trust_set=reg_trust`; TC-SIG-004 — the shipped-trust-set assertion `len(shipped) == 0` becomes `pytest.raises(..., match="TRUST-ANCHOR-ABSENT")` plus the same "an empty set refuses every Ed25519 registry" check against an explicit empty set. Both assertions previously encoded the vulnerability; neither control is weaker.

## 8. Evidence

| Evidence | Where |
|---|---|
| Quartets (8 tests, all four kinds twice) | `test/quartets/test_tc_ai_egress_trust.py` |
| Generated evidence record | `docs/TEST_CASES/TC-AI.md` (22 records, quartet complete), `docs/TEST_CASES/EVIDENCE_REPORT.md` (212 records, 24/24 areas) |
| Implementation | `mcp/servers/mcp_servers/egress.py`, `runtime.py`, `registry.py`; `libs/core/rtcore/trust.py`; `apps/web/web_bff/platform.py`; `apps/cli/rt365_cli/main.py`; `scripts/verify_tool_registry.py`; `observability/alerts.yaml` |
| Probe 04 before / after | below |
| `make all`, `make security-scan` | below |

**Probe 04 before the fix** (`RT_ENV=sim python3 docs/PENTEST/probes/rt_probe_04_trust_anchor.py` at `b912249`, reproducing the reviewer's §2 output verbatim):

```
  shipped registry: algorithm=HMAC-SHA256 key_id=dev-key-v0 fixture=True
  forged registry ACCEPTED: key_id=attacker-key-v1 algorithm=Ed25519 dev_key_in_use=False
  submit_trade_intent now: quota_per_minute=100000 payload_limit_bytes=10000000 masking=none
  control case (trust set removed): refused — RegistryUnsigned: registry key refused: unknown key_id 'attacker-key-v1' for tool-registry trust set
```

**Probe 04 after the fix** (same command at `451931a`) — the probe now fails at the attack step and can no longer print "ACCEPTED":

```
  shipped registry: algorithm=HMAC-SHA256 key_id=dev-key-v0 fixture=True
Traceback (most recent call last):
  File ".../docs/PENTEST/probes/rt_probe_04_trust_anchor.py", line 71, in main
    reg = load_registry(stage / "tool_registry.signed.json")
  File ".../mcp/servers/mcp_servers/registry.py", line 198, in load_trust_set
    raise TrustAnchorRefused(
mcp_servers.registry.TrustAnchorRefused: TRUST-ANCHOR-ADJACENT: a trust set beside the artefact
 (/tmp/tmp279jugrs/policies/trust/registry_keys.json) is not a trust anchor; the anchor for
 'tool-registry' is /home/user/RT365/.../mcp/policies/trust/registry_keys.json
```

**`make all`** (tail):

```
python3 scripts/verify_tool_registry.py
NOTE: registry is a sim FIXTURE (approvals pending); it embodies no approval and is refused outside dev/sim
NOTE: no usable trust anchor — TRUST-ANCHOR-ABSENT: no trust set for 'tool-registry' at .../mcp/policies/trust/registry_keys.json
OK: registry 0.1.0 (HMAC-SHA256, key_id=dev-key-v0, dev key), 6 tools, policies consistent
python3 scripts/generate_agents.py --check
OK: 67 agents in .claude/agents match goals/
python3 scripts/secret_scan.py
OK secret scan: 614 files, no findings
python3 -m pytest
230 passed, 2 warnings in 21.62s
python3 scripts/evidence_report.py
wrote docs/TEST_CASES/EVIDENCE_REPORT.md: 212 records, 24/24 areas with full quartet
python3 scripts/export_test_cases.py
wrote 24 TEST_CASES files
```

**`make security-scan`**: `OK scan exceptions: 0 entries, none expired`; bandit (HIGH at MEDIUM+ confidence) no findings; `pip-audit`: `No known vulnerabilities found` (twice, JSON and text).

**`--production` still refuses** [Verified]: `python3 scripts/verify_tool_registry.py --production` → `FAIL: dev signing key / fixture registry refused for production: HMAC-SHA256 is accepted in dev/sim only (RT_ENV='production'); the registry must be Ed25519-signed under the trust set`, exit 1. Under `--production` an absent or unpinned trust anchor is now also a failure.

**`rt365 check --env sim`** passes and reports the new state: `trust anchor: none usable at .../mcp/policies/trust/registry_keys.json — TRUST-ANCHOR-ABSENT ...; asymmetric registries are refused (pin with RT365_TRUST_SET_SHA256_TOOL_REGISTRY)`.

## 9. For the Red-Team & Pen-Test Lead — the probe patch I could not apply

The write-scope guard refused my edit to `docs/PENTEST/probes/rt_probe_04_trust_anchor.py` (his artefact). The scenario is committed as **TC-AI-030** so that it stays failed in CI. If he wants the probe to report rather than crash, the minimal patch is:

```python
        try:
            reg = load_registry(stage / "tool_registry.signed.json")
            spec = reg.get("submit_trade_intent")
            print(f"  forged registry ACCEPTED: key_id={reg.key_id} algorithm={reg.algorithm} dev_key_in_use={reg.dev_key_in_use}")
            print(f"  submit_trade_intent now: quota_per_minute={spec.quota_per_minute} payload_limit_bytes={spec.payload_limit_bytes} masking={spec.masking}")
        except Exception as exc:  # noqa: BLE001 — expected since the trust-anchor fix (TC-AI-028..031)
            print(f"  forged registry REFUSED: {type(exc).__name__}: {exc}")
```

and a fourth case worth adding, which I have covered as a test but not as a probe: write the attacker's trust set into the **resource root** (`RT365_HOME` pointing at a staged bundle) and confirm `TRUST-ANCHOR-PIN-MISMATCH`, then unset the pin and confirm `TRUST-ANCHOR-UNPINNED`.

## 10. Threat-model delta this build produces

| Delta | Rows | Boundary | State |
|---|---|---|---|
| Egress: claim corrected, capability absence proved, seam built | T-13 (correction), T-59 (the "nothing refuses a provider call" clause is still true — there is still no provider and no gateway) | B6, B2 | delivered dev/sim, tested |
| Trust anchor: adjacency closed, anchor pinned, refusals named | T-89 (control column), T-69..T-73 (cross-reference), T-95 | B10, B8, B6 | delivered dev/sim, tested; no ceremony key, no committed anchor [Open: H-20] |
| Registry parameter integrity | T-91 | B6, B3 | **unchanged — finding reported, nothing built (§5)** |
| Start-up configuration as the remaining way in | T-92 | B10, B8 | **unchanged — the pin and the root are start-up inputs** |
| Unsigned policy files | T-90 | B10, B6 | **unchanged** |

## 11. Concerns for the Product Owner

- **E09-PO-1 Two controls now exist that the model already claimed; that is a correction, not new coverage.** [Verified: `451931a`, 230 tests] The egress allowlist is on the MCP call path and the trust anchor is resolved and pinned. Neither adds a capability, a market or a strategy, and neither passes a gate. **Decide:** ask the Security Architect for the v1.1a T-13 wording in §6 in the same breath as the reviewer's other blocking row, so the evidence-index row is filled against text that matches the code.
- **E09-PO-2 The honest egress control is that there is nothing to filter.** [Verified: TC-AI-026] No MCP tool handler performs network I/O, and none of the 32 first-party modules the handlers reach can open a connection. I did not build an outbound path so that the allowlist would have something to guard — that would have added the exact capability this epic denies. What an attacker can still do: nothing through a handler today; but the enforcement that keeps it that way is **two tests**, and CI is not a required check (branch protection is not enabled, O-20, the reviewer's RT-PO-8). **Decide:** either make CI a required check before Gate B sign-off, or record that TC-AI-005 and TC-AI-026 are unenforced gates like every other CI-based control in the model.
- **E09-PO-3 The trust anchor is now pinned, and the pin is only as strong as the start-up environment.** [Verified: TC-AI-028..031, and by construction] An attacker who can write files — the boundary the reviewer's probe exercised — is now refused: a trust set beside an artefact is not a trust anchor, and the anchored one must match a digest held in code or named by an operator. An attacker who controls the **process environment** can still set `RT365_TRUST_SET_SHA256_TOOL_REGISTRY` to the digest of their own anchor, or point `RT365_HOME` at their own bundle entirely. That is the reviewer's T-92 / RT-PO-6, and it is untouched by this work. **Decide:** treat "a platform instance is bound to its state and its configuration" as a shadow entry condition, as the reviewer asked, and note that this fix moves the trust root into that same dependency rather than out of it.
- **E09-PO-4 Nothing checks what a signed registry is allowed to say.** [Verified: `scripts/verify_tool_registry.py`, `docs/MCP_TOOL_CATALOG.md`] I checked, as asked, and I am reporting rather than building: the verifier checks the *shape* of the registry (the six names, one write-class tool, positive numbers) and that the plain copy equals the signed copy — which a forger who re-signs both files satisfies. Nothing compares a loaded quota, payload limit, timeout or masking string against an approved catalogue, and the catalogue itself says explicitly that none of its numbers is a decided threshold [Open]. So a validly signed registry can still hand the write-class tool a 100000/minute quota, and the only thing standing between that and the platform is the signing key and its anchor. I did not invent a floor: the numbers are yours and the MCP Security Agent's to decide. **Decide:** commission the approved catalogue as data (a machine-checkable ceiling per tool, decided by the MCP Security Agent with the Chief Risk Agent) rather than as prose, and make `verify_tool_registry.py` compare against it.
- **E09-PO-5 An alert now fires that has no action behind it.** [Verified: `observability/alerts.yaml`] `mcp.egress_denied` is catalogued S1 with `auto_action: none`, because an automatic response — revoking the agent identity, as `plane.deny` does — is a control decision and I must not take it. Today it pages a human and stops nothing, which is the same asymmetry the reviewer flagged for the audit witness (RT-F2, O-137). **Decide:** ask the MCP Security Agent and the Chief Risk Agent to set the auto-action explicitly, rather than letting `none` become the answer by silence.
- **E09-PO-6 The policy files beside the registry are still unsigned, and now they matter more.** [Committee: the reviewer's T-90] Before this session, adding a host to `mcp/policies/egress.yaml` widened a list nothing consulted. Now it widens what a future handler may reach. The same holds for `runtime.yaml`, the per-tenant allowlists and `alerts.yaml` — all loaded as plain YAML at start-up beside a registry that is signed. **Decide:** whether the registry signature should cover the policy directory, or each file gets its own pin, before shadow.
- **E09-PO-7 What none of this says.** [Source: 00, 12] Nothing here authorises promotion beyond dev/sim, asserts that any control is fit for real money, or asserts a regulatory position, a data licence, a broker capability or a vendor capability. The committed registry is still HMAC under the published dev key (O-22, O-127, H-20): in dev/sim, whoever can verify can still forge, and the trust anchor does not change that because the HMAC path never consults it. No trust set is committed and the code pin table is empty, so the asymmetric path is fail-closed by absence — this work stops a forged anchor from being accepted; it does not put a real one in place. Profit remains an objective, never a promise.

## 12. Assumptions, confidence, provenance

- A-1 [Verified]: every `[Verified]` statement is a file read, a grep, a test run or a command run on 2026-09-08 in this worktree at `b912249` (before) or `451931a` (after). The probe outputs in §8 are verbatim, with the traceback abridged at the path prefix only.
- A-2 [Verified]: 222 tests passed at `b912249`; 230 pass at `451931a` (the eight new ones), 24/24 quartet areas, `make security-scan` clean. No test was deleted, skipped or weakened; the two changed assertions are named in §7.
- A-3 [Verified]: the import-closure claim is mechanical — 32 first-party modules reachable from `mcp_servers`, none importing a network module. It is a *static* claim about first-party code; it does not prove that a third-party package inside the closure's dependencies cannot open a socket, which is why the socket sentinel in TC-AI-026 (b) is the second half.
- A-4 [Open]: I did not test the frozen executable or an installed wheel with a trust anchor inside it (`installer/` is not in my write scope, and no anchor exists to package). `resource_root()` resolves `_MEIPASS` and the installed bundle, so the anchor travels with the bundle by construction; TC-PKG would need a case when an anchor exists [Open: O-126].
- A-5 [Open]: nothing here is verified against a deployed topology, a cluster NetworkPolicy, a KMS, a ceremony key or a model provider — none exists (H-05, H-20, O-79).
- A-6 [Committee]: the severities and reason codes I introduced are naming decisions, not thresholds. The one numeric ceiling anywhere near this work — the tool quotas and payload limits — I deliberately did not touch (§5, E09-PO-4).
- Confidence: **high** that both defects are closed against the attack each was reported under (each is one command or one test to reproduce); **high** that no existing control was weakened (full suite, evidence regeneration, security scan); **medium** that the trust-anchor design is the right long-run shape — a ceremony signature over the anchor is probably worth adding above the pin, and that is the Security Architect's call; **low** on anything about deployment, because there is nothing to test.
- Provenance: `docs/SESSIONS/REVIEW_2026-09-08_threat_model_redteam.md` (RT-F1, RT-F6, RT-PO-1, RT-PO-5, probe 04), `docs/THREAT_MODEL.md` T-13 and T-69..T-73 with the proposed T-89..T-96, `docs/DATA_FLOWS.md` DF-20, `docs/ADRs/ADR-019.md`, `docs/SECURITY_PLAN.md` v1.1 (F-20), `docs/MCP_TOOL_CATALOG.md`, `mcp/policies/`, and the code and tests named in §8. This packet records no approval, no decision, no gate pass and no risk acceptance.
