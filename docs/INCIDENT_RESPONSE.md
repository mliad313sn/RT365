# INCIDENT_RESPONSE

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| SRE Lead | Security Architect | CAB, Security & Privacy Board | C | Draft v1.1, 2026-09-08 — three fail-closed recoveries added (O-126, O-134); **reviewer signature pending**; not accepted |

Severity: S1 capital at risk / control bypass / data breach · S2 degraded control or data · S3 other.
Incident command: SRE Lead (commander), Chief Risk Agent (risk decisions), Compliance Agent (notifications), Security Architect (cyber), Support Lead (customers). Deputies documented in RACI.md [Source: 13].

## Runbooks [Source: 10]
| Runbook | Trigger | First action | Escalation |
|---|---|---|---|
| Data stale | freshness SLO breach | autonomy → Supervised; confirm RK-FRESH rejections | Data Eng Lead |
| Broker disconnected | health check fail | cancel-only mode; reconcile on reconnect | Broker-Connector Lead |
| Duplicate order | reconciliation or alert | Kill Switch at account; investigate fencing/idempotency | Integration Architect |
| Risk engine unavailable | health/latency | confirm HALTED outcomes (fail closed); restore | Backend Lead |
| Reconciliation break | EOD/intraday break | account → Supervised; ticket | Operations |
| Unexpected exposure | runtime monitor | halt strategy/account; apply emergency policy | Chief Risk Agent |
| Model drift | drift threshold | suspend challenger/champion signals | Model Risk Lead |
| Credential compromise | detection | revoke/rotate; Kill Switch at tenant; forensic snapshot | Security Architect |
| Regional failure | cell loss | DR_PLAN | Cloud Architect |
| Kill Switch activation | any | evidence snapshot; notify; post-incident review before restore | Incident commander |
| **Trust set missing (RB-11)** | fleet-wide refusal of every asymmetric verification, from a start or a deploy | confirm the trust-set file's presence, mode and hash against the release manifest; **never disable verification** | Security Architect + Backend Lead |
| **Audit witness lost (RB-12)** | `audit.anchor_missing` S1 (auto-action **none** — a page, not a halt) | record the incident correlation id **before** acting; classify unreachable vs damaged; restore the replica | Security Architect, Internal Audit, Cloud Architect |
| **Store will not open (RB-13)** | a process refuses to start: `StoreError`, `StoreIntegrityError`, `AuditIntegrityError` | **stop restarting it**; copy both store files and the anchor directory as found; classify availability vs integrity | Backend Lead, Security Architect, Cloud Architect, Chief Risk Agent |
Post-incident review within 5 working days; findings to RAID_LOG.md.

## Fail-closed recoveries [Committee] [Source: 10] — O-126, O-134

Three controls in this platform stop work rather than continue when they cannot prove themselves. Each is correct and none may be weakened for speed. The standing rule for all three: **recovery is *restore then verify*, never *disable then reopen*. Disabling a check is never a fix, at any hour, under any pressure** (O-134) [Committee]. Written by the SRE Lead 2026-09-08 from the review in docs/SESSIONS/REVIEW_2026-09-08_capacity_sre.md; **reviewer signature pending** — the author of a runbook does not sign it [Source: 13].

### RB-11 — Missing or malformed trust set (O-126, O-141)

