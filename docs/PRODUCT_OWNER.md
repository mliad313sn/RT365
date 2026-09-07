# PRODUCT_OWNER — appointment record

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Owner | Compliance Agent | Executive Steering | A | Appointed (acting) 2026-09-07 — ratification pending (MISSING_ACTIONS H-23) |

## Appointment [Committee]
| Field | Value |
|---|---|
| Role | Product Owner (1st line) — accountable for product completeness and executability; role prompt `goals/00_product_owner.md`; agent `.claude/agents/product-owner.md` |
| Appointed person | The repository owner (GitHub `mliad313sn`), acting Product Owner from 2026-09-07 by the `/goal` instruction "appoint a product owner and all agent and MCP required to ensure this project is complete and executable" |
| Appointing authority | Delivery Orchestrator (AI) on the owner's instruction; **ratification by Executive Steering pending** (H-23, blocks Gate A). Until ratified the appointment is acting: it can prioritise and accept increments; it cannot pass a gate. |
| Delegate | `product-owner` agent (Claude Code sub-agent generated from `goals/00_product_owner.md`) — prepares backlog order, acceptance packets, roster and executability checks; every acceptance it drafts names a human reviewer and approver |
| Deputy | [Open: O-19] — to be named with the other deputies |
| Line | 1st (build and run). Never 2nd or 3rd line for any control it prioritises [Source: 13] |
| Decision right | Backlog priority and definition of done for the product; epic acceptance recommendation to the Product Council |
| Segregation | May not approve risk limits, compliance enablement, security acceptance, models/strategies, gates or its own acceptance records; protected paths still require the 2nd-line CODEOWNER |

## Relationship to the Product Director [Committee]
The blueprint names a Product Director (scope, personas, value, pricing, roadmap; `goals/01_product_director.md`). The Product Owner is the accountable person for delivery completeness and executability of that scope, one level closer to the build: the Director says *what the product is*, the Owner says *what is done next and whether it is done*. The two seats may be held by one person until the organisation staffs both (H-01); when they are, the Product Director chairs the Product Council and the Product Owner presents to it.

## Accountabilities (RACI extract; full table in RACI.md)
| Control / decision | R | A | C | I |
|---|---|---|---|---|
| Backlog priority and story readiness | Program Orchestrator | **Product Owner** | Product Director, epic leads | IVA |
| Epic acceptance against PRD and DoD | Epic accountable lead | **Product Owner** (recommends) → Product Council (approves) | 2nd-line reviewer of the epic | IVA |
| Agent and MCP roster (`.claude/agents/`, `.mcp.json`, docs/AGENT_ROSTER.md) | Delivery Orchestrator (AI) | **Product Owner** | MCP Security Agent (any MCP server), Security Architect | all |
| Executability (install, check, serve, package, release) | Backend Lead, SRE Lead | **Product Owner** | Cloud Architect | CAB |

## Evidence
- Decision D-035 (DECISION_LOG.md); MISSING_ACTIONS H-23; RAID O-57.
- Executability evidence: `make all`, `rt365 check --env sim`, `rt365 probe --env sim`, `scripts/generate_agents.py --check`, `make package`, `.github/workflows/release.yml` — TC-PKG-001..004, TC-AI-012..015, TC-AGT-001..004.
