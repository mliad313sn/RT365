# /goal — External dependency workflow: Broker / exchange onboarding and certification

```text
# ROLE
You drive the external dependency "Broker / exchange onboarding and certification" for Global AI-MCP RoboTrader to closure.
Owner: Broker-Connector Lead + Legal Agent. You prepare every artefact, question and checklist; humans perform the
acts only humans can perform (sign, pay, authorise, operate). Track each such act in
docs/MISSING_ACTIONS.md with owner, due date and blocking gate.

# STEPS
1. Identify candidate brokers for the target cell (O-11) with API, sandbox, asset coverage, jurisdictions served
2. Prepare the vendor assessment (docs/VENDOR_ASSESSMENTS/TEMPLATE.md) and the questions for the broker (API terms, sandbox access, order types, rate limits, statements, algorithmic-trading obligations)
3. Draft the commercial/legal request; humans sign
4. Once sandbox credentials exist in the vault: run E03 certification harness; file BROKER_CERTIFICATIONS/<broker>.md
5. Gate C evidence: certification complete; unsupported features documented

# RULES
Never assume the dependency is satisfied; it is [Open] until the evidence file exists.
Never fabricate vendor capabilities, prices, regulatory positions or contract terms.
Report weekly: status, blocking human actions, gate impact.
```
