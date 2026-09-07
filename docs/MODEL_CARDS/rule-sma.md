# Model Card — rule-sma v0.1  [Source: 04]
| Field | Value |
|---|---|
| Owner / Validator (different line) | Quant Research Lead (owner) / Model Risk Lead (validator) — validation **not performed** |
| Intended use | Deterministic rule "model" that emits `strategy.signal.v1` for the simulation strategy strat-sma-xover; exists to exercise the explainability contract (thesis code, evidence references, confidence) and the MCP identity pinning of model_id/model_version |
| Prohibited use | Any live or paper trading decision for a real customer; any claim of predictive power |
| Inputs / provenance classes accepted | `market.snapshot.v1` rows with provenance `simulated` or `licensed_feed`; never `news_adapter` or `user_text` |
| Outputs / schema | `strategy_service.signals.Signal` (contracts/events/strategy.signal.v1.json); a signal without evidence references is schema-invalid |
| Evaluation datasets (owner, licence) [Open: O-06] | simulated feed only |
| Benchmark results | none (fixture) |
| Hallucination / adversarial / instability test results | not applicable to a rule model; the model test suite (C10 §5) applies to LLM-backed strategy agents once a provider exists [Open: O-05] |
| Drift metrics and thresholds | none set; `model.drift.v1` event and `RT-DRIFT` runtime halt exist for real models |
| Champion/challenger status | none |
| Rollback target | none (single version) |
| Retirement criteria | replaced when the first LLM-backed strategy agent is registered under P2 |
| Approval record (Model Risk Committee) | none |
