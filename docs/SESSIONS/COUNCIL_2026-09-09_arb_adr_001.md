# COUNCIL 2026-09-09 — ARB with the Security & Privacy Board on ADR-001 (plane topology), O-177

| Pack author | Council to convene | Body | Standing | Gate blocked |
|---|---|---|---|---|
| Enterprise Architect (1st line, owner of `docs/ADRs/`, `docs/NFR.md`, the C4 diagrams) | ARB **with the Security & Privacy Board** — the pairing named for ADR-001 in `docs/SESSIONS/REVIEW_2026-09-08_adr_007_and_status.md:100` | Architecture Review Board (advisory) + Security & Privacy Board (advisory) | **Advisory only (D-039, D-040)** — this packet contains **no approval and no decision**; the Product Owner, or the delegate under D-040, decides | **B** (entry condition O-177) |

Prepared on branch `claude/project-owner-agent-setup-hi3xqu` at `442cebd`. **This session writes exactly one file — this one.** `docs/ADRs/ADR-001.md`, `docs/NFR.md`, `docs/RAID_LOG.md`, `docs/DECISION_LOG.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/AUDIT_EVIDENCE_INDEX.md`, `infra/`, `libs/`, `services/`, `scripts/` and `test/` are **read only** here; every row and every paragraph this packet proposes for them is quoted as proposed text for its owner [Source: 13; CLAUDE.md].

---

## 0. How to read this packet

Every statement carries **[Source: path:line]** (a file read in this worktree, quoted or paraphrased with its location), **[Committee]** (this pack's reasoning or a cited council's) or **[Open]** (unresolved, with the register id that settles it). **[Verified]** marks a command run in this worktree whose output is quoted verbatim in §3.3. No cloud capability, price, latency, throughput, broker capability, venue capability, licence term or regulatory status is asserted anywhere [Source: 00]. **A target is never evidence. A declaration is never enforcement.**

**One deliberate deviation from the ADR-007 precedent, stated so no reader is misled [Committee].** `docs/SESSIONS/COUNCIL_2026-09-08_arb_adr_007.md` §4 records positions per seat. In this packet the seats in §4 have **not** met: the positions are drafted by the Enterprise Architect *in role*, and every one of them is anchored to a document, a code line or a standing finding that already exists in the tree, cited inline. **No seat has confirmed its wording, and a position becomes that seat's only when that seat says so.** This is a pack **for** the ARB and the Security & Privacy Board to test, not their minute. The chair of neither board has seen it.

---

## 1. The author's independence declaration — read this before the recommendation [Committee] [Source: 13]

1. **I did not author ADR-001.** It arrived in the bootstrap commit `03e6739`; the only other commit that has touched it is `dad8242` ("ADR status reconciliation"), which is mine and which added the undecided note now at `docs/ADRs/ADR-001.md:4` [Verified: `git log --oneline -- docs/ADRs/ADR-001.md`].
2. **I own the two documents this packet says are wrong.** `docs/NFR.md:20` — NFR-SEC-01, target column "Enforced by policy, tested" — is my file and my text, and §4.4 below says that target column is a claim about a policy engine that has never run. `docs/COMPONENT_DIAGRAMS.md` and `docs/SEQUENCE_DIAGRAMS.md` are mine and contain the word "plane" **zero** times [Verified: grep], although ADR-001 is a decision about which component sits in which plane.
3. **I am not independent of the reliance.** I applied the ADR-007 amendment under D-069, and that amendment cites ADR-001 twice as the thing that delivers route isolation [Source: docs/ADRs/ADR-007.md:17, docs/ADRs/ADR-007.md:24] and once, more honestly, as a proposal [Source: docs/ADRs/ADR-007.md:71]. If ADR-001 is weaker than it reads, ADR-007's Context and its controls table are weaker too, and I wrote both.
4. **Consequence for this session.** I recommend and apply nothing. If the amended text of §7 is accepted, the **Enterprise Architect** applies it to `docs/ADRs/ADR-001.md`; the **Security Architect** (2nd line) reviews the invariant and the **Cloud Architect** reviews the manifest conditions — both are the CODEOWNERS of the artefacts concerned [Source: .github/CODEOWNERS:11]; the **Independent Validation Agent** is asked for a finding on §3.2 and §11; the **Product Owner or the delegate (D-039, D-040)** decides. I approve nothing, and I record nothing in any ledger [Source: 13; CLAUDE.md].

---

## 2. The question put to the council

O-177, opened by the ADR status reconciliation and named in D-069 as the larger item:

> "Among them is ADR-001, the three-plane topology that NFR-SEC-01, every network policy, the policy checker and TC-NET-001..004 are written against: the four passing plane tests in every packet this week test conformance to a proposal. What is owed is the ARB and the Security & Privacy Board recommending on ADR-001 and the delegate deciding (PO-7, PO-2)" [Source: docs/RAID_LOG.md:238].

> "…recommending on ADR-001 is one meeting and a larger part of the Gate B pack than ADR-007 was (O-177)" [Source: docs/DECISION_LOG.md:77 (D-069)].

Five sub-questions:

1. **What does the tree actually enforce**, and which parts of ADR-001's text are enforced by nothing? (the ADR-007 split: invariant versus assertion)
2. **Is the route set right, and is it closed?** Two planes exist in the manifests that ADR-001's title and Decision do not name.
3. **What conditions must attach**, given that no cluster has ever applied a manifest?
4. **NFR-SEC-01 and the RTM**: one requirement id currently carries two different requirements. Which is amended, by whom?
5. **Is ADR-001 already decided?** D-004 and D-042 mention it; O-180 asks whether that reaches the ADRs [Source: docs/RAID_LOG.md:241].

---

## 3. Evidence read, and checks run

### 3.1 Read at `442cebd` [Verified]

`docs/ADRs/ADR-001.md` (19 lines, in full), `ADR-007.md`, `ADR-008.md`, `ADR-013.md`; `infra/kubernetes/namespaces.yaml` and all five files of `infra/kubernetes/network-policies/`, in full; `scripts/check_network_policies.py` in full; `libs/core/rtcore/planes.py` in full; `test/quartets/test_tc_net_planes.py` in full; `test/quartets/test_tc_ai_mcp.py` TC-AI-005; `services/oms/oms/intent_queue.py`, `services/oms/oms/pipeline.py`, `services/execution/execution_gateway/gateway.py`, `apps/web/web_bff/platform.py`, `apps/web/web_bff/app.py`, `apps/cli/rt365_cli/main.py`, `mcp/servers/mcp_servers/tools.py`, `mcp/servers/mcp_servers/egress.py`, `mcp/servers/mcp_servers/runtime.py` (guard call sites only); `mcp/policies/egress.yaml`; `docs/NFR.md`; `docs/REQUIREMENTS_TRACEABILITY.md`; `docs/CONTAINER_DIAGRAM.md`, `docs/CONTEXT_DIAGRAM.md`, `docs/COMPONENT_DIAGRAMS.md`, `docs/SEQUENCE_DIAGRAMS.md`; `docs/THREAT_MODEL.md`; `docs/GATE_REPORTS/GATE_B_2026-09-07.md`; `docs/COMMITTEE_DEEP_DIVE.md` §C2; `docs/RAID_LOG.md` (O-42, O-159, O-163, O-169, O-177, O-178, O-180); `docs/DECISION_LOG.md` (D-004, D-042, D-069); `docs/PO_DECISION_QUEUE.md`; `docs/SESSIONS/COUNCIL_2026-09-08_arb_adr_007.md`; `docs/SESSIONS/REVIEW_2026-09-08_adr_007_and_status.md`; `docs/SESSIONS/REVIEW_C3_mcp_security_agent.md`; `.github/CODEOWNERS`; `.github/workflows/ci.yml`; `Makefile`.

### 3.2 Facts established by reading, each independently checkable [Verified]

