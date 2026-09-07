# RoboTrader — instructions for coding agents
Read GOAL.md and goals/build/<epic>.md for the epic you are assigned; follow docs/PROJECT_EXECUTION_PLAN.md.
Never: give AI/MCP components a broker route, a secret, a limit write path, an audit delete path, or a way to change mode.
Always: tests first (control quartet for control-bearing code), correlation_id in logs, RTM row per story, DoD checklist in PR.
Protected paths (see .github/CODEOWNERS) need 2nd-line approval. Run `make all` before pushing.
Environment ladder: dev -> sim -> shadow -> paper -> supervised pilot -> capped autonomous pilot -> controlled GA; never promote past what the gate authorises.
