# DEFINITION_OF_DONE

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Program Orchestrator | Independent Validation Agent | CAB | B | Draft v1.0 |

A story is Done when all are true [Committee, derived from 00, 11]:
- [ ] Code merged with reviewer ≠ author; protected paths approved by 2nd-line CODEOWNER
- [ ] Unit, contract and integration tests pass; control quartet passes for every critical control touched
- [ ] Evidence record written (requirement ID, environment, data version, expected, actual, evidence link, owner, reviewer) [Source: 11]
- [ ] Observability delivered: metrics, structured logs with correlation ID, alerts in ALERT_CATALOG.md
- [ ] Security scans clean (SAST/DAST/SCA/secret scan); SBOM updated
- [ ] Rollback verified in the lowest applicable environment
- [ ] Documentation and RTM updated; ADR written if a standard was changed
- [ ] Accessibility checks pass for UI stories
- [ ] Not promoted beyond the environment the current gate authorises
