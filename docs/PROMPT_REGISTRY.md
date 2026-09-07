# PROMPT_REGISTRY

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Model Risk Lead | MCP Security Agent | Model Risk Committee | D | Draft v1.0 |

| Prompt ID | Version | Purpose | Model | Provenance rules applied | Eval suite result | Approved by | Status |
|---|---|---|---|---|---|---|---|
| P-STRAT-SIGNAL | 0.1 | Strategy agent signal generation | [Open: O-05] | untrusted text delimited; no instruction from data | pending | — | Draft |
| P-RESEARCH-SUMM | 0.1 | Research summarisation (Observe mode) | [Open: O-05] | same | pending | — | Draft |
Rules [Source: 04]: every prompt change re-runs hallucination, adversarial, instability and unsafe-tool-selection tests; champion/challenger before promotion; rollback path recorded.