| # | Fact | Where |
|---|---|---|
| **F-1** | **ADR-001 is nineteen lines.** Its Decision is one sentence; its Consequences is one line ("Extra latency at plane boundaries; simpler threat model; injection blast radius confined to Analytics"); its Status is `Proposed` and no entry of `docs/DECISION_LOG.md` accepts it | `docs/ADRs/ADR-001.md:1-19`; status at `:2`; Decision at `:10`; Consequences at `:16` |
| **F-2** | **D-004 records "ADR-001..008 proposed to ARB"; D-042 ratifies D-001..D-004** as "ADR-001..008 proposed to the ARB chair". Neither states what ADR-001 decides, what its conditions are, or what alternatives were weighed | `docs/DECISION_LOG.md:12`, `docs/DECISION_LOG.md:50`; the reading is contested at `docs/RAID_LOG.md:241` [Open: O-180] |
| **F-3** | **"Three planes" is not what the tree deploys or models.** `namespaces.yaml` declares **five** namespaces — analytics, control, execution, **security**, **edge** — under a comment that reads "Three planes as namespaces"; `rtcore.planes.Plane` declares **six** identities — EDGE, ANALYTICS, CONTROL, EXECUTION, BROKER, VAULT. ADR-007, amended and applied five days ago, already describes ADR-001 as holding "the five plane namespaces" | `infra/kubernetes/namespaces.yaml:1` vs `:4,:8,:12,:16,:20`; `libs/core/rtcore/planes.py:21-27`; `docs/ADRs/ADR-007.md:24` |
| **F-4** | **The grouping ADR-001 decides is written down nowhere in full.** `CONTAINER_DIAGRAM` says "Twenty bounded contexts grouped into three planes" and then draws an **Edge** subgraph plus four nodes in no plane at all — Notification, Billing, Support and the **Kill Switch service**. `COMMITTEE_DEEP_DIVE` §C2 assigns **fourteen** contexts to three planes and none of BFF, Identity, Tenant, Notification, Billing, Support or Kill Switch. `COMPONENT_DIAGRAMS.md` and `SEQUENCE_DIAGRAMS.md` do not contain the word "plane" | `docs/CONTAINER_DIAGRAM.md:7` vs `:11-14`, `:36`, `:40`; `docs/COMMITTEE_DEEP_DIVE.md:163-166`; [Verified: grep of both diagram files] |
| **F-5** | **Nothing places a service in a plane.** `infra/` holds five namespaces, nine `NetworkPolicy` objects in five files, one dev/sim compose file, one Dockerfile and one IaC README. There is **no** Deployment, StatefulSet, Service, or IaC module, so no workload is assigned to a namespace anywhere in the repository | `find infra -type f` [Verified]; independently matches `docs/ADRs/ADR-007.md:45` |
| **F-6** | **The checker enforces seven invariants, six denials and one requirement.** Default-deny present; no analytics egress to execution/security/ipBlock; only execution holds an ipBlock; vault ingress only from control and execution; MCP egress to named analytics pods and the intent queue only; the additive **effective-union** rule for MCP pods; no `0.0.0.0/0`. The seventh is positive: **the run fails if the execution namespace has no broker egress** | `scripts/check_network_policies.py:4-13`, `:74-88`, `:89-97`, `:101-111`, `:112-123`, `:124-130`, `:131-135`, `:136-141` |
| **F-7** | **Two of the five namespaces have no default-deny and no policy that reaches them.** The checker's namespace loop names `analytics`, `control`, `execution` only; there is **no** policy file for `edge`, and `security` carries only a vault-pod ingress rule. Under the additive semantics this repository assumes, a pod no policy selects is unrestricted | `scripts/check_network_policies.py:101`; `find infra/kubernetes/network-policies -type f` [Verified: five files, none for edge]; `infra/kubernetes/network-policies/security.yaml:4-12`; the semantics assumption is `docs/RAID_LOG.md:59` (O-42, "verified by reading only") |
| **F-8** | **The "only via the intent queue" rule is enforced on one side; on the other side it is a comment.** Analytics **egress** names the pod (`podSelector: {app: intent-queue}`) and the checker reads it. The Control-plane **ingress** rule that admits analytics on 8443 carries the comment "# intent-queue only" while its `podSelector` is `{}` — every pod in the namespace. The same shape appears on the Execution side: edge is admitted on 8444 under the comment "# read-only order/position queries" with `podSelector: {}`. **No checker invariant reads ingress in either namespace** | `infra/kubernetes/network-policies/analytics.yaml:19-22` and `mcp-servers.yaml:14-17` vs `control.yaml:13` + `:20-22`; `execution.yaml:13` + `:19-21`; `scripts/check_network_policies.py:112-141` |
| **F-9** | **In-process, ten declared routes are checked at two call sites.** `ALLOWED_ROUTES` declares ten (source, destination) pairs. `check_caller` is called by product code in exactly two places: the intent queue and `ExecutionGateway.submit`. `cancel_command` is declared as a channel and is passed to a guard **nowhere**; `ExecutionGateway.cancel` and `cancel_all` carry no plane check — the finding IVA-10 recorded on 2026-09-07 and still true at this commit. **IVA-10 has no row in `docs/RAID_LOG.md`** | `libs/core/rtcore/planes.py:31-42`; `services/oms/oms/intent_queue.py:47`; `services/execution/execution_gateway/gateway.py:286` vs `:588`, `:641`; `docs/GATE_REPORTS/GATE_B_2026-09-07.md:104`; [Verified: grep "IVA-10" docs/RAID_LOG.md → no match] |
| **F-10** | **The in-process guard's source plane is self-declared.** `enter(Plane.CONTROL)` is callable by any in-process caller, which the Gate B report already records as IVA-11: "the in-process guard is a convention". Its one hard property is the fail-closed default: an unattributed caller is treated as Analytics | `libs/core/rtcore/planes.py:73-79` (default at `:77-78`), `:89-95`; `docs/GATE_REPORTS/GATE_B_2026-09-07.md:51`, `:70`, `:96` |
| **F-11** | **The strongest thing standing between the Analytics plane and execution today is not a route rule; it is an import scan.** TC-AI-005 parses every module of `mcp_servers` and fails if it imports `execution_gateway`, `broker_adapters`, `killswitch_service`, `identity_service`, `risk_engine.policy`, `rtcore.signing`, `subprocess`, `socket`, `requests`, `httpx` or `urllib` | `test/quartets/test_tc_ai_mcp.py:131-159` |
| **F-12** | **No cluster has ever applied these manifests.** The Gate B report states it in its own evidence column, and the Kubernetes semantics the effective-union rule depends on are verified by reading only | `docs/GATE_REPORTS/GATE_B_2026-09-07.md:51`; `docs/RAID_LOG.md:59` [Open: O-42, H-05] |
| **F-13** | **The four tests ADR-001 names are not traced.** The RTM contains **one** row citing a TC-NET id — FR-07, citing **TC-NET-003** alone. TC-NET-001, TC-NET-002 and TC-NET-004 appear in no RTM row, although all four mark themselves `req("NFR-SEC-01")` | `docs/REQUIREMENTS_TRACEABILITY.md:17`; `test/quartets/test_tc_net_planes.py:17,28,43,61`; [Verified: grep "TC-NET" docs/REQUIREMENTS_TRACEABILITY.md → one hit] |
| **F-14** | **One requirement id carries two different requirements.** `docs/NFR.md:20` NFR-SEC-01 is the **plane** requirement ("No network route analytics → execution; no secrets in agent context"), target column "Enforced by policy, tested". The RTM's only NFR-SEC-01 row is the **asymmetric-signing** row and names ADR-019, ADR-009, TC-SIG and TC-ARC — not ADR-001 and not TC-NET | `docs/NFR.md:20` vs `docs/REQUIREMENTS_TRACEABILITY.md:31` |
| **F-15** | **The blast-radius sentence is contradicted by two other ADRs.** ADR-013 records, in its own alternatives table, that "Execution-plane classes (gateway, simulated broker) still load in the analytics process (ADR-001 tension)", and the MCP Security Agent asked for a threat-model delta "for ADR-008 vs ADR-001: document why execution-plane code in the analytics process is acceptable, or move the backtest runner". **That delta does not exist**: `docs/THREAT_MODEL.md` contains no row mentioning ADR-008 or the backtest runner | `docs/ADRs/ADR-013.md:9,:22`; `docs/ADRs/ADR-008.md:10`; `docs/SESSIONS/REVIEW_C3_mcp_security_agent.md:59`; [Verified: grep "ADR-008\|backtest" docs/THREAT_MODEL.md → no match] |
| **F-16** | **ADR-001's own open-item pointer is broken.** `docs/ADRs/ADR-001.md:4` says "[Open: O-169 proposed]". O-169 in the register is an unrelated **closed** trust-anchor issue. The row that actually carries this work is **O-177**. **Sixteen ADR files carry the same broken pointer** | `docs/ADRs/ADR-001.md:4` vs `docs/RAID_LOG.md:230`; the real row at `docs/RAID_LOG.md:238`; [Verified: `grep -l "O-169 proposed" docs/ADRs/*.md \| wc -l` → 16] |
| **F-17** | **The same defect class was found in this tree three days ago by a different line, and it was blocking.** The Red-Team & Pen-Test Lead found that v1.1 of the threat model "named an egress allowlist as a delivered control while `EgressPolicy.check()` was consulted by no product code", and the row was rewritten against what the tree does. That is exactly the shape of F-9 | `docs/THREAT_MODEL.md:33` (uncommitted v1.2 edit present in the working tree at read time; see §3.3) |
| **F-18** | **Fifteen of the twenty ADR files read `Status: Proposed`**; five cite a decision (ADR-009, 017, 018, 019, 020) | [Verified: status line of each `docs/ADRs/ADR-0*.md`] |

### 3.3 Checks run in this worktree, verbatim [Verified]

