# PRIVACY_IMPACT

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Privacy Lead | Security Architect | Security & Privacy Board | D | **Draft v1.1, 2026-09-08 — data-at-rest rows, the derived-record position on the control-store journal, the erasure position against the append-only audit chain and the platform-auditor envelope added from docs/SESSIONS/REVIEW_2026-09-08_data_flows_privacy.md. Reviewer signature pending; Board approval pending; nothing here is accepted.** |

Obligations [Source: 06]: purpose limitation, minimisation, consent where applicable, residency/transfer mapping, retention schedules, deletion workflows, subject rights, DPIA where required, privacy-safe telemetry.

**Reading rules for this document [Committee].** (1) No retention period, lawful basis, notification duty or jurisdictional requirement is stated here: those are counsel's answers through H-04 (scope H-25) and the Compliance Agent's matrix, and they are [Open: O-09, O-10]. (2) A cell marked [Open] is an unanswered question, never an implied answer. (3) **Retention fails closed**: with no `(record_class, jurisdiction)` schedule a deletion request is `SUPPRESSED_NO_SCHEDULE` and nothing is deleted (D-025). (4) **A DPIA exists before a cell is enabled**, not after. (5) Classification of a data flow is proposed by the Data Architect and decided by the Security & Privacy Board; this document records the privacy handling consequence, not the classification decision [Open: O-106].

## 1. Data categories in motion [Source: 06]

| Data category | Purpose | Legal basis (per jurisdiction) | Residency | Retention | Deletion / legal hold [O-09] | Telemetry redaction |
|---|---|---|---|---|---|---|
| Identity & contact | account operation | [Open: O-10] | per tenant | regulatory record period [Open: O-09] | hold suppresses deletion; logged | redacted at emission |
| Trading records | execution, reporting, surveillance | regulatory duty [Open: O-10] | per tenant | per COMPLIANCE_MATRIX [Open: O-09] | hold by default | pseudonymised |
| Session/security logs | security | legitimate interest [Open: O-10] | per cell | security retention [Open: O-09] | — | IP/user redacted |
| AI context | analytics | contractual [Open: O-10] | per cell | short [Open: O-09] | none stored beyond audit refs | masked account state only; **no personal or customer-identifying data reaches a processor before the DPIA for that cell (O-10) and signed terms (H-06) exist** |

## 2. Data at rest — the artefacts under `store_dir` and `anchor_dir` [Committee: REVIEW_2026-09-08_data_flows_privacy §6]

Five artefacts are now written to disk by the dev/sim code paths (DATA_FLOWS DF-10, DF-11, DF-12, DF-21, DF-22). Between them there is today **no retention rule, no backup schedule, no owner split and no residency statement**. The rows below are the Privacy Lead's positions; the owner, backup and residency columns need the Cloud Architect (O-136), the SRE Lead (T-81, H-19) and the DPIA (O-10) [Open].

| Ref | Artefact | Category / handling class | Purpose | Residency | Retention position | Deletion / legal hold | Owner (proposed) |
|---|---|---|---|---|---|---|---|
| PI-1 | `control_state.sqlite` (live rows) | Confidential, **customer-identifying** | operating the control envelope (orders, indexes, leases, outbox/inbox, activations) | tenant cell — **not answerable today**: `Tenant.residency_region` is read by no code [Open: F-7, H-05, O-10] | live rows may be reduced to the shortest period consistent with the operational need; **no schedule exists → fails closed, nothing deleted** (D-025) [Open: O-09] | no erasure path exists (PI-2); a hold must suppress any future compaction | Backend Lead (data), Cloud Architect (host) |
| PI-2 | `journal` table of the control store | Confidential, **derived record** | integrity: every `put`/`delete` with its full value, `correlation_id` and timestamp, chained | as PI-1 | **inherits the retention class of the records it duplicates** (today: trading records); no independent schedule; compaction (O-111) is the retention mechanism | **there is no erasure primitive**: `delete()` removes the row but not the journalled value, and removing a journal entry makes `verify()` refuse the store at open (fail closed). Adding erasure is a design change to the integrity scheme [Open: O-111, O-128, O-135] | Backend Lead; **Privacy Lead consulted on the compaction design** |
| PI-3 | `audit_state.sqlite` and `audit_anchors.jsonl` | Regulated record (chain); Internal + pseudonymous identifier and timing metadata (anchors) | evidence of what happened, and an external witness that it was not rewritten | audit replication is contemplated cross-cell (ADR-007) — **that is a transfer** [Open: O-10]; the witness store is outside our own storage by design [Open: O-54] | schedule owed per record class and jurisdiction [Open: O-09, O-135]; anchors retained at least as long as the period they witness. **Do not commit to WORM before the schedule exists** | append-only by design: **no update and no delete path at any layer**, and no erasure is possible today — see §3 | SRE Lead / Internal Audit — **a different owner and backup schedule from the control store** (O-136) |
| PI-4 | `revocations.jsonl`, `nonces.jsonl`; Kill Switch activation records | Internal + **Personal (actor id)** | revoked grants, consumed nonces, activations with the acting human's id | same cell as the control store; both journals move onto the store seam before shadow (D-061 (6)) | security-log class [Open: O-09]; nonces may be compacted once expiry is provable; **revocations must outlive any activation they revoke** (T-81) | restored as **one unit** with the control store (D-058 (e)); free-text `reason` needs minimisation [Open] | MCP Security Agent (semantics), Backend Lead (storage) |

