# Product Owner weekly — 2026-09-08

| Field | Value |
|---|---|
| Chair | Product Owner (human decides; the AI delegate operates and decides delegated matters under D-040) |
| Prepared by | Product Owner delegate (AI), from the ledgers at the branch head |
| Portfolio | Meridian IT-PMO 5.10.0, programme RBT, 16 projects, 134 RAID items (`make pmo-sync`, 17 incremental writes) |
| Evidence base | `make all` green: 211 tests, 22/22 quartet areas with a full quartet, 191 evidence records; CI and the three-platform release workflow green on the pushed head |
| Standing rule | Nothing here promotes any environment beyond dev/sim. No market, broker, licence, limit or autonomy is enabled. Profit is an objective, never a promise. |

## 1. What moved this week

Five register items were built and merged, each tests-first with its control quartet, its session packet and its ledger rows.

| Item | What now exists | Decision |
|---|---|---|
| B-10 (E06) | Typed legal record, disclosure acknowledgement, per-mode consent and classification evidence as decision inputs; CP-CLASS, CP-DISCL, CP-MODE-CONSENT fail closed | earlier in the week |
| B-1 (E07) | Durable control state on a store seam: lease and fencing counter, outbox/inbox, gateway indexes and Kill Switch activations survive a restart, with tamper-evident rows and a hash-chained journal | D-058 |
| B-3 (E01) | Tenant isolation: per-tenant allowlists, tenant as a server-side principal fact, a tenant predicate on every read and write, tenant-tagged audit rows | D-059 |
| B-4 (E13) | Asymmetric signing: verifiers hold a public trust set and no private material, rotation is overlap-then-retire, the dev HMAC key is refused outside dev/sim | D-060 |
| B-5 (E11) | Durable audit in its own store, witnessed by an external anchor written by a different principal; a truncated tail or a restored stale backup is detectable | D-062 |

Two boards met on the Gate B exit evidence and one decision covered their advice (D-061). The executable was fixed for Windows after the release workflow caught a real defect: the frozen binary had no time-zone database, so venue calendars failed on that platform (TC-PKG-005, O-119).

## 2. The finding that matters most

**Two of the four Gate B exit-evidence documents were refused by their own boards.** The Security & Privacy Board did not accept SECURITY_PLAN v1.0; the Architecture Review Board did not accept DATA_FLOWS v1.0. THREAT_MODEL and CAPACITY_MODEL were accepted only with conditions, and no number in the capacity model was accepted because none was presented.

This is the governance working, not failing. The code was ahead of its documents: DATA_FLOWS drew a flow on a route the declared topology forbids and omitted the only persistent data-at-rest flow in the envelope. New versions are in preparation with the exact conditions the boards wrote (O-129). **Gate B is not convened until they exist**, which is the right sequence and moves the gate later than the earlier plan implied.

## 3. Decisions taken under delegation this week

D-052..D-057 (Gate B decision packs), D-058 (durable stores, with the Execution-plane store separated from shadow), D-059 (tenant isolation, with the platform-operator principal as an IdP claim), D-060 (asymmetric signing), D-061 (the two board packets: four document verdicts, the store-integrity scheme, the write-scope guard replaced by a CI path-ownership check), D-062 (durable, witnessed audit).

Every one is recorded with its alternatives and its conditions. None of them approves a gate, enables a market or accepts a residual risk that is the human owner's to accept.

## 4. What the owner alone can still do

Twelve human acts remain open. The ones blocking the most: the operating entity and country (A-1), an owner-authored ratification of the delegation on the committed tree (A-2), engaging counsel (H-25), naming the second humans for two-person controls (H-26), a real Meridian instance (H-28), the key ceremony for a real signing key (H-20, O-127), code-signing certificates (H-30), and filing the Meridian value requirements upstream (H-31).

Nothing an agent can do substitutes for these. They are facts only the owner knows, or acts only a human can sign.

## 5. Meridian, as the tool driving this programme

The loop we opened on Monday closed the same day: all twelve improvements we filed upstream were delivered in Meridian 5.10.0, which now carries a request register that reads this repository. Measured on the new version: 513/513 tests, the first hour works with no manual steps, and our loader wrote 134 RAID items with a second run creating nothing.

A new list of twelve requirements (V-1..V-12) aims at the owner's actual goal — proving a project was worth doing, not only that it was run well. The gap is specific: Meridian has a business case and a benefits model, but neither is writable through the integration API, no gate enforces the case, nothing chases a benefit review, and there is no forecast-versus-realised report. One item we published as their defect was ours: our sixteen projects carried two gate ladders because our loader never declared one, which their code has accepted since the feature shipped. It is withdrawn, re-filed narrower, and fixed on our side.

## 6. Risks I would raise at the table

- **The blast radius of the audit control.** A corrupted audit store halts trading platform-wide by catalogued auto-action. Right for a control envelope; the largest blast radius we carry. It should be chosen deliberately (O-137).
- **Fail-closed conditions are multiplying.** A missing trust set, a lost audit witness and an unreadable control store each stop the platform. Each is correct alone. Together they are three new ways to be down at 03:00 with no runbook (O-126, O-134).
- **Everything is still dev/sim.** Nothing is measured on real infrastructure: no cross-process store behaviour, no power-loss test, no KMS, no WORM bucket, no real broker. The evidence is honest about this, and it is the distance to Gate C.

## 7. Next week

Finish the four document versions and convene Gate B on a CI-evidenced commit; the IVA re-validation on that head (C-1); FX as a deterministic decision input (F-3) for the multi-currency claim; then the Gate C build items in order — real broker adapters (B-6), licensed data (B-7), margin and reconciliation models (B-8), risk thresholds from the approved matrix (B-9).