```
$ git rev-parse --short HEAD
442cebd

$ git status --short          # at the start of the session
 M docs/DATA_FLOWS.md
 M docs/DR_PLAN.md
 M docs/THREAT_MODEL.md

$ git status --short          # at the end of the session (the edits above were committed by their owners while this pack was written)
?? docs/SESSIONS/COUNCIL_2026-09-09_O-170_O-172_mcp_security_agent.md
?? docs/SESSIONS/COUNCIL_2026-09-09_arb_adr_001.md

$ git rev-parse --short HEAD  # at the end of the session
42f19c6

$ git diff --name-only 442cebd..HEAD
docs/CAPACITY_MODEL.md docs/DATA_FLOWS.md docs/DR_PLAN.md docs/SECURITY_PLAN.md docs/THREAT_MODEL.md

$ python scripts/check_network_policies.py
OK: network policies satisfy plane invariants (TC-NET)
exit=0

$ python -m pytest test -k "net" -p no:warnings
5 passed, 246 deselected in 1.31s
   (test/quartets/test_tc_net_planes.py: 4 — TC-NET-001..004;
    test/quartets/test_tc_ai_egress_trust.py: 1 — matched on the name, not a plane test)

$ python -m pytest test -p no:warnings
251 passed in 21.07s
```

**Two notes on that output, because both matter [Committee].**

