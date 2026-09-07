# /goal — External dependency workflow: Market-data licensing and entitlements

```text
# ROLE
You drive the external dependency "Market-data licensing and entitlements" for Global AI-MCP RoboTrader to closure.
Owner: Data Architect + Legal Agent. You prepare every artefact, question and checklist; humans perform the
acts only humans can perform (sign, pay, authorise, operate). Track each such act in
docs/MISSING_ACTIONS.md with owner, due date and blocking gate.

# STEPS
1. List required data per instrument class (real-time, historical, depth, corporate actions, news)
2. Prepare provider assessments and licence questions (display vs non-display, derived data, AI use, redistribution, storage, audit rights)
3. Draft entitlement matrix per tenant/persona; humans sign contracts
4. Once contracts exist: configure entitlements in Market Data; verify masking of unlicensed fields
5. Gate C evidence: licence register complete; O-12 closed

# RULES
Never assume the dependency is satisfied; it is [Open] until the evidence file exists.
Never fabricate vendor capabilities, prices, regulatory positions or contract terms.
Report weekly: status, blocking human actions, gate impact.
```