| | |
|---|---|
| **Trigger** | Every asymmetric verification refuses at once — signed commands, registry signatures, MCP tool calls — from the moment a process starts. It looks like a mass credential failure and is not. |
| **How you find out** | By the *shape*: a fleet-wide refusal that began at a deploy or a restart, with no credential change behind it. `mcp/policies/trust/registry_keys.json` **does not exist in the tree** (O-141): the loader treats absent as empty and refuses everything asymmetric — fail closed by design. **No alert names this condition today** [Open: O-126, SRE-R6]. |
| **First action** | Confirm the file's presence, owner, mode and content hash on the affected node and compare the hash with the release manifest of the running artefact. Page the Security Architect **in parallel** with the Backend Lead while you check: you do not get to classify this as "just a deployment defect" alone. |
| **Never** | Do not disable asymmetric verification. Do not enable an unsigned fallback. Do not hand-place a key file from a developer machine. Refusing everything is the control working. |
| **Escalation** | Security Architect (trust decision), Backend Lead (loader), MCP Security Agent if tool calls are the visible symptom. |
| **Evidence first** | File presence/absence, owner, mode, hash; the release manifest entry; the first refusal's `correlation_id`; the deploy or restart event immediately before it. |
| **Exit** | The artefact-shipped trust set is in place at the manifest hash, a signed call verifies, and the deployment defect has a ticket. **Rolling the release back is preferred over placing a file by hand** (ROLLBACK_PLAN, "Service release"). |
| **Still owed** | The trust-set file's owner, its packaging step and its review step (O-126) and the file itself (O-141) — a decision for the Security Architect and the Cloud Architect, not for this runbook. |

### RB-12 — Audit witness lost, stale or corrupt (O-134, O-54)