1. **The tree moved under this session, and none of it touches this ADR.** Reads were made at `442cebd`; while the pack was written, other owners committed the DR plan, data flows, capacity model, security plan and threat model (the C-007-4 and Red-Team follow-ups) as `a233274` and `42f19c6`. **I did not write them and did not touch them.** `git diff --name-only 442cebd..HEAD` names those five documents and nothing else: `docs/ADRs/ADR-001.md`, `infra/`, `libs/core/rtcore/planes.py`, `scripts/check_network_policies.py`, `test/`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/NFR.md`, `docs/CONTAINER_DIAGRAM.md`, `docs/RAID_LOG.md` and `docs/DECISION_LOG.md` are **unchanged** [Verified]. F-17 is quoted from `docs/THREAT_MODEL.md` v1.2, which was uncommitted when read and is committed now; the B3/B4 boundary line it also cites sits at `:12` of the committed v1.1 and at `:14` of v1.2.
2. **What the green results evidence, and what they do not.** They evidence that the manifests satisfy seven static invariants and that the in-process guard denies the crossings the tests ask it about. **They evidence nothing about a running network.** The manifests have never been applied (F-12); the guard is consulted at two call sites (F-9); the source plane is self-declared (F-10). A Gate B pack can be assembled entirely from these green checks and still contain no evidence that any route is denied anywhere.

---

## 4. Council discussion

Positions drafted in role by the Enterprise Architect and anchored to the tree, per §0. **No seat has confirmed its wording.**

### 4.1 Round one — decide as proposed, amend, or replace?

| Seat | Line | Position drafted for it | Anchor in the tree |
|---|---|---|---|
| **enterprise-architect** (owner) | 1st | "**Amend.** The invariant is right and is the most load-bearing sentence in the repository: *analytics has no route to execution or a broker; analytics reaches control only at the intent queue*. What is wrong is everything around it. The title names three planes and the tree has five namespaces and six plane identities; the Decision assigns twenty contexts to planes that no artefact lists; and the Consequences claims a blast-radius property that ADR-010 and ADR-013 contradict. Same shape as ADR-007: an invariant welded to a claim about a deployment that does not exist" | F-1, F-3, F-4, F-15 |
| **security-architect** | 2nd | "**Amend, and the amendment is mine to review, not to write.** My finding is F-8: the rule 'analytics may reach only the intent queue' is expressed by a selector on the egress side and by a **comment** on the ingress side, and the checker reads neither ingress rule. A comment is not a control. Second finding, F-7: two of five namespaces have no default-deny, one of them the **edge** namespace that terminates human sessions and, in the code's own route table, may reach control, analytics **and** execution" | F-7, F-8; `planes.py:38-40` |
| **cloud-architect** (owner of `infra/`, CODEOWNER of the policies) | 1st | "**Amend, with the ADR-007 sentence repeated in ADR-001's own Decision text.** I will not support a decision that reads as though a boundary is enforced. **No cluster has ever applied these files.** What is enforced today is a YAML linter with seven rules and one placeholder CIDR from the RFC 5737 documentation range. Decide the constraint; do not let the record say the constraint runs" | F-12; `execution.yaml:31-33` |
| **integration-architect** | 1st | "**Amend, and close the route list the way ADR-007 item 4 was closed.** `ALLOWED_ROUTES` is a ten-entry table in a library, consulted at two call sites. Either it is the normative route set — in which case it belongs in the ADR and a test must fail when the two diverge — or it is documentation with a `.py` extension" | F-9 |
| **sre-lead** | 2nd | "**Amend.** And record that deciding this measures nothing: 'extra latency at plane boundaries' is a performance claim with no baseline anywhere in this repository" | `ADR-001.md:16`; [Open: O-03] |
| **mcp-security-agent** | 2nd | "**Amend.** The honest strongest control on the analytics side is not a route rule: it is the import scan, which makes the capability structurally absent rather than merely denied. Say so, and stop citing the network policy as the thing that stops an MCP server reaching a broker in dev/sim — no network is involved; one process is" | F-11, F-15 |
| **data-architect** | 1st | "**Amend.** The five namespaces are the unit ADR-007 now says a deployment cell contains. If ADR-001 keeps saying three, the two ADRs disagree about the same object" | `docs/ADRs/ADR-007.md:24` vs `ADR-001.md:1,:10` |
| **counsel-platform-reliability** | advisory | "**Amend.** A one-sentence Decision and a one-line Consequences under NFR-SEC-01, every network policy, the CI policy gate and four tests. The reason it survived is the reason ADR-007 survived: it is too short to disagree with" | F-1 |

**Summary [Committee].** Eight seats drafted, eight say *amend*. **None argues to decide as proposed. None argues to replace.** The reasons converge on one structural defect, which is the same one D-069 named in ADR-007: **ADR-001 welds a route invariant that costs nothing to decide to a set of claims about a deployment that does not exist and a grouping that is written nowhere.**

### 4.2 Round two — is the route set right, and is it closed?

| What the tree has | What ADR-001 says about it | Finding |
|---|---|---|
| **Ten inter-plane routes** declared in `planes.py:31-42`, including EDGE→CONTROL (api **and intent_queue**), EDGE→EXECUTION (api_read), CONTROL→ANALYTICS (revocation, events), CONTROL→VAULT and EXECUTION→VAULT | It names three of them (analytics→control via the queue; the denial of analytics→execution and analytics→broker) | **The closed list is not closed.** Seven permitted routes exist that the ADR never states, including a route into the Execution plane from a plane the ADR does not name |
| **Five namespaces**, two of them (`edge`, `security`) with no default-deny | "Three planes" | **The ADR's own title excludes the two namespaces with the weakest policy.** What an ADR does not name, no reviewer checks (F-7) |
| **Vault ingress restricted to control and execution**, enforced by the checker | nothing | The checker enforces an invariant the ADR never states. That is the right invariant and the wrong provenance: a rule with no ADR can be relaxed by anyone who edits the script |
| **`0.0.0.0/0` refused; one ipBlock per certified adapter; execution *must* declare a broker route** | "deny any network route from Analytics to Execution **or brokers**" | The positive requirement (execution must have a broker egress) has no ADR behind it, and the CIDR present is an RFC 5737 documentation placeholder. Nothing here evidences a broker capability [Open: H-07] |
| **The Kill Switch service** halts risk, OMS and the AI plane; it sits in **no** plane in either artefact that draws it | nothing | The one component that supersedes everything [Source: 00; CLAUDE.md] has no plane, so no route rule covers it |

**The council's answer to sub-question 2 [Committee]: the route set is right in what it denies and incomplete in what it permits.** The remedy is the one ADR-007 used: make the permitted set **explicit, closed and directional**, put it in the Decision, and require a new ADR and both boards to add a row.

### 4.3 Round three — invariant versus aspiration, stated plainly

This is the answer to sub-question 1 and the heart of the packet.

**Load-bearing today — the code and the tests really do this:**

| Enforced | By what | Evidence |
|---|---|---|
| The nine manifests satisfy seven static invariants, and a policy edit that opens analytics→execution fails the check and passes again when reverted | `scripts/check_network_policies.py`, run by `make policy-check` and by CI | TC-NET-003, TC-NET-004; `Makefile:29`; `.github/workflows/ci.yml:23` |
| An in-process caller attributed to Analytics, **or unattributed**, cannot call `ExecutionGateway.submit`; the denial is recorded and raises an S1 `plane.deny` | `PlaneGuard.check_caller` at `gateway.py:286`, fail-closed default at `planes.py:77-78` | TC-NET-002 |
| An in-process caller reaching the intent queue is checked against the same table | `intent_queue.py:47` | TC-NET-001 |
| `mcp_servers` **cannot import** execution, broker, vault, kill-switch, identity, policy-mutation, signing or network modules | AST scan | TC-AI-005 |
| MCP pods are excluded from the broad analytics egress rule, and the additive union of policies matching an MCP pod is checked | `analytics.yaml:16`; `check_network_policies.py:74-88` | TC-NET-003; threat row T-20 |

**Aspiration — asserted by the text and checked by nothing:**

| Asserted | Checked by | Why it is aspiration |
|---|---|---|
| "Group the 20 bounded contexts into Analytics, Control and Execution planes" | nothing | No artefact lists the grouping in full (F-4) and no workload manifest exists to place a service in a namespace (F-5) |
| "deny any network route" — as a property of a **running** system | nothing | No cluster has applied a manifest (F-12); the semantics relied on are read-verified only (O-42) |
| "Analytics reaches Control only via the trade-intent queue" — on the **receiving** side | nothing | The control-plane ingress restriction is a comment (F-8) |
| "no analytics→execution route" — for the **whole** Execution surface in-process | nothing | `cancel` and `cancel_all` have no plane check (F-9, IVA-10) |
| The in-process guard as a **boundary** | nothing | The source plane is self-declared (F-10, IVA-11). It is a defect detector: it catches a component wired wrongly, not an adversary |
| "injection blast radius confined to Analytics" | nothing, and it is contradicted | Every plane runs in one process in dev/sim (ADR-010), and execution-plane classes load in the analytics process (ADR-013:22). The threat-model delta asked for in REVIEW_C3 does not exist (F-15) |
| "Extra latency at plane boundaries" | nothing | No latency baseline exists anywhere in this repository [Open: O-03] |
| NFR-SEC-01 "Enforced by policy, tested" | nothing | The policy engine has never run (F-12, F-14) |

### 4.4 Round four — NFR-SEC-01 and the RTM (sub-question 4)

**The finding, precisely.** `docs/NFR.md:20` NFR-SEC-01 is the plane requirement. `docs/REQUIREMENTS_TRACEABILITY.md:31`, the RTM's **only** NFR-SEC-01 row, is the asymmetric-signing requirement. The four plane tests mark themselves `req("NFR-SEC-01")` and land, in the RTM, on a row about signing keys; three of the four appear in no RTM row at all (F-13). CLAUDE.md requires an RTM row per story; the control that Gate B cites most often has one, and it describes a different control.

**Position drafted for the seats:** amend the **requirement**, not the architecture — the ADR-007 precedent for NFR-SCL-01 (D-069). Split NFR-SEC-01 into **NFR-SEC-01a** (plane route topology; TC-NET-001..004, TC-AI-005, the checker) and **NFR-SEC-01b** (asymmetric signing; the existing RTM row 31 content), so that a requirement id stops carrying two requirements and the target column stops claiming an enforcement that has never run. Owner of `docs/NFR.md`: Enterprise Architect. Reviewer: SRE Lead (named in the file header) with the Security Architect on the security half. RTM re-keying: Program Orchestrator. Exact text at §9.

### 4.5 Round five — is ADR-001 already decided? (O-180)

D-004 says "ADR-001..008 proposed to ARB"; D-042 ratifies D-001..D-004 (F-2). Two readings are possible and O-180 asks the IVA which is right [Source: docs/RAID_LOG.md:241].

**The position drafted for the council, and it does not depend on which reading wins [Committee]:** even on the wider reading, **D-004 cannot serve as the decision record for a control-bearing ADR.** It records no scope, no conditions, no alternatives, no reviewer and no environment; it does not say what was decided; and D-042's own text describes the object as "proposed". A status line written from D-004 would say "Accepted" while the ledger it cites says "proposed" — the precise ADR-017 ambiguity that the reconciliation was run to remove [Source: docs/SESSIONS/REVIEW_2026-09-08_adr_007_and_status.md:30-39]. **Either way, a fresh decision entry is needed.** The IVA's answer to O-180 changes how eight other ADR rows are worded; it does not change this one.

---

## 5. What this pack rejects

| Option | Why rejected [Committee] |
|---|---|
| **DECIDE AS PROPOSED** | Six defects survive it, none of which needs a cluster to be true: the title and Decision name three planes where the tree has five namespaces and six identities (F-3); the twenty-context grouping exists in no artefact (F-4); the permitted route set is seven routes larger than the ADR states (§4.2); the receiving-side restriction is a comment (F-8); the Consequences asserts a blast-radius property two other ADRs contradict (F-15); the ADR's own register pointer is broken (F-16) |
| **REPLACE ADR-001** | The invariant is sound and is correctly relied on by the checker, four tests, the CI policy gate, ADR-007, ADR-013 and the threat model's B3/B4 boundaries. Replacement would orphan those references and suggest the denial was withdrawn. Nothing found here contradicts *analytics has no route to execution or a broker* |
| **DO NOT DECIDE YET** | Held as the **fallback**: if the amended text of §7 is declined, this pack's position reverts to DO NOT DECIDE YET and Gate B is not convened on it, because the foundation is then still a proposal. "Decide it as it stands so the gate can proceed" is not available: it would be recording a control as decided while its own text overstates it |
| **Defer to Gate C, when a cluster exists** | Rejected: the constraint is decidable today and four tests, nine manifests, one CI gate and two other ADRs already depend on it. Deferring leaves the Gate B pack resting on a proposal for a further gate — the defect O-159 named and D-069 acted on |
| **Assert the status line** (set `Accepted` on the strength of D-004/D-042) | Rejected without discussion. **The ledgers stay the truth** [Source: CLAUDE.md; ADR-017]. See §4.5 |
| **Widen the ADR to cover the two unpoliced namespaces by relaxing the checker** | Rejected: the remedy for an unpoliced namespace is a policy, not a smaller invariant. Any change in the other direction is the Security Architect's residual risk to accept, and never mine [Source: 13] |

---

## 6. RECOMMENDATION — **DECIDE WITH AMENDMENTS**

**The pack recommends (advisory; the Product Owner or the delegate decides under D-039/D-040) that ADR-001 be decided *as amended by §7*, and not as it stands.**

The recommendation is: **decide the route set, and say what runs.**

- The **invariant** — five plane namespaces, an explicit closed directional route set, analytics reaching control only at the intent queue, only execution holding a broker route, default-deny everywhere — costs no evidence to decide. It is a constraint on future work, and it is what the checker, four tests, the CI gate, ADR-007 and ADR-013 already assume.
- The **claims about enforcement** — that the topology is enforced by network policy, that the in-process guard is a boundary, that blast radius is confined, that plane boundaries cost latency — **cannot** be decided, because nothing in this repository evidences any of them. The amendment states, in the Decision text and not a footnote, that no cluster has ever applied these manifests and that in-process the guard is a defect detector.

**Confidence.** **High** that F-1..F-18 are established by reading and by the commands in §3.3, and that the invariant is sound and correctly relied upon. **High** that ADR-001 is undecided. **Medium-high** on the closed route table of §7 item 2 being complete — it is transcribed from `planes.py` and the manifests, and neither has ever met a second implementation. **Medium** on the Kubernetes semantics behind F-7 and F-8, which rest on O-42, an assumption verified by reading only. **None** on any latency, capacity, cost, provider, broker or venue figure: none is stated and none may be derived from this packet.

---

## 7. Amended text of ADR-001, for the Enterprise Architect to apply without interpretation

Quoted here and **deliberately not written into `docs/ADRs/ADR-001.md` in this pass**, so that no reader of the ADR can mistake a proposal for a decision [Source: 13].

> # ADR-001 — Plane topology and the closed inter-plane route set
>
> **Status:** *(filled by the delegate from the Product Owner's decision record, quoting the decision id; `Proposed` until that entry exists)* · **Date:** 2026-09-07, amended 2026-09-09 · **Deciders:** ARB with the Security & Privacy Board (advisory, D-039/D-040); the Product Owner decides · **Consulted:** Enterprise Architect, Security Architect, Cloud Architect, Integration Architect, Data Architect, SRE Lead, MCP Security Agent, counsel-platform-reliability · **Provenance:** [Committee, derived from 00, 03, 04] / [Committee: ARB packet `docs/SESSIONS/COUNCIL_2026-09-09_arb_adr_001.md`; ADR-007, ADR-010, ADR-013, ADR-019] / [Open: O-177 status, O-180 D-042 reading, O-42 CNI semantics, H-05 no cluster, IVA-10, IVA-11]
>
> **This ADR is undecided.** No entry of `docs/DECISION_LOG.md` accepts it. The Status field is filled by the delegate **from the Product Owner's decision record**, quoting the decision id, and only after that entry exists. D-004 records this ADR as *proposed* and D-042 ratifies D-004; whether that ratification reaches the ADRs is [Open: O-180], and in either reading D-004 records no scope, conditions or alternatives and cannot serve as the decision record for a control-bearing ADR. The reconciliation this line belongs to is `docs/SESSIONS/REVIEW_2026-09-08_adr_007_and_status.md` §4 [Open: O-177].
>
> Author of the amendment: Enterprise Architect · Reviewers (different lines): Security Architect (invariant), Cloud Architect (manifests) — both CODEOWNERS of `infra/kubernetes/network-policies/` · Recommending bodies: ARB and the Security & Privacy Board (advisory) · Approver: the Product Owner (D-039).
>
> ## Context
>
> Blueprint 00 permits only the deterministic Execution Gateway to submit real orders, and requires AI/MCP components to hold no broker route, no secret, no limit write path, no audit delete path and no way to change mode. This ADR is the technical form of the first of those rules: **the pipeline is enforced by topology, not by convention.**
>
> Three clarifications of scope, because each has already caused a document to overstate itself:
>
> - **"Three planes" names the pipeline, not the deployment.** The pipeline is Analytics → Control → Execution → broker. The deployed unit is **five plane namespaces** — `analytics`, `control`, `execution`, `security` (vault/KMS) and `edge` (BFF and human sessions) — and the code models **six plane identities**, adding `broker` as an external destination and `vault` as the security-plane service. Documents that say "three planes" are naming the pipeline; this ADR governs all five namespaces.
> - **What is enforced today is a static check and two in-process seams, not a network.** `scripts/check_network_policies.py` checks nine manifest objects against seven invariants in CI; `rtcore.planes.PlaneGuard` is consulted at two call sites; `mcp_servers` cannot import execution, broker, vault, kill-switch, identity, signing or network modules (TC-AI-005). **No cluster has ever applied these manifests** [Open: H-05], and the additive semantics the effective-union rule depends on are verified by reading only [Open: O-42].
> - **This ADR does not confine blast radius in dev/sim, and must not be cited as doing so.** Every plane runs in one process (ADR-010) and execution-plane classes load in the analytics process to keep the single backtest code path (ADR-008, ADR-013). The threat-model delta that would justify that arrangement is owed and does not exist [Open: REVIEW_C3 item 4].
>
> ## Decision
>
> 1. **Planes.** Five plane namespaces exist — `analytics`, `control`, `execution`, `security`, `edge` — labelled `plane: <name>`, and the code's `Plane` enum is the authoritative list of plane identities. Every deployed workload belongs to exactly one plane namespace. The bounded contexts of blueprint 03 are grouped into planes in **one place only**, `docs/CONTAINER_DIAGRAM.md`, which must list every context including those currently drawn in no plane (Notification, Billing, Support, **Kill Switch service**) and the Edge contexts (BFF, Identity, Tenant). Until a workload manifest exists, plane membership is a documentary claim and no test checks it [Open: H-05].
>
> 2. **The inter-plane route set is closed, explicit and directional.** Exactly the following may cross a plane boundary; **anything absent is denied**. This table and `rtcore.planes.ALLOWED_ROUTES` state the same thing and must not diverge.
>
>    | Source | Destination | Channel(s) permitted |
>    |---|---|---|
>    | Analytics | Control | `intent_queue` — the trade-intent queue pod only |
>    | Control | Execution | `order_command`, `cancel_command` |
>    | Control | Analytics | `revocation`, `events` |
>    | Control | Vault (security) | `signing_keys` |
>    | Execution | Broker | `broker_adapter` |
>    | Execution | Control | `events` |
>    | Execution | Vault (security) | `broker_credentials` |
>    | Edge | Control | `api`, `intent_queue` |
>    | Edge | Analytics | `api` |
>    | Edge | Execution | `api_read` — read-only order and position queries |
>
>    **Denied and never added by an operational argument:** Analytics → Execution, Analytics → Broker, Analytics → Vault, Analytics → Edge, Execution → Analytics, Broker → anything. **Adding a row to this table requires a new ADR, this board and the Security & Privacy Board**; no latency, capacity, cost, convenience or delivery-date argument may add one.
>
> 3. **Every permitted route is restricted on both sides, by a selector and never by a comment.** A rule that admits a plane "to the intent queue only" or "for read-only queries only" states that restriction in its `podSelector`, and the invariant checker reads ingress as well as egress. A restriction that exists only in a YAML comment is not a control.
>
> 4. **Every plane namespace carries a default-deny policy for Ingress and Egress**, including `edge` and `security`. Today `edge` has no policy file and `security` has only a vault-pod ingress rule; that is a defect against this item, not an exception to it [Open].
>
> 5. **Only the Execution plane may hold a route to a broker.** The route is an explicit CIDR per certified adapter, filled from the broker certification record at deployment; `0.0.0.0/0` and `::/0` are refused. The CIDR presently in the repository is an RFC 5737 documentation range used as a sim placeholder and **asserts no broker capability, endpoint or entitlement** [Open: H-07].
>
> 6. **Vault ingress is restricted to the Control and Execution planes.** Analytics and Edge never reach the vault. This invariant is already enforced by the checker and is stated here because a rule enforced by a script and by no decision can be relaxed by whoever edits the script.
>
> 7. **In-process, the plane guard is a defect detector and not a security boundary, and this ADR is never cited as evidence that an in-process caller cannot reach the Execution plane.** The guard's source plane is self-declared: any in-process caller may enter any plane (IVA-11). Its hard properties are two: an unattributed caller is treated as Analytics and refused (fail closed), and every denial is recorded and raises an S1 `plane.deny`. It is consulted at two call sites — the intent queue and `ExecutionGateway.submit`; `cancel` and `cancel_all` are unguarded (IVA-10) and that is a defect owed a fix or an accepted, recorded residual risk from the Security Architect — never from this board and never from the author of this ADR.
>
> 8. **What this ADR does not decide, and does not deliver. No cluster has ever applied these manifests; there is no network on which any of these rules has ever run; nothing here authorises an environment or advances the environment ladder** [Source: 00]. It states no latency, throughput, capacity or cost figure, and none may be derived from it. It delivers no resource isolation between planes (that is delivered by nothing today [Open: O-160]) and no tenant isolation (delivered in software and tested, D-059).
>
> ## Alternatives considered
>
> | Alternative | Why not |
> |---|---|
> | (a) **Convention-only separation** (original alternative) | Rejected: not testable, drifts. Retained as rejected |
> | (b) **Single plane with RBAC** (original alternative) | Rejected: an injected agent could reach execution APIs. Retained as rejected |
> | (c) **Three planes with network policy** (the original decision text) | Retained as the *route* decision and rejected as the *statement*: it names three of the ten permitted routes, excludes the two namespaces with the weakest policy, and asserts an enforcement that has never run |
> | (d) **Five plane namespaces with a closed, directional route set, both-sided selectors and default-deny everywhere** (chosen) | Chosen: it is what the code and the manifests already model; it closes the permitted set the way ADR-007 item 4 closed the cross-cell list; and it separates the decidable constraint from the undeliverable claim |
> | (e) **Defer until a cluster exists** | Rejected: nine manifests, four tests, one CI gate, ADR-007 and ADR-013 already depend on this ADR. Deferring leaves them resting on a proposal for a further gate (O-177) |
> | (f) **Retire the in-process guard and rely on the manifests** | Rejected: the manifests run nowhere and the guard is the only part of this ADR that executes. Item 7 states what it is worth instead of retiring it |
>
> ## Consequences
>
> - **Two invariants that the checker enforces today have no ADR behind them** until this amendment lands: vault ingress restriction and the refusal of `0.0.0.0/0`. Both are now decisions of record.
> - **Two namespaces are in breach of item 4 on the day this is decided.** `edge` has no policy and `security` has no default-deny. The remedy is a manifest change owned by the Cloud Architect and the Security Architect (CODEOWNERS), and the checker gains the corresponding invariants; until then the breach is visible in the Gate B pack, not hidden by it [Open].
> - **Two ingress rules assert in comments what they do not express in selectors** (control from analytics; execution from edge). Same owners, same treatment.
> - **The in-process guard covers two of the three Execution-plane entry points.** `cancel` and `cancel_all` are owed a fix or a recorded acceptance (IVA-10).
> - **The blast-radius claim of the previous text is withdrawn**, and the ADR-008/ADR-001 threat-model delta stays owed [Open: REVIEW_C3 item 4].
> - **No latency claim is made.** The previous "extra latency at plane boundaries" is unmeasured and no baseline exists [Open: O-03].
> - **This ADR creates no infrastructure.** `infra/` holds five namespaces, nine network policies, one dev/sim compose file and no workload object of any kind.
>
> ## Controls and tests affected
>
> | Control | Test | State |
> |---|---|---|
> | Manifest route invariants (seven) | TC-NET-003, TC-NET-004; `scripts/check_network_policies.py`; `make policy-check`; CI | exists and passes; **static file check only — no cluster** [Open: H-05, O-42] |
> | Analytics → Control at the intent queue, in-process | TC-NET-001 | dev/sim, one process |
> | Analytics → Execution denied, unattributed callers denied, S1 alert raised | TC-NET-002 | dev/sim; `submit` only — `cancel`/`cancel_all` unguarded [Open: IVA-10] |
> | MCP cannot import execution, broker, vault, kill-switch, identity, signing or network modules | TC-AI-005 | passes; the strongest analytics-side control in dev/sim |
> | Default-deny in `edge` and `security`; both-sided ingress selectors | **no test exists and no invariant checks it** | owed [Open] |
> | Route table in this ADR versus `rtcore.planes.ALLOWED_ROUTES` | **no test exists** | proposed TC-NET-005 [Open] |
> | Plane membership of a deployed workload | **no test can exist until a workload manifest exists** | [Open: H-05] |
>
> ## NFRs and register items this ADR is the foundation for
>
> NFR-SEC-01a (plane route topology, as amended), NFR-AVL-01 (planes never shed), NFR-TEN-01 (route half only). Threat-model boundaries B3, B4, B5, B6; rows T-02, T-20, T-28. Register: O-177, O-180, O-42, H-05, IVA-10, IVA-11, O-03, O-160.
>
> Conditions attached by the ARB and the Security & Privacy Board to any decision on this ADR: C-001-1..C-001-10 of `docs/SESSIONS/COUNCIL_2026-09-09_arb_adr_001.md` §8.

---

## 8. Conditions attached to any decision

If the Product Owner (or the delegate under D-040) decides ADR-001 as amended, the recommendation is conditional on all ten. **None of these is an approval; each is a condition on a decision only the Product Owner can make** [Source: 13].

| # | Condition | Owner | Closes / opens |
|---|---|---|---|
| **C-001-1** | The sentence "**No cluster has ever applied these manifests; there is no network on which any of these rules has ever run**" appears in the **Decision** section (item 8), not in a footnote or a consequence — the analogue of C-007-2, and the Cloud Architect's stated condition for supporting a decision at all | Enterprise Architect | O-177; keeps H-05, O-42 visible |
| **C-001-2** | The route set is the **closed, directional ten-row table** of item 2. A row is added only by a new ADR, the ARB **and** the Security & Privacy Board; no latency, capacity, cost, convenience or delivery-date argument may add one | Enterprise Architect; enforced at review by the Integration Architect | O-177 |
| **C-001-3** | **The ADR's table and `rtcore.planes.ALLOWED_ROUTES` are proved identical by a test that fails on divergence** (proposed **TC-NET-005**, quartet: positive = tables agree; negative = a row removed from the ADR fails; abuse = a row added to the code fails; recovery = restoring the row passes). Written by the Backend Lead, reviewed by the Security Architect. **This pack does not write tests** | Backend Lead; Security Architect; QA Lead | new register row proposed (§10) |
| **C-001-4** | **Both-sided selectors.** The control-plane ingress rule that admits Analytics, and the execution-plane ingress rule that admits Edge, name the pods they claim to admit; `scripts/check_network_policies.py` gains ingress invariants for both. Protected path — needs the 2nd-line CODEOWNER | Cloud Architect (owner of `infra/`), Security Architect (CODEOWNER) | F-8; new register row proposed |
| **C-001-5** | **Default-deny in all five plane namespaces**, including `edge` and `security`, with the checker's namespace loop extended to match. If either is instead accepted as a residual risk, the **Security Architect** records that acceptance — not the ARB, not the Enterprise Architect, not this pack | Cloud Architect; Security Architect | F-7; new register row proposed |
| **C-001-6** | **IVA-10 gets a register row and a disposition before Gate B** — `ExecutionGateway.cancel` and `cancel_all` carry no plane check. Either the check is added, or the residual risk is accepted and recorded by the Security Architect with the fencing-token mitigation stated | Backend Lead; Security Architect; Program Orchestrator (register) | IVA-10 (unregistered today, F-9) |
| **C-001-7** | **NFR-SEC-01 is split in the same working session as the ADR** (text at §9), because a decided ADR-001 and an NFR-SEC-01 whose target column reads "Enforced by policy, tested" contradict each other inside one evidence pack. The RTM is re-keyed at the same time and TC-NET-001, -002 and -004 acquire rows | Enterprise Architect (`docs/NFR.md`); Program Orchestrator (RTM); SRE Lead and Security Architect review | O-163 precedent (C-007-7); F-13, F-14 |
| **C-001-8** | **The blast-radius claim is withdrawn and the owed threat-model delta is named.** ADR-001 is not cited as confining injection blast radius while ADR-010 and ADR-013 hold; the ADR-008-vs-ADR-001 delta asked for in REVIEW_C3 is written by the Security Architect or the request is closed with a stated reason | Security Architect (owner of `docs/THREAT_MODEL.md`); Enterprise Architect | F-15; REVIEW_C3 item 4 |
| **C-001-9** | **The broken register pointer is repaired in all sixteen ADR files**: `[Open: O-169 proposed]` → `[Open: O-177]`. It is a documentary edit and it is the Enterprise Architect's | Enterprise Architect | F-16 |
| **C-001-10** | **Author ≠ reviewer ≠ approver.** The Enterprise Architect applies §7 and §9; the Security Architect reviews the invariant and the Cloud Architect the manifest conditions (both CODEOWNERS); the ARB and the Security & Privacy Board recommend; the **Product Owner or the delegate decides**. The author's declared interest (§1) is recorded in the decision row. The author approves nothing and writes no ledger row | Enterprise Architect; Security Architect; Cloud Architect; delegate | D-039, D-040 |

### 8.1 Control quartet for the critical control (plane route denial)

| Quartet cell | Test that exists | State |
|---|---|---|
| **positive** — Analytics reaches Control through the intent queue and the pipeline proceeds | TC-NET-001 | exists, passes (dev/sim, one process) |
| **negative** — Analytics, and an unattributed caller, are refused at `ExecutionGateway.submit`, with an S1 `plane.deny` and a recorded deny | TC-NET-002 | exists, passes; **covers `submit` only** [Open: IVA-10] |
| **abuse** — no route exists from Analytics to vault, broker or execution in the route table, and the manifests satisfy the invariants | TC-NET-003; TC-AI-005 (import scan) | exists, passes |
| **recovery** — a policy edit that opens Analytics→Execution fails the check, and restoring the file passes again; a denied crossing leaves no sticky state | TC-NET-004 | exists, passes |
| **missing quartets, named so they are not mistaken for gaps nobody noticed** | default-deny in `edge`/`security`; both-sided ingress selectors; ADR-table ↔ code-table agreement (TC-NET-005); plane membership of a deployed workload | **none of these has a test** [Open: C-001-3, C-001-4, C-001-5, H-05] |

---

## 9. Exact amended text for `docs/NFR.md`, for the Enterprise Architect to apply without interpretation (C-001-7)

**Owner: Enterprise Architect** (the file header names him owner, the SRE Lead reviewer, ARB the approving body). The security half is reviewed by the **Security Architect**. **No target, threshold or figure is added** [Committee] [Source: 13].

**9.1 Replace the single NFR-SEC-01 row with these two.** (Column order is the existing one: ID | Category | Requirement | Source | Target.)

> | NFR-SEC-01a | Security | **No route from the Analytics plane to the Execution plane, to a broker or to the vault; Analytics reaches Control only at the trade-intent queue; only the Execution plane holds a broker route** (ADR-001 as amended). The permitted inter-plane route set is the closed, directional table of ADR-001 item 2 and `rtcore.planes.ALLOWED_ROUTES`; anything absent is denied. **No secret is reachable from an agent context**: `mcp_servers` cannot import execution, broker, vault, kill-switch, identity, policy-mutation, signing or network modules | 04, 06 | **Static invariants over nine manifest objects (`scripts/check_network_policies.py`, CI) and in-process denial at two call sites — TC-NET-001..004, TC-AI-005. The manifests have never been applied to a cluster** [Open: H-05]; **the CNI's additive semantics are verified by reading only** [Open: O-42]; **in-process the guard is a defect detector, not a boundary — the caller's plane is self-declared** [Open: IVA-11]; `cancel`/`cancel_all` carry no plane check [Open: IVA-10]; `edge` and `security` carry no default-deny [Open: C-001-5] |
> | NFR-SEC-01b | Security | Asymmetric signing: `rtcore.trust` (verify-only Ed25519 and the public TrustSet) and `rtcore.signing` (signer only, banned from `mcp_servers`); `PublicKeyCommandVerifier` in the execution gateway; trust set in the tool-registry loader (ADR-019); engines free of the web framework (ADR-009) | 06 | TC-SIG-001..004, TC-ARC-001..004, TC-AI-005 — the existing RTM row 31 content, re-keyed so that one requirement id no longer carries two requirements |

**9.2 A note the Enterprise Architect should add under the NFR table** [Committee]:

> "Plane" in NFR-SEC-01a, NFR-AVL-01 and NFR-TEN-01 means one of the **five plane namespaces** of ADR-001 (`analytics`, `control`, `execution`, `security`, `edge`); the code models six plane identities, adding `broker` and `vault`. "Three planes", where it appears in this repository, names the **pipeline** Analytics → Control → Execution and not the deployed namespace set. No statement in this table asserts that a network policy is running: none is.

**9.3 RTM changes owed at the same time (Program Orchestrator, reviewer IVA)** [Committee]: re-key row 31 to **NFR-SEC-01b**; add a row for **NFR-SEC-01a** with architecture `rtcore.planes` + `infra/kubernetes/network-policies` + `scripts/check_network_policies.py`, owner Security Architect, control "closed route set, default-deny, no analytics→execution/broker/vault", tests **TC-NET-001..004, TC-AI-005**, evidence `docs/TEST_CASES/TC-NET.md`, gate **B**, status "dev/sim; manifests never applied [Open: H-05, O-42, IVA-10, IVA-11]"; keep the FR-07 row and correct its test list.

---

## 10. Documents that must change, in order, with owners

| # | Document | Change | Owner (writes) | Reviewer (different line) | Blocks Gate B? |
|---|---|---|---|---|---|
| 1 | **`docs/ADRs/ADR-001.md`** | Apply §7 verbatim. **Status stays `Proposed` until the decision entry exists** | Enterprise Architect | Security Architect; Cloud Architect | **Yes** |
| 2 | **`docs/DECISION_LOG.md`** | The first entry ADR-001 has ever had (proposed row below) | delegate, on the Product Owner's decision | Independent Validation Agent | **Yes** |
| 3 | **`docs/NFR.md`** | Apply §9.1–§9.2 (NFR-SEC-01 split; the plane note) | Enterprise Architect | SRE Lead; Security Architect | **Yes** (C-001-7) |
| 4 | **`docs/REQUIREMENTS_TRACEABILITY.md`** | Apply §9.3; TC-NET-001, -002, -004 acquire rows | Program Orchestrator | Independent Validation Agent | Yes — an RTM row per requirement is a house rule |
| 5 | **`infra/kubernetes/network-policies/`** | C-001-4 (both-sided selectors) and C-001-5 (default-deny in `edge` and `security`), or a recorded residual-risk acceptance by the Security Architect | Cloud Architect | Security Architect (CODEOWNER, protected path) | Yes |
| 6 | **`scripts/check_network_policies.py`** | Ingress invariants; namespace loop extended to five | Cloud Architect | Security Architect | Yes |
| 7 | **`test/quartets/`** | TC-NET-005 (ADR table ↔ code table) | Backend Lead | QA Lead; Security Architect | Yes (C-001-3) |
| 8 | **`docs/CONTAINER_DIAGRAM.md`** → v1.2 | The single place the twenty contexts are grouped into planes: every context named, including Notification, Billing, Support, the **Kill Switch service**, and the Edge contexts; the "three planes" line corrected to five namespaces / pipeline. Also clears the outstanding Cloud Architect review of v1.1 | Enterprise Architect | Cloud Architect | Yes |
| 9 | **`docs/COMPONENT_DIAGRAMS.md`, `docs/SEQUENCE_DIAGRAMS.md`** | State the plane of every component and of every participant; today neither file contains the word | Enterprise Architect | Backend Lead | Yes — they are cited as Gate B architecture evidence |
| 10 | **`docs/THREAT_MODEL.md`** | C-001-8: the ADR-008-vs-ADR-001 delta, plus rows for the two unpoliced namespaces and the comment-only ingress restrictions (proposed text below) | Security Architect | Red-Team & Pen-Test Lead | Yes |
| 11 | **The other fifteen `Proposed` ADRs** | C-001-9 pointer repair in all sixteen files; the remaining status questions stay owed to their councils (`REVIEW_2026-09-08_adr_007_and_status.md` §4.1) | Enterprise Architect | Program Orchestrator | Pointer repair: yes. The rest: see §12 |

**Proposed threat-model delta (text only; this pack writes no threat model) [Committee]:**

| Proposed row | Threat | Boundary | Control today | Test |
|---|---|---|---|---|
| **T-8x-a** | A workload in a plane namespace with **no default-deny** (`edge`, `security`) reaches any destination, including a broker CIDR, because no policy selects it | B1, B4, B5 | **none**; the checker requires default-deny in three namespaces only | none [Open: C-001-5] |
| **T-8x-b** | A rule that admits a plane "to the intent queue only" or "for read-only queries only" admits it to **every pod in the namespace**, because the restriction is a comment and the selector is `{}` | B3, B4 | **none on the ingress side**; the egress side names the pod | none [Open: C-001-4] |
| **T-8x-c** | Execution-plane code loaded in the analytics process (ADR-008 single code path, ADR-013 per-platform guard) is reachable without crossing any network boundary | B3, B6 | private per-platform `PlaneGuard` (ADR-013, T-28); the `mcp_servers` import scan (TC-AI-005) | TC-AI-006, TC-AI-005; the delta REVIEW_C3 asked for is owed [Open] |

**Proposed DECISION_LOG row (text only; this pack writes no ledger) [Committee]:**

> | D-0xx | 2026-09-09 | O-177: ADR-001 **plane topology decided as amended** — five plane namespaces (`analytics`, `control`, `execution`, `security`, `edge`), not three; the permitted inter-plane route set is **closed, explicit and directional** with exactly ten rows, identical to `rtcore.planes.ALLOWED_ROUTES`, and a row is added only by a new ADR with the ARB and the Security & Privacy Board; Analytics reaches Control only at the trade-intent queue and has no route to Execution, a broker or the vault; only Execution holds a broker route, as explicit CIDRs per certified adapter, never `0.0.0.0/0`; every permitted route is restricted by a **selector on both sides, never by a comment**; every plane namespace carries default-deny. **No cluster has ever applied these manifests; nothing here authorises an environment; no latency, capacity or cost figure is stated or derivable; the previous claim that injection blast radius is confined to Analytics is withdrawn, because every plane runs in one process in dev/sim (ADR-010, ADR-013).** Conditions C-001-1..C-001-10. This decision supplies **no reviewer signature**: the Security Architect's and Cloud Architect's reviews of the amended text, the SRE Lead's review of `docs/NFR.md`, the Cloud Architect's review of CONTAINER_DIAGRAM and the IVA finding all remain pending | Product Owner (D-039) / delegate (D-040) · Council: **ARB with the Security & Privacy Board — recommendation DECIDE WITH AMENDMENTS** (`docs/SESSIONS/COUNCIL_2026-09-09_arb_adr_001.md`); the pack's author declared a non-independence of reliance (§1) | Decide as proposed (rejected: three-plane naming, ungrouped contexts, seven unstated permitted routes, comment-only ingress restriction, withdrawn blast-radius claim, broken register pointer); replace (rejected: the invariant is sound and is relied on by nine manifests, four tests, a CI gate and two ADRs); do not decide yet (held as the fallback if the amendment is declined) | [Source: 00, 03, 04] / [Committee] / [Open: H-05, O-42, IVA-10, IVA-11, O-180, O-03] | ADR-001 rev.1; NFR-SEC-01a/01b; RTM rows; CONTAINER_DIAGRAM v1.2; network policies; `scripts/check_network_policies.py`; RAID O-177, O-180 |

**Proposed RAID rows (text only; this pack writes no ledger) [Committee]:**

| Proposed id | Type | Text | Owner | Gate |
|---|---|---|---|---|
| **O-177** (update) | Issue | Append: "ARB pack prepared 2026-09-09 (`COUNCIL_2026-09-09_arb_adr_001.md`): recommendation **DECIDE WITH AMENDMENTS**, amended ADR text and amended NFR text supplied, conditions C-001-1..C-001-10. The ARB and the Security & Privacy Board have **not** met on it; the pack's positions are drafted in role and unconfirmed. Fallback if the amendment is declined: **DO NOT DECIDE YET** and do not convene Gate B on ADR-001. Closes on the decision **and** steps 1–11 of §10" | ARB chair, Security & Privacy Board chair, Enterprise Architect | B |
| **O-18x-a** (new) | Gap | "**Two of the five plane namespaces have no default-deny policy.** `infra/kubernetes/network-policies/` contains no file for `edge`, and `security` carries only a vault-pod ingress rule; `scripts/check_network_policies.py:101` requires default-deny in `analytics`, `control` and `execution` only. Under the additive semantics assumed in O-42, a pod no policy selects is unrestricted, and the `edge` namespace holds the BFF, which in the code's route table may reach Control, Analytics and Execution. No cluster exists, so this is a manifest defect and not a live exposure [Open: H-05]. Remedy C-001-5" | Cloud Architect, Security Architect | B |
| **O-18x-b** (new) | Gap | "**Two ingress rules assert in a comment what their selector does not express.** `control.yaml:20-22` admits the Analytics plane on 8443 under the comment 'intent-queue only' with `podSelector: {}`; `execution.yaml:19-21` admits Edge on 8444 under 'read-only order/position queries' with `podSelector: {}`. The checker reads egress only. The 'analytics reaches Control only via the queue' invariant is therefore single-sided. Remedy C-001-4" | Security Architect, Cloud Architect | B |
| **O-18x-c** (new) | Gap | "**`rtcore.planes.ALLOWED_ROUTES` declares ten routes and is consulted at two call sites** (`intent_queue.py:47`, `gateway.py:286`); `cancel_command` is declared and checked nowhere. A declared table that no code consults is the defect the Red-Team found in the egress allowlist three days earlier (THREAT_MODEL v1.2, RT-F1). Remedy: TC-NET-005 (C-001-3) plus a disposition on IVA-10 (C-001-6)" | Backend Lead, Security Architect | B |
| **O-18x-d** (new) | Issue | "**IVA-10 has never had a register row.** `ExecutionGateway.cancel` and `cancel_all` carry no plane check; recorded in `docs/GATE_REPORTS/GATE_B_2026-09-07.md:104` on 2026-09-07 and still true at `42f19c6`. A finding that lives only in a gate report is not tracked" | Program Orchestrator, Security Architect | B |
| **O-18x-e** (new) | Gap | "**Sixteen ADR files point at the wrong register row.** Their undecided note reads '[Open: O-169 proposed]'; O-169 in `docs/RAID_LOG.md:230` is an unrelated, **closed** trust-anchor issue. The row that carries the ADR status work is O-177. An `[Open]` tag whose id resolves to a closed, unrelated row is worse than no tag. Remedy C-001-9" | Enterprise Architect | B |

---

## 11. Independent Validation

The Independent Validation Agent was **not** convened for this session, and no finding of its is quoted or implied here [Open].

Because of the author's declared interest (§1), the Product Owner is asked to require an IVA finding on four points **before** deciding:

1. **Answer O-180 first.** Whether D-042's ratification of D-004 reaches ADR-001..008 changes how eight ADR rows are worded. §4.5 argues that it does not change this one; that argument should be tested by a line that did not write it.
2. **Reproduce F-3, F-4, F-5, F-7, F-8, F-9, F-13, F-14 and F-16 independently** — the namespace/plane counts, the absent grouping, the `infra/` inventory, the two namespaces without default-deny, the comment-only ingress restrictions, the two guard call sites, the untraced tests, the doubled requirement id and the broken register pointer.
3. **Test the "declared but not consulted" argument (F-9, F-17)** against the Red-Team's own RT-F1 finding, since it is the finding that turns this amendment from tidy-up into necessity, and it was produced by the author of the document being amended.
4. **Confirm that no capacity, latency, cost, provider, broker or venue figure appears anywhere in this packet or in the amended ADR and NFR text**, and that the amended text authorises no environment and advances no gate.

---

## 12. A larger finding this pack did not go looking for [Committee]

The defect that makes ADR-001 weaker than it reads is not "an undecided ADR". It is a class that has now been found three times in this repository by three different lines in eight days:

- **The Red-Team, 2026-09-08:** an egress allowlist named as a delivered control while `EgressPolicy.check()` was consulted by no product code (F-17) — blocking, and fixed.
- **This pack, 2026-09-09:** a ten-row route table named as the topology while it is consulted at two call sites, and two ingress restrictions that live in YAML comments (F-8, F-9).
- **The Cloud Architect, 2026-09-08:** a cost sheet cell reading "0 by design" in a sheet whose own rule forbids an unmeasured figure [Source: docs/SESSIONS/COUNCIL_2026-09-08_arb_adr_007.md §1].

**The pattern is the same in all three: an artefact that *declares* a control is cited as though it *enforced* one.** A test suite cannot catch it, because the declaration is usually true — the table really does say that, the allowlist really does list those hosts. Only a reader who asks "what calls this?" catches it.

**A rule the ARB could adopt, for the Product Owner and not for this pack to settle [Committee]:** any artefact cited in a gate pack as a control must name, in the pack, **the call site or the check that consults it**; where there is none, the artefact is a specification and is cited as one. This is cheap — it is one column in the evidence index — and it would have caught all three findings above at the point of citation rather than at the point of review.

---

## 13. Concerns for the Product Owner

- **PO-1 The ARB pack recommends deciding ADR-001, but not the sentence you have.** The invariant — analytics has no route to execution or a broker, and reaches control only at the trade-intent queue — is right, is what the blueprint requires, and is what nine manifests, four tests, a CI gate and two other ADRs already assume. What is wrong is everything around it: the title says three planes and the tree deploys **five namespaces** and models **six plane identities**; the Decision assigns "the 20 bounded contexts" to planes and **no artefact lists that assignment** — my own component and sequence diagrams do not contain the word "plane"; and the Consequences claims injection blast radius is confined to Analytics, which is not true in dev/sim, where every plane runs in one process. I am asking you to decide the route set and to refuse the claims about enforcement.

- **PO-2 The most useful sentence in this packet is the one that says what runs.** Today, ADR-001 is enforced by a Python script that reads nine YAML files in CI, by two `check_caller` lines in the product code, and by an import scan that makes the dangerous modules unreachable to MCP servers. That is a genuine and unusually good set of controls for this stage, and I want it recorded as such. It is **not** a network boundary: the manifests have never been applied to a cluster, and in-process the guard's caller declares its own plane, so the guard catches a component wired wrongly — not an adversary. Every packet this week that said "plane topology enforced" was leaning on a static file check.

- **PO-3 Two of the five namespaces have no default-deny, and one of them is the front door.** There is no policy file at all for the `edge` namespace, and `security` has only a vault ingress rule. Under the semantics this repository assumes, a pod that no policy selects is unrestricted — and `edge` is where the BFF and human sessions live, and in the code's own route table Edge may reach Control, Analytics **and** Execution. Nothing is deployed, so this is a defect in a manifest set and not a live exposure; but it is exactly the kind of thing that ships the day a cluster is created, and it exists because ADR-001's title names three planes and nobody writes a policy for a namespace the architecture decision never mentions.

- **PO-4 Two restrictions that this platform relies on are written in comments.** The rule "Analytics may reach Control **only at the intent queue**" is expressed as a pod selector on the way out of Analytics — and, on the way into Control, as a `#` comment beside a rule that admits every pod in the namespace. The same is true of "read-only order/position queries" on the Execution side. The checker reads egress and not ingress, so nothing notices. A control with one side missing is a control that works until someone edits the other file.

