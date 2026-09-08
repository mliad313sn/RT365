# RoboTrader — instructions for coding agents
Read GOAL.md and goals/build/<epic>.md for the epic you are assigned; follow docs/PROJECT_EXECUTION_PLAN.md.
Never: give AI/MCP components a broker route, a secret, a limit write path, an audit delete path, or a way to change mode.
Always: tests first (control quartet for control-bearing code), correlation_id in logs, RTM row per story, DoD checklist in PR.
Protected paths (see .github/CODEOWNERS) need 2nd-line approval. Run `make all` before pushing.
Environment ladder: dev -> sim -> shadow -> paper -> supervised pilot -> capped autonomous pilot -> controlled GA; never promote past what the gate authorises.
Agents: one per goals/ prompt, generated into .claude/agents by `make agents` (CI runs `make agents-check`); MCP: only `rt365-sim` in .mcp.json (six registered tools, sim identity). Product Owner: docs/PRODUCT_OWNER.md — the human Product Owner decides every human decision and gate (D-039); councils are advisory; open decisions live in docs/PO_DECISION_QUEUE.md; agents never record an approval.
Executability: `rt365 check --env sim` and `rt365 probe --env sim` must pass; `make package` / `make exe` build the wheel and the one-file executable (rt365.exe from the release workflow).