| | |
|---|---|
| **Trigger** | `audit.anchor_missing`, S1; reasons `AUD-ANCHOR-MISSING`, `AUD-ANCHOR-STALE`, `AUD-ANCHOR-CHAIN-BROKEN`, `AUD-ANCHOR-TAIL-REMOVED` (ADR-020). |
| **Know this first** | **This alert does not halt anything.** Its catalogued auto-action is `none`, deliberately: the audit chain itself may be intact and only the external witness is unavailable. Trading continues while you work. And the witness is **not** checked when a process starts — a clean start-up is **not** evidence the witness is healthy; the published verification must be called explicitly. |
| **First action** | (1) Record the **incident correlation id** from the alert payload *before touching anything*: the store opens exactly one incident row per process lifetime and that id is how the eventual `audit.anchor.recovered` row is tied to it. (2) Establish which of the four reasons applies — they have different recoveries. (3) Decide **unreachable** (credential, mount, network to the other principal's store) versus **damaged** (chain broken, tail removed). The second is an integrity finding and is a security incident until the Security Architect says otherwise. |
| **Never** | **Do not disable the check. Do not re-anchor to "fix" it. Do not restart to clear it.** Publishing a fresh anchor over a chain you have not verified is exactly what restoring a stale backup looks like, and the design refuses it: a scheduled publication may never create the first anchor for a non-empty chain, and only an operator's explicit, audited `seal` may re-anchor. Restarting is worse than useless — the open-incident state is in-process only, so a restart abandons the incident id, the original incident never receives its recovery row, and the next verification opens a **second** incident under a new id [Open: SRE-R3]. |
| **Escalation** | Security Architect (integrity), Internal Audit (this is their control), Cloud Architect (the anchor directory's deployment identity, O-54). If the platform is also halted, this is not RB-12 — go to RB-13. |
| **Evidence first** | Incident correlation id; the reason verdict with `length`, `anchor_length`, `lag`, `max_lag`; a **read-only copy of the anchor file as found**; the provenance of the last good copy; who holds the anchor principal's credential and who last used it. |
| **Exit** | The anchor directory is restored from the last good copy **by the anchor principal, not by the audit service's identity**; an explicit published verification returns ok; an operator seal is taken and audited; an `audit.anchor.recovered` row exists **under the original incident correlation id**. If that id was lost to a restart, say so in the record rather than closing quietly. |
| **Standing gap** | The second principal that owns the anchor directory does not exist yet (O-54); until it does, the "different principal" property is modelled, not evidenced [Open: O-54]. |

### RB-13 — A store will not open: the platform does not start (ADR-018, ADR-020, O-111, O-156)

| | |
|---|---|
| **Trigger** | A process refuses to start: `StoreIntegrityError` (control-store journal chain broken, or state does not match the journal), `StoreError` (SQLite unreadable, locked past the 5 s busy timeout, disk gone), `AuditIntegrityError` (audit chain refused at open). |
| **How you find out — read twice** | **Not from an alert.** Both verifications run inside the store constructors, which run *before* the alert router is wired: no S1 is emitted, no auto-action fires, nothing is delivered, nothing reaches a dashboard [Open: SRE-R1]. **Your only signal is a process that will not boot** — in a cluster, pods that never become ready. Treat "the platform did not come back after a restart" as this runbook until proved otherwise. |
| **First action** | (1) **Stop restarting it.** A crash loop adds nothing and, if the cause is disk or memory pressure, makes it worse. (2) Read the exception class: the two classes have opposite recoveries. `StoreError` is an **availability** failure — disk, mount, stuck writer — fixed by fixing the environment. `StoreIntegrityError` / `AuditIntegrityError` is an **integrity** failure and is a security incident until the Security Architect says otherwise. (3) Take a byte-for-byte copy of **both** store files and the anchor directory *before* any repair attempt. |
| **Never** | Do not open a store with verification disabled to "get trading back". Do not delete or truncate a journal to make an open succeed. Do not restore a control store without restoring the audit store and the anchor directory as a **matched set**, and **do not restore the audit store to a length below the last published anchor** — that reads as a truncated chain and carries `killswitch_platform` platform-wide (DR_PLAN, and the finding D-01). The gateway submitting nothing while the store is unavailable (`execution.store_unavailable`, S1, auto-action `none`) is the control working: no order reaches a broker while this is true. |
| **Watch for the amplifier** | If the cause is time or memory rather than corruption — a very long journal, a very long chain — the restart itself is the problem: `verify()` is O(n) in **time and memory** and neither is measured (O-156). A store that cannot finish verifying within the process's memory or the orchestrator's start-up timeout will never open, and restarting cannot change that. The lever now is more memory and a longer start-up budget; the lever later is compaction and retention (O-111, O-133) — which are integrity and legal decisions, not SRE tuning knobs (O-135). |
| **Escalation** | Backend Lead (store), Security Architect (any integrity verdict), Cloud Architect (disk, node, restore), Chief Risk Agent before any account resumes, Compliance if the audit trail is affected. S1; incident command per this document. |
| **Evidence first** | Exception class and message including the failing sequence number; copies of the control store, the audit store and the anchor directory **as found**; the journal length, chain length and anchor count at failure; the last clean start of the same process; disk, memory and start-up-timeout state at the moment of failure. |
| **Exit** | The store opens and verifies from a restored copy; the audit chain verifies **against the witness**, explicitly (the open-time verify does not check it); reconciliation against broker statements has run before any account resumes; the resumption is a two-person act; and the post-incident review records the three history lengths and the four-phase timing so the incident becomes an O-18 input rather than an anecdote. |

### RB-14 — What a DR drill record must state (a requirement, not an incident) — O-18

A drill that does not say what it ran against is not evidence, and a drill on a fresh system measures the best case and will be quoted as the general case. Every DR drill record must state, as a precondition of being cited anywhere [Committee]:

1. **Control-store journal rows** at drill time.
2. **Audit chain events** at drill time.
3. **Anchor records** at drill time — they grow at one per `anchor_every` events plus one per seal, so they are **not** derivable from (2).
4. The **wall-clock split**: restore · control-store `verify()` · audit-chain verify · anchor verify · reconciliation-before-reopen. A single total conceals which of the four to attack.
5. **Peak resident memory** during each verification — the term that decides whether a large restore completes at all.
6. The **environment and disk class**, with the explicit statement that none is chosen yet (H-05).
7. Whether the cell was **fresh or aged**, and if fresh, the sentence *"this is a best case and may not be quoted as a general recovery time"* **in the record itself**, not in a covering note.
8. **Who acted**: the identities that restored the audit store and the anchor directory, and whether they were different people.

A drill record missing any of 1–3 or 7 produces a number the SRE Lead will refuse to carry into O-18. **No RPO or RTO figure is stated or implied here** [Open: O-18] [Source: 00].
