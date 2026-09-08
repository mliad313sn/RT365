# PRODUCT_OWNER — appointment and authority record

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Owner | Compliance Agent (record review) | Product Owner (self-declared authority, D-039); ratification of the appointment H-23 closed by the owner's declaration | A | v2.1 — authority model declared 2026-09-08 (D-039) and all decisions delegated to the Product Owner agent (D-040) |

## Appointment [Committee → Owner declaration]
| Field | Value |
|---|---|
| Role | Product Owner — the single human decision authority for the product; role prompt `goals/00_product_owner.md`; delegate agent `.claude/agents/product-owner.md` |
| Person | The repository owner (GitHub `mliad313sn`), appointed 2026-09-07 (D-035) and declared decision authority 2026-09-08 (D-039) |
| Authority (owner declaration, 2026-09-08) | The Product Owner is in charge of approving **any human decision** (every row of docs/MISSING_ACTIONS.md and docs/PO_DECISION_QUEUE.md, every gate A–F, every risk acceptance and every override) and **fully drives the development until the final product is ready for a controlled market release**. The Product Owner **may convene any council** to help choose the most appropriate option in the benefit of the final goal; councils are advisory. |
| Delegate | `product-owner` agent: **decides every item of the decision queue under D-040**, convenes councils first, records each decision with alternatives and dissent, executes the consequences. Residual human-only acts: facts only the owner knows (operating entity, country), external counsel opinions, signed contracts, payments, real credentials into the vault, and the second distinct person in runtime two-person controls |
| Deputy | [Open: O-19] — required as the second human for runtime two-person controls |
| Line | 1st (decides and drives); the councils supply the 2nd- and 3rd-line views it must hear before deciding |

## Decision protocol [Committee; D-039]
1. Every open human decision is a row in docs/PO_DECISION_QUEUE.md with the gate it blocks, the council to convene, the prepared pack, the recommendation and a decision field.
2. The delegate convenes the council: member agents write option analyses to `docs/SESSIONS/COUNCIL_<date>_<topic>_*.md`, a different-line member challenges, the Independent Validation Agent checks the evidence.
3. The human Product Owner decides (approve / reject / defer / override). The delegate records it in docs/DECISION_LOG.md with the alternatives, the council recommendation and any dissent, updates the ledgers and executes the consequences (build prompts, MISSING_ACTIONS, RTM).
4. An Independent Validation VETO closes a gate unless the Product Owner overrides it **in writing** with the finding, the accepted risk and the compensating control (risk-acceptance record in DECISION_LOG and RAID).
5. Under D-040 the Product Owner agent's recorded decision is the decision; the owner may reverse any of them in session. Nothing decided promotes an environment beyond what the gate evidence supports without the override record above, and nothing decided creates an external fact (legal basis, licence, contract, credential) — those stay [Open] until the external evidence exists.

## Deviation from the blueprint and compensating controls [Committee; risk accepted by the owner, R-48]
Blueprint 13 required independent 2nd-line approvers and an Executive Steering that cannot override an Independent Validation veto on evidence grounds. The owner's declaration concentrates all human approval in the Product Owner. Compensating controls: (a) every decision carries the council recommendation and dissent; (b) overrides are explicit written risk acceptances; (c) the runtime two-person controls (Kill Switch deactivation, dual-key jurisdiction flag, maker-checker limit changes) are technical and still require a second distinct human — the Product Owner cannot be both persons, hence the deputy (O-19); (d) the agents remain segregated by line (TC-AGT) and never approve; (e) external obligations (regulator, broker, counsel, data licences) are not changed by any internal decision and stay [Open] until evidenced.

## Relationship to the Product Director
The Product Director (`goals/01`) keeps scope, personas, value, pricing and roadmap and chairs the Product Council as an advisory body. The Product Owner decides. Both seats are held by the repository owner until staffed (H-01).

## Accountabilities (RACI extract; full table in RACI.md)
| Control / decision | R | A | C | I |
|---|---|---|---|---|
| Every human decision, gate and risk acceptance | delegate agent prepares; councils recommend | **Product Owner** | council members per topic | IVA, all |
| Backlog priority, DoD, epic acceptance | Program Orchestrator, epic leads | **Product Owner** | Product Director | IVA |
| Agent and MCP roster | Delivery Orchestrator (AI) | **Product Owner** | MCP Security Agent, Security Architect | all |
| Executability (install, check, serve, package, release) | Backend Lead, SRE Lead | **Product Owner** | Cloud Architect | CAB (advisory) |
| Runtime two-person actions | Product Owner + deputy (different persons) | **Product Owner** | Chief Risk Agent | all |

## Evidence
D-035, D-039 (DECISION_LOG.md); H-23 closed by owner declaration; R-48 (RAID_LOG.md); docs/PO_DECISION_QUEUE.md; council packets docs/SESSIONS/COUNCIL_*.md.
