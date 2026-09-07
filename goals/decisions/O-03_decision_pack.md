# /goal — Decision pack O-03: Numeric freshness and latency thresholds

```text
# ROLE
You are preparing decision pack O-03 for Global AI-MCP RoboTrader. Decision owner:
SRE Lead. Must close by Gate E. You prepare; the owner decides.

# QUESTION TO CLOSE
Freshness budget per instrument class; risk-decision latency, order-ack, event-lag targets from measured baselines.

# TASKS
1. State what the blueprint already fixes about this question [Source: NN] and what it
   leaves open.
2. Gather inputs: read the relevant docs/ files; where external facts are needed
   (regulation, vendor terms, market conventions), list them as questions for humans with
   the exact source to consult. Do not invent regulatory status, prices, vendor
   capabilities or thresholds.
3. Propose 2-3 options with pros, cons, cost, risk, reversibility and which controls or
   tests each affects.
4. Recommend one option with confidence level and evidence provenance.
5. Draft the decision record for docs/DECISION_LOG.md and the resulting edits to the
   owning artefacts (e.g. LIMIT_MATRIX.md, COMPLIANCE_MATRIX.md, ADR).
6. List the human actions required to make the decision effective (signature, contract,
   configuration) and add them to docs/MISSING_ACTIONS.md with owner and date.

# OUTPUT
Decision pack: context, options table, recommendation, decision record draft, artefact
diffs, human-action list. Mark the RAID entry O-03 'Pack ready' — it closes only when
the owner records the decision.
```
