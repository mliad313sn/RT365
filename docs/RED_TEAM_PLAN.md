# RED_TEAM_PLAN

| Owner (author) | Reviewer (different line) | Recommending body | Decider | First gate | Status |
|---|---|---|---|---|---|
| Red-Team & Pen-Test Lead (3rd line) | Security Architect (1st line, for scope realism only — never for a finding's closure) | Security & Privacy Board | Product Owner (D-039; AI delegate under D-040) | D (external engagement); dev/sim cases run continuously | v1.1, 2026-09-08 — RT-05 re-scoped and RT-07..RT-14 added from the review of THREAT_MODEL v1.1 (`docs/SESSIONS/REVIEW_2026-09-08_threat_model_redteam.md`). **Reviewer signature on this version: [Open] — not written.** |

Scope [Source: 06, 11]: AI/MCP paths (injection, tool escalation, exfiltration, hallucinated symbols, audit deletion, unsafe tool selection), tenant escape, secrets leakage, replay, duplicate orders, supply chain, authorisation, and — added in v1.1 — the integrity of the material every other control is verified against (trust anchors, policy files, start-up configuration) and denial of service **against** fail-closed controls [Committee: REVIEW_2026-09-08_threat_model_redteam §4].

**Reading rules.**
1. A case that has been *run* names the artefact holding its output. A case that has not been run says so; an allocated id is never evidence [Committee: D-061, O-143].
2. "Executed in dev/sim as TC-nn" means a control quartet covers the case in the test suite. It does **not** mean the case has been run against a deployed system, and no gate report may present it as one.
3. The red team does not remediate, does not accept residual risk, and does not sign off a test it scoped alone where the same seat also owns the control (D-063 (c), O-144).
4. Findings are closed by evidence of a retest, never by an explanation [Committee].
5. Nothing here asserts a vendor capability, a regulatory position or a threshold; every such point is [Open] with the act that would settle it.

## 1. Case list

| Case | Objective (attacker's goal) | Success for red team = finding | Where it can run | Cadence |
|---|---|---|---|---|
| RT-01 Injection via a content adapter | make an agent submit an intent outside its envelope, or call a tool it was not granted | any control bypass | dev/sim now (fixture content); **a real provider feed needs H-08/O-12** | before Gate D, F |
| RT-02 Tool escalation | reach a broker route, a secret, a limit write path, an audit delete path or a mode change from the MCP server | any route | dev/sim now | before Gate D |
| RT-03 Tenant escape | read or move another tenant's positions, intents, limits or audit rows | any leak | dev/sim now, executed as TC-TEN-002/003 (agent → other account, cross-tenant mint, human A → B on every endpoint, forged `X-Actor-Tenant`, unbound principal, cross-tenant limit leak, cross-tenant Kill Switch and deactivation, another tenant's queued intent; 404 bodies identical for missing and foreign objects). **Open: the deployed BFF with an IdP session (R-06) and a multi-account tenant case** | before Gate D |
| RT-04 Replay / duplicate | create two live orders from one intent, or re-use an authorisation grant | duplicate or re-used grant | dev/sim now; the **broker-side** half needs a certified sandbox (broker certification, H-07) | before Gate C |
| RT-05 **Store and audit integrity** (re-scoped in v1.1 — see §2) | make a durable control lie: disengage a Kill Switch, un-consume a grant, un-revoke an identity, or shorten the audit trail, without any detection | any undetected change to a control-bearing row, journal, chain or witness | **§2 (a)–(d) run in dev/sim now — (a) and (b) already produce findings**; (e)–(g) need a deployed topology, a real anchor principal and a WORM medium (O-54, H-05) | before Gate C, retest before D and F |
| RT-06 Supply chain | get unreviewed or unsigned material into a running platform: an image, a wheel, an installer, a dependency or a CI step | any accepted artefact | dev/sim for the wheel, the one-file executable and the bundle; **images, signing and the deployed pipeline need H-05/H-30 and code-signing** | before Gate B for what exists; D for the deployed pipeline |
| RT-07 **Trust-anchor substitution** | forge a tool registry or a command grant by writing the verifier's *own* trust material, not by stealing a key | any accepted forgery | dev/sim now — **already produces a finding** (`docs/PENTEST/probes/rt_probe_04_trust_anchor.py`) | before Gate C |
| RT-08 **Unsigned policy files** | widen a per-tenant allowlist, an egress list or an alert catalogue by editing the file the platform loads at start | any widened grant that loads | dev/sim now | before Gate C |
| RT-09 **Denial of service against the fail-closed controls** | use the controls as the weapon: starve the store lock, exhaust the MCP handler pool, corrupt one audit byte to trigger the platform-wide halt, flood the alert path into a catalogued auto-action | any single low-privilege action that halts or starves the platform | dev/sim for the store lock, the handler pool and the audit-halt path; **the multi-process, multi-host and network cases need a deployed topology (H-05, O-117)** | before Gate C (dev/sim half), D (deployed) |
| RT-10 **Start-up and configuration integrity** | bypass every durable control by starting the platform against different paths, an empty state directory, a different anchor directory or an attacker-supplied authorisation key | the platform serves with no history and no alert | dev/sim now — **already produces a finding** (`docs/PENTEST/probes/rt_probe_05_clean_slate.py`) | before Gate C |
| RT-11 **Operator abuse and the recovery path** | use the documented recovery action as the attack: seal over a truncated chain, restore a stale backup, complete a stale two-person deactivation, or narrow a platform-wide halt | any recovery step that destroys or launders evidence | dev/sim now for the seal and restore cases; **the two-person and platform-operator cases need R-06 and a second named human (H-01, H-26)** | before Gate C (technical half), D (human half) |
| RT-12 **Agent harness and delivery path** | have a delivery agent author what it reviews, edit the guard that constrains it, or land a change on a protected path without its 2nd-line owner | any protected-path change without a distinct reviewer | dev/sim now for the guard and roster; **the branch-protection and CODEOWNERS half is not testable until O-20 and branch protection exist** | before Gate C |
| RT-13 **Model-provider boundary** | get a secret, a broker route, a limit write path or unmasked customer data across the model-gateway boundary; make the platform depend on a provider's answer | any of the five, or a decision that changes when the provider's answer changes | **cannot run: no gateway, no provider, no terms (D-052, O-79, H-06)** | before the first provider is wired, and before Gate D |
| RT-14 **Market-data entitlement boundary** | move a licensed or unlicensed field into an AI context, an export or a second tenant | any field crossing the boundary | **cannot run beyond fixtures: no licence and no entitlement implementation (H-08, O-12, D-056)** | before Gate D |

## 2. RT-05 scope, written by the red team (O-144, D-063 (c))

RT-05 was one line ("alter or delete an audit event") and was cited by THREAT_MODEL T-61 as the case that would prove or disprove the store-integrity claim. The Security Architect owns the control, proposes the O-128 remedy and must not scope or sign off the test that judges it (D-063 (c)); this is that scope. **Objective: make a durable control lie without detection.** The target is never a data row for its own sake — it is always a control: a Kill Switch activation, a consumed authorisation, a lease and its fencing token, a revocation, an audit event.

| Sub-case | What is attempted | State at 2026-09-08 |
|---|---|---|
| RT-05 (a) Consistent rewrite of the control store | remove or flip a control row **and** re-chain the whole journal, so `SqliteStore.verify()` passes | **Run. Finding: an engaged ACCOUNT Kill Switch was removed, the store verified clean, no alert fired and the next intent reached the broker.** Evidence `docs/PENTEST/probes/rt_probe_03_consistent_rewrite.py`. This is the residual T-61 admits; the probe measures it as a *control* bypass, not a row edit [Open: O-128] |
| RT-05 (b) Audit truncation and witness manipulation | truncate the chain consistently, remove the witness, remove the anchor tail, and take the one recovery action an operator has | **Run. Findings: a rebuilt platform serves on a truncated chain and only an explicit `verify()` call halts it; a deleted witness pages but halts nothing; an operator `seal` after a deleted witness re-anchors the truncated chain and everything reports healthy.** Evidence `docs/PENTEST/probes/rt_probe_01_audit_witness.py` [Open: O-133, O-134, O-137] |
| RT-05 (c) Out-of-band mutation while the process runs | delete or edit rows in an open store; observe what the running platform reads | **Run.** A deleted activation row disappears from `active()` with no alert; the store refuses only at the next open. Evidence `docs/PENTEST/probes/rt_probe_02_control_store.py` |
| RT-05 (d) Journal and revocation files | delete a revocation line, append a forged `lift` line, roll back the nonce journal | **Not yet run** — the behaviour is admitted by T-80 (no digest, no chain); the case is written to size the exposure, not to discover it |
| RT-05 (e) Restore as replay | restore the control store without its journals, and the reverse; restore a stale backup with a current witness | **Not run in dev/sim yet**; the deployment half needs a real backup/restore procedure and a DR drill (H-19) |
| RT-05 (f) The anchor principal | attempt an audit write, a delete or a re-anchor while holding only the publisher's credential | **Cannot run**: in dev/sim the "different principal" is a directory on the same host under the same user (`FileAnchorPublisher`). Needs O-54 (a real identity and a WORM medium) — this sub-case is the one that would make the witness meaningful |
| RT-05 (g) Journal-head anchoring, once built | verify that a control-store rewrite is refused because the journal head no longer matches the last sealed audit event | **Cannot run: not implemented** [Open: O-128]. This is the retest that would close (a) |

**Reporting for RT-05:** each sub-case reports severity, the exact command, the observed platform behaviour and the owner; (a), (b) and (c) are already reported in `docs/SESSIONS/REVIEW_2026-09-08_threat_model_redteam.md`. **The red team does not accept the residual and does not choose the remedy** — O-144 asks the Product Owner to name the seat that accepts it [Open].

## 3. What cannot be run here, and what would change that

| Blocked case | Why | What settles it |
|---|---|---|
| Any deployed-topology case (RT-03 deployed, RT-06 images, RT-09 multi-host, RT-12 branch protection) | there is no cluster, no edge, no registry and no branch protection | H-05 (infrastructure spend), O-20 (CODEOWNERS + branch protection) |
| RT-05 (f) and the WORM half of RT-05 (b) | the witness is a directory on the same host under the same identity | O-54 (anchor principal and medium) |
| RT-13 model provider | no gateway, no provider, no signed terms | D-052 build, H-06, O-79 |
| RT-14 entitlement | no licence, no entitlement implementation | H-08, O-12, D-056 |
| Broker-side RT-04 | no certified broker sandbox | H-07 broker certification |
| An **independent** engagement of any of the above | the same programme cannot be its own external assurance | H-10 (contract an external pen-test and red team). Until H-10, every case here is internal 3rd-line work and must be labelled as such in any gate record |

## 4. Reporting and retest

Severity (this plan's scale, not a vendor's): **Critical** — a control of record can be bypassed or silenced with no detection and the platform keeps trading; **High** — bypass with detection that no automatic action follows, or a control that is not in the call path; **Medium** — a control weaker than the document claims; **Low** — record, wording or traceability defect. Every finding carries: case id, severity, the command run, the observed behaviour, the owning role, and the gate by which a retest is due. Findings are closed by a retest run by this role (or by the external supplier under H-10), never by an explanation from the owner of the control. Retest before Gate D and Gate F is mandatory [Source: 06, 11]; retest before Gate C for RT-04, RT-05, RT-07..RT-12. External pen-test annually once H-10 exists; nothing in this plan asserts that an external supplier has been engaged.
