# RELEASE_CHECKLIST

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB, boards per gate | A–F | Draft v1.0 |

Gates [Source: 12]. Assertions without evidence links count as absent.
| Gate | Criterion | Evidence link (AUDIT_EVIDENCE_INDEX #) | Approver | IVA verdict |
|---|---|---|---|---|
| A | Approved charter, personas, jurisdiction hypothesis, measurable outcomes | | Product Council, Exec Steering | |
| B | Threat model, data flows, ADRs, capacity model, control ownership | | ARB, Security & Privacy Board | |
| C | Broker sandbox, deterministic risk tests, reconciliation, audit, support workflows | | Trading Risk Committee, CAB | |
| D | Independent quant validation, security assessment, compliance sign-off, trained operators, rollback drill | | MRC, S&P Board, C&L Committee, CAB | |
| E | Capital envelope, runtime monitoring, automatic halts, model thresholds, incident command | | Trading Risk Committee, Exec Steering, CAB | |
| F | No unresolved critical; highs resolved/risk-accepted; SLO, DR, accessibility, support, disclosures, legal terms, release dossier | | All boards, Exec Steering | |
Each gate authorises only the next environment on the ladder [Source: 00].