- **PO-5 The four tests everyone quotes are not traced to a requirement.** The RTM contains one row citing a TC-NET id, and it cites TC-NET-003 alone; TC-NET-001, -002 and -004 appear in no row. Meanwhile `NFR-SEC-01` means the **plane** requirement in `docs/NFR.md` and the **asymmetric-signing** requirement in the RTM — one id, two requirements, and the plane tests mark themselves against it. That is my file and my defect, and §9 contains the split that fixes it.

- **PO-6 Deciding this creates nothing, and I would rather you hear it from me.** `infra/` holds five namespaces, nine network policies, a dev/sim compose file and **no workload object of any kind** — so nothing places a service in a plane, and no test can check plane membership until a workload manifest exists. If you decide ADR-001, you have decided a **constraint on future work**. No environment is authorised and no gate advances.

- **PO-7 On whether you already decided this in D-004.** D-004 says "ADR-001..008 proposed to ARB" and D-042 ratified D-004; O-180 asks whether that reaches the ADRs. My reading is that it ratifies the act of proposing, and I flagged my own reading as the thing an independent line should check first. It matters less than it looks: **even on the wider reading, D-004 records no scope, no conditions and no alternatives, and D-042's own words call the object "proposed"**. A status line written from it would say "Accepted" while the ledger it cites says "proposed" — the ADR-017 ambiguity the reconciliation was run to remove. Either way you need a fresh entry.