## 3. Erasure against an append-only audit chain [Committee: REVIEW_2026-09-08_data_flows_privacy §7] [Open: O-135, O-09, O-10]

- The audit chain **cannot delete, and that is deliberate**: no delete path is requested and one would be refused.
- **The platform cannot honour an erasure request today, and no gate report, DPIA, customer document or external statement may say otherwise.** The audit event stores the payload inline and verification recomputes its hash, so redacting or removing a payload makes the store refuse to open and, through `audit.chain_verification_failed`, engages the platform-wide Kill Switch.
- Erasure is never a reason to disable, weaken or skip a verification; recovery is restore-then-verify (O-134).
- `payload_hash` and truncated target hashes are **unsalted** digests over low-entropy values: they are pseudonymisation, not removal, and they are re-derivable by enumeration.
- The remedies require build changes, not policy sentences: **payload minimisation** (payload outside the hashed record, with a "withdrawn" state that verifies) and **crypto-shredding** (per-subject keys with custody, two-person destruction and a keyed or salted hash, or shredding does not shred). Because `tenant`, `account` and `actor` sit in the hash preimage, **actor and account must be keyed pseudonyms from the first write**, resolvable through a separately erasable map. This decision must be taken **before the first environment holding a real person's data** — a Gate C entry item, not a Gate D item [Open: O-P5 proposed].
- Rectification against the chain is a **forward-only correction event**, never a rewrite; a subject-access answer is assembled from a view over the chain.

## 4. Platform-auditor privacy envelope (unfiltered cross-tenant read) [Committee] [Open: O-121, O-10, R-06]

Set before any build, as the Security & Privacy Board asked (D-059, D-061 (7), COUNCIL_2026-09-08_gate_B_spb_docs §3.4). The full text is docs/SESSIONS/REVIEW_2026-09-08_data_flows_privacy.md §8 (PA-0..PA-10). In summary: no build or enablement on real personal data before this envelope, the DPIA and the read's own audit path (PA-0); three named purposes only — assurance, investigation, legal hold/regulatory request — with a reference, else refused (PA-1); **every unfiltered read is itself an audit event written before the result is returned** (PA-2); pseudonymised identifiers and withheld payloads by default, reveal being a second act with a second approver from a different line (PA-3); read-only, time-bound, tenant-less IdP claim, never held by an AI or MCP component (PA-4); **a region mismatch is refused, not silently filtered** (PA-5); secrets, key material, the re-identification map, unentitled market data, third-party free text and bulk payloads may **never** be exported (PA-6); the read record is a Regulated record (PA-7); tenant transparency by default unless lawfully suppressed (PA-8); fail-closed refusal conditions (PA-9); and the envelope is enforced **above** the store seam, never by exposing it (PA-10).

## 5. Telemetry [Source: 06; NFR-PRV-01]

Redaction happens **at emission** (`observability/rtobs/logging.py`, TC-OB-002) and is **pattern-based**: e-mail, bearer tokens, vault references, 12–19-digit numbers, `acct-`/`cust-`/`tenant-` prefixed identifiers, IBAN-shaped strings, IPv4 addresses and secret key-values. **The actor/principal identifier is not redacted**: it is retained deliberately so that operator actions remain attributable. Its purpose, retention and access rule are owed [Open: PI-6]. Free-text fields (`reason`, prompt content, break notes) are not covered by any pattern and are where personal data arrives unannounced; a field-level inventory is owed with the DPIA [Open: O-10].

## 6. DPIA status

DPIA per launch jurisdiction: [Open: O-10]. **A DPIA exists before the cell is enabled.** Counsel engagement is a human act (H-04, scope H-25) and no jurisdictional position is stated anywhere in this document [Committee] [Source: 00].
