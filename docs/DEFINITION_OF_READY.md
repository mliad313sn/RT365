# DEFINITION_OF_READY

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | QA Lead | CAB | B | Draft v1.0 |

A story is Ready when all are true [Committee, derived from 14]:
- [ ] Linked to an FR and an RTM row; epic and gate identified
- [ ] Story template fully filled (value, scope, assumptions, API/event, security/privacy, observability, migration, rollback)
- [ ] Given/When/Then acceptance written and reviewed by QA
- [ ] If control-bearing: control quartet test IDs reserved; 2nd-line reviewer named
- [ ] Threat-model delta assessed (none / minor / requires Security Architect)
- [ ] Data classification and residency impact assessed by Privacy Lead where personal data is touched
- [ ] Dependencies and blockers logged in RAID_LOG.md
- [ ] No assumption of regulatory permission, licensing, broker capability or market access left implicit