- **PO-8 What I could not verify, plainly.** Whether the target CNI implements NetworkPolicy the way the effective-union checker assumes — that is O-42 and it is "verified by reading only". Whether any broker endpoint resembles the CIDR in `execution.yaml`; it is an RFC 5737 documentation range used as a sim placeholder and I assert no broker capability. What any of this costs in latency: no baseline exists in this repository and the amended ADR states none.

- **PO-9 I must tell you where I am not independent.** I did not write ADR-001 — it came in the bootstrap commit — but I own `docs/ADRs/`, I own `docs/NFR.md` whose NFR-SEC-01 target column ("Enforced by policy, tested") this packet says is wrong, I own the two C4 diagrams that never mention planes, and I applied the ADR-007 amendment that cites ADR-001 as delivering route isolation. That is a reliance, and it is why this is a **recommendation and not an approval**, why the Security Architect and the Cloud Architect — not I — must review the amended text, why the ARB and the Security & Privacy Board must actually meet on it rather than accept positions I drafted for their seats, and why I am asking for an IVA finding first. **I have approved nothing, decided nothing and written no ledger row, and no agent may record one on your behalf** (D-039).

---

## 14. Assumptions, confidence, provenance

- **Assumptions.** The tree at `442cebd` (files quoted) and at `42f19c6` (the five documents committed mid-session by other owners) is the repository of record for this session; D-039, D-040, D-042, D-069 stand as recorded; `.claude/agents/roster.json` at this commit is the write scope of record; Kubernetes NetworkPolicy semantics are additive, which this repository records as an assumption verified by reading only [Open: O-42] [Committee].
- **Confidence.** **High** that ADR-001 is undecided and that F-1..F-6, F-9..F-11, F-13..F-16, F-18 are established by reading and by the commands in §3.3. **High** that the invariant is sound and correctly relied upon. **Medium-high** that the ten-row route table of §7 item 2 is complete — it is transcribed from `planes.py` and the five manifests, and has never met a second implementation. **Medium** on F-7 and F-8's operational consequence, which depends on the CNI semantics of O-42. **None** on any latency, capacity, cost, provider, broker or venue figure: none is stated, implied or derivable from this packet or from the amended text.
- **Provenance.** [Source: 00, 03, 04, 06, 13] as transmitted by the repository artefacts; [Committee] for this pack's reasoning and for the cited councils; [Verified] only for the file reads and command outputs quoted in §3; [Open] items carry their register ids.
- **Independence and scope.** Author of ADR-001: the bootstrap commit `03e6739`. Author of the amendment text: this pack (Enterprise Architect), to be applied by the Enterprise Architect. Reviewers: Security Architect and Cloud Architect (different lines, CODEOWNERS of the artefacts). Recommending bodies: ARB and the Security & Privacy Board — **which have not met on this pack**. Approver: **the Product Owner (D-039), or the delegate (D-040)**. **No agent recorded an approval or a decision in any ledger during this session. `docs/ADRs/`, `docs/NFR.md`, `docs/RAID_LOG.md`, `docs/DECISION_LOG.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/AUDIT_EVIDENCE_INDEX.md`, `infra/`, `libs/`, `services/`, `scripts/` and `test/` were read and not edited; this session wrote exactly one file** [Source: 13].
