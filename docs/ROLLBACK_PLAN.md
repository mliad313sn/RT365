# ROLLBACK_PLAN

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| SRE Lead | Chief Risk Agent | CAB | C | Draft v1.0 |

Triggers [Source: 00]: guardrail breach, integrity-check failure, reconciliation failure, observability loss, SLO safety breach.
| Change type | Rollback action | Safety step first |
|---|---|---|
| Service release | redeploy previous signed artefact via lease transfer | move affected accounts to Supervised |
| Risk policy / limits | revert to previous policy_version (maker-checker fast path) | block new risk until reverted |
| Model / prompt | re-point to champion version | suspend challenger signals |
| MCP tool | revoke registry signature for the tool | — |
| Jurisdiction flag | set OFF (single person may disable; enabling needs dual key) | — |
| Data pipeline | replay from last good snapshot ID | freshness rejections protect risk |
Drill: rollback of each type evidenced before Gate D [Source: 12].
