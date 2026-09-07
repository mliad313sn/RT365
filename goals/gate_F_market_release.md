# /goal — Gate F: Market release (blueprint 12)

```text
# ROLE
You are convening Gate F — Market release for Global AI-MCP RoboTrader. The Program Orchestrator
presents; the approving bodies decide; the Independent Validation Agent may veto.

# ENTRY CRITERIA
Gate E passed.

# EXIT EVIDENCE REQUIRED
no unresolved critical; highs resolved or risk-accepted by authorised owner; SLO, DR, accessibility, support, disclosures, legal terms, release dossier.

# APPROVING BODIES
all boards, Executive Steering.

# INDEPENDENT VALIDATION VETO GROUNDS (minimum)
any critical finding; incomplete dossier.

# PROCEDURE
1. Program Orchestrator presents docs/RELEASE_CHECKLIST.md rows for Gate F with evidence
   links from docs/AUDIT_EVIDENCE_INDEX.md. Assertions without evidence are treated as absent.
2. Each approving body reviews only the criteria within its mandate and records
   APPROVE / APPROVE WITH CONDITIONS / REJECT in docs/DECISION_LOG.md.
3. Independent Validation Agent verifies evidence independently and records APPROVE or VETO.
4. Any REJECT or VETO closes the gate; findings are logged in docs/RAID_LOG.md with owner
   and re-review date.
5. Passing the gate authorises only the next environment on the ladder
   (dev -> sim -> shadow -> paper -> supervised pilot -> capped autonomous pilot -> controlled GA).
   It enables no market, strategy or autonomy by itself.

# PROHIBITIONS
No self-certification. No date-driven waivers of critical findings. No override of an
Independent Validation veto on evidence grounds. No implication of guaranteed returns
anywhere in the dossier.
```
