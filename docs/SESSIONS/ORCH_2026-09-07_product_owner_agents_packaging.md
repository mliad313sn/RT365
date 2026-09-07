# Session packet ORCH-2 — Product Owner appointment, agent and MCP roster, installable distribution

| Session | Date | Environment | Status | Documented by |
|---|---|---|---|---|
| ORCH-2 | 2026-09-07 | dev/sim only | Orchestrator output packet; recommends, never approves | Master Delivery Orchestrator (AI), on the repository owner's `/goal` instruction |

Instruction: "appoint a product owner and all agent and MCP required to ensure this project is complete and executable, create as well installation package and .exe if missing". Branch `claude/project-owner-agent-setup-hi3xqu`, built on `2b44f76`.

## 1 Roles
| Role | Actor | Line |
|---|---|---|
| Product Owner (acting) | repository owner (GitHub `mliad313sn`), delegated to the generated `product-owner` agent | 1st |
| Builder of record | Delivery Orchestrator (AI) executing goals/build/E09 (stdio transport), E12 (probe CLI), E13 (distribution, guard) | 1st |
| Reviewers (pending) | MCP Security Agent (stdio transport, `.mcp.json`, agent guard), Security Architect (distribution), SRE Lead (installers, release workflow), Compliance Agent (appointment record) | 2nd |
| Assurance (pending) | Independent Validation Agent | 3rd |
| Approvers (pending) | Executive Steering (H-23), ARB and Security & Privacy Board (ADR-016), CAB (release channel) | human |

## 2 Purpose
- [Source: 13] Name a single accountable owner for completeness and executability without giving that seat any approval right over risk, compliance, security, models or gates.
- [Source: 00, 04] Give agent hosts exactly one path to the six tools, through the existing runtime, with identity bound by the host process.
- [Source: 16] Make the product installable and runnable from a clean machine with the same fail-closed rules as the source tree.
- [Committee] Turn every prompt of the kit into an invocable agent, machine-check the three lines of defense for agents, and supply the `goals/build/` prompts that CLAUDE.md and the session packets referenced but which did not exist (O-31).
- [Open] Ratification (H-23), Windows build evidence (H-24), tool registration (O-35), artefact signing (O-23), harness hook support (O-58).

## 3 Decisions and ADRs
D-035 (Product Owner), D-036 (generated agents + guard), D-037 (stdio transport), D-038 (distribution) in docs/DECISION_LOG.md; ADR-016 with five alternatives. All Proposed; none approved.

## 4 RTM
FR-09 extended with TC-AI-012..015; NFR-SEC-02 extended with the roster drift check and release workflow; new rows NFR-DIST-01 (TC-PKG-001..004) and NFR-GOV-01 (TC-AGT-001..004) in docs/REQUIREMENTS_TRACEABILITY.md v1.3; NFR.md carries the two new requirements.

## 5 Threat-model delta
T-47 (MCP transport exposure), T-48 (agent authoring what it reviews), T-49 (tampered resource bundle), T-50 (unlabelled or non-sim binary) in docs/THREAT_MODEL.md, each with control → test → owner.

## 6 Control quartets
| Control | positive | negative | abuse | recovery |
|---|---|---|---|---|
| MCP stdio transport | TC-AI-012 | TC-AI-013 | TC-AI-014 | TC-AI-015 |
| Distribution fail-closed rules | TC-PKG-001 | TC-PKG-002 | TC-PKG-003 | TC-PKG-004 |
| Agent roster and write-scope guard | TC-AGT-001 | TC-AGT-002 | TC-AGT-003 | TC-AGT-004 |
Suite: 163 tests, 17 areas with a full quartet (docs/TEST_CASES/EVIDENCE_REPORT.md).

## 7 Evidence list
| Evidence | Location |
|---|---|
| Appointment | docs/PRODUCT_OWNER.md; goals/00_product_owner.md; docs/RACI.md; `Role.PRODUCT_OWNER` |
| Agents | .claude/agents/ (51 files + roster.json); docs/AGENT_ROSTER.md; scripts/generate_agents.py --check (CI job) |
| Build prompts | goals/build/README.md, E01..E15 |
| MCP | .mcp.json; mcp/servers/mcp_servers/stdio.py; docs/MCP_TOOL_CATALOG.md §Servers; smoke test `printf '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \| rt365 mcp-serve --env sim` |
| Distribution | apps/cli/rt365_cli; libs/core/rtcore/resources.py; installer/; scripts/build_package.sh, build_exe.sh; .github/workflows/release.yml; docs/INSTALLATION.md |
| Local build verification (this session) | wheel `rt365_robotrader-0.1.0-py3-none-any.whl` installed into a clean venv and `rt365 version/check/probe` run from `/tmp` (resource root resolved to the installed bundle); Linux one-file binary `dist/bin/rt365` (16.2 MiB, PyInstaller 6.22.2 in a clean venv), SHA-256 `7120081adb69eaed2b9108accce79d13eae9020c34164a64ee23aa717524bad8`, run from `/tmp`: `version`, `check`, `probe` pass; `check --env production` exit 1; unlabelled `check` exit 2; bogus `RT365_HOME` exit 1; `mcp-serve` lists six tools and denies `cancel_order` |
| Not verified here | Windows `rt365.exe` (no Windows host; produced and smoke-tested by the `exe` job on `windows-latest`, H-24); macOS binary likewise |
| Ledgers | DECISION_LOG D-035..D-038; RAID O-57..O-59, R-46, R-47; MISSING_ACTIONS H-23, H-24; AUDIT_EVIDENCE_INDEX rows 25..29 |

## 8 RAID, assumptions, confidence, provenance
- Assumptions: the acting Product Owner is the repository owner because the instruction came from them; a person of record and deputy are named at ratification (H-23, O-19). Claude Code honours `hooks:` in agent frontmatter (O-58); where it does not, the roster is advisory and CODEOWNERS remains the control. The 8-hour MCP session identity is acceptable only in sim (R-47).
- Confidence: high that the wheel and the Linux binary behave as the tests and the smoke run state on this commit; medium for the Windows and macOS binaries (same spec, same smoke test, run by CI on hosts this session does not have); none about any environment beyond sim.
- Provenance: [Source: NN] kit documents; [Committee] this packet and ADR-016; [Verified] commands listed under evidence; [Open] as tagged.
