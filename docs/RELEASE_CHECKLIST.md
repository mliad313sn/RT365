# RELEASE_CHECKLIST

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB, boards per gate | A–F | Draft v1.0 |

Gates [Source: 12]. Assertions without evidence links count as absent.
| Gate | Criterion | Evidence link (AUDIT_EVIDENCE_INDEX #) | Approver | IVA verdict |
|---|---|---|---|---|
| A | Approved charter, personas, jurisdiction hypothesis, measurable outcomes | #1 charter approved D-042; #1b hypothesis row D-043 (country fact Q-11-1 open); outcomes D-044; personas × mode D-045; #30 council packets | Product Council, Compliance & Legal Committee (advisory); Product Owner decides (D-039/D-040) | see GATE_REPORTS/ (re-convened 2026-09-08) |
| B | Threat model, data flows, ADRs, capacity model, control ownership | #2, #2b, #10, #11, #12 | ARB, Security & Privacy Board | see GATE_REPORTS/ |
| C | Broker sandbox, deterministic risk tests, reconciliation, audit, support workflows | #3, #4, #5 (sim only), #5b | Trading Risk Committee, CAB | see GATE_REPORTS/ |
| D | Independent quant validation, security assessment, compliance sign-off, trained operators, rollback drill | | MRC, S&P Board, C&L Committee, CAB | |
| E | Capital envelope, runtime monitoring, automatic halts, model thresholds, incident command | | Trading Risk Committee, Exec Steering, CAB | |
| F | No unresolved critical; highs resolved/risk-accepted; SLO, DR, accessibility, support, disclosures, legal terms, release dossier | | All boards, Exec Steering | |
Each gate authorises only the next environment on the ladder [Source: 00].
