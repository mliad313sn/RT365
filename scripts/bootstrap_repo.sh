#!/usr/bin/env bash
# Bootstrap the RoboTrader repository structure [Source: 16] with protected paths and CI skeleton.
set -euo pipefail
ROOT="${1:-robotrader}"
mkdir -p "$ROOT"/{apps/web,apps/admin,mcp/servers,mcp/policies,connectors/brokers,connectors/data-providers,contracts/api,contracts/events,infra/iac,infra/kubernetes,observability,security,test,docs,scripts,.github/workflows}
for s in market-data strategy backtest portfolio risk compliance approval oms execution reconciliation audit identity tenant notification billing support; do mkdir -p "$ROOT/services/$s"; done
KIT="$(cd "$(dirname "$0")/.." && pwd)"
cp -r "$KIT/docs/." "$ROOT/docs/"; cp -r "$KIT/goals" "$ROOT/docs/goals"; cp "$KIT/GOAL.md" "$ROOT/docs/GOAL.md"
cp "$KIT/contracts/api/API_OPENAPI.yaml" "$ROOT/contracts/api/"; cp "$KIT/contracts/events/README.md" "$ROOT/contracts/events/"; cp "$KIT/mcp/policies/README.md" "$ROOT/mcp/policies/"
cat > "$ROOT/CODEOWNERS" << 'C'
# Protected paths require 2nd-line approval [Committee]. Replace handles with real reviewers.
/services/risk/         @chief-risk-agent
/services/compliance/   @compliance-agent
/services/execution/    @trading-domain-lead
/mcp/policies/          @mcp-security-agent
/security/              @security-architect
/contracts/             @integration-architect @chief-risk-agent
C
cat > "$ROOT/.github/workflows/ci.yml" << 'C'
name: ci
on: [pull_request]
jobs:
  gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Unit + property + contract tests
        run: echo "TODO: run test suites per docs/TEST_STRATEGY.md"
      - name: SAST / SCA / secret scan
        run: echo "TODO: wire scanners; fail on critical"
      - name: SBOM + signature
        run: echo "TODO: generate CycloneDX SBOM and sign artefact"
      - name: Determinism check (risk engine)
        run: echo "TODO: run TC-RK-001..004; fail on any divergence"
      - name: Network-policy tests
        run: echo "TODO: run TC-NET-001..004"
C
cat > "$ROOT/CLAUDE.md" << 'C'
# RoboTrader — instructions for coding agents
Read docs/GOAL.md and docs/goals/build/<epic>.md for the epic you are assigned.
Never: give AI/MCP components a broker route, a secret, a limit write path, an audit delete path, or a way to change mode.
Always: tests first (control quartet for control-bearing code), correlation_id in logs, RTM row per story, DoD checklist in PR.
Protected paths (see CODEOWNERS) need 2nd-line approval.
C
echo "Bootstrapped $ROOT"
