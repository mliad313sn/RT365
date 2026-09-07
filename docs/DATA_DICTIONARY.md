# DATA_DICTIONARY

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Data Architect | Quant Research Lead | ARB | B | Draft v1.0 |

| Field | Type | Definition | Source of truth | Classification |
|---|---|---|---|---|
| market_ts | timestamp (UTC) | Time the event occurred at the venue | Provider | Licensed |
| ingest_ts | timestamp | Time received by Market Data | Platform | Internal |
| decision_ts | timestamp | Time the risk decision was written | Risk Engine | Internal |
| provenance | enum | licensed_feed / news_adapter / user_text / internal_doc | Ingest | Internal |
| freshness_budget | duration | Max market_ts age per instrument class [Open: O-03] | Policy | Internal |
| policy_version | string | Version of RISK_POLICY/LIMIT_MATRIX applied | Policy store | Internal |
| reason_code | string | Machine reason with plain-language mapping in the reason dictionary | Risk/Eligibility | Internal |
| thesis_code | string | Strategy rationale identifier carried by intents | Strategy | Internal |
| confidence | 0–1 | Model-reported confidence; informational, not a control input | Model | Internal |
| capital_envelope | money | Max capital at risk for bounded autonomy per account/strategy | Trading Risk Committee | Confidential |
| snapshot_id | string | Reproducible data snapshot reference | Data platform | Internal |
| fencing_token | int | Monotonic executor lease token | Execution Gateway | Internal |
Extend per contract in API_OPENAPI.yaml.
