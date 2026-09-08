# ROADMAP

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Director | Program Orchestrator | Product Council, Executive Steering | A | Draft v1.1 (2026-09-08, D-057 columns; Product Council endorsement pending) |

Roadmap is gate-driven, not date-driven [Committee]. D-057 (2026-09-08) supersedes the earlier sentence that dates would be set once the Gate B capacity model exists: the calendar is decoupled from capacity numbers; each phase carries predecessor, condition and the measurement that produces any date; calendar dates appear only for the owner's own committed acts (register §A) until Gate C/E baselines exist [v1.1 adds the columns; Open: Product Council endorsement].

| Phase | Gate | Epics in focus [Source: 14] | Environment authorised [Source: 00] | Predecessor | Condition to start [Committee] | Measurement that produces the date (D-057) |
|---|---|---|---|---|---|---|
| 0 Discovery | A | E15 (jurisdiction hypothesis), charter | — | — | charter draft, personas, outcomes | Gate A passed with conditions 2026-09-08 (D-048); conditions GA-C1..GA-C8 tracked in the register |
| 1 Foundation | B | E01, E13, architecture ADRs, contracts | development, simulation | Gate A | GA-C1..GA-C3 closed; IVA re-validation on a CI-evidenced commit (C-1); Board approval of THREAT_MODEL, SECURITY_PLAN, DATA_FLOWS, CAPACITY_MODEL (O-106) | date = day the IVA report on the committed head is filed; nothing else produces it |
| 2 Data & execution core | C | E02, E03, E04, E05, E07, E12 | shadow, paper | Gate B | B-1 (done dev/sim, D-058), B-4, B-6 broker sandbox certification, A-8 limit matrix, A-10 broker contract, replicated stores (R-05) | date = broker sandbox certification 14/14 rows plus deterministic risk tests on the deployed topology; a shadow soak of measured length sets the paper date [Open: baseline] |
| 3 Governance & AI | D | E06, E08, E09, E10, E11, E14 | supervised pilot | Gate C | independent quant reproduction, security assessment closure, compliance sign-off for one enabled cell (dual key), trained operators, rollback drill | date = paper-trading evidence window of the length the Model Risk Committee sets from the strategy card [Open: O-40 baseline]; no date before a cell is legally enabled |
| 4 Autonomy | E | runtime halts, capital envelope, incident command | capped autonomous pilot | Gate D | capital envelope decided, runtime monitors with measured thresholds, automatic halts drilled, incident command certified | date = supervised-pilot window measured against the Gate D exit metrics; the Trading Risk Committee proposes, the owner decides |
| 5 Launch | F | E15, disclosures, support, DR, accessibility | controlled GA per market | Gate E | no unresolved critical; highs risk-accepted by the authorised owner; SLO, DR, accessibility, support, disclosures, legal terms, release dossier per market | date per market = the later of the legal enablement record and the pilot exit; never announced before dual-key enablement |
