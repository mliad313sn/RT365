#!/usr/bin/env bash
# Bootstrap the RoboTrader repository structure [Source: 16] with protected paths and CI skeleton.
#
# Two modes:
#   scripts/bootstrap_repo.sh            -> in-place: verifies/creates the structure in this repository
#                                           (kit v1.1 + dev/sim build already present) and prints the make targets
#   scripts/bootstrap_repo.sh <dir>      -> creates a fresh skeleton at <dir> from this kit (original v1.1 behaviour)
set -euo pipefail
KIT="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="${1:-$KIT}"
mkdir -p "$ROOT"/{apps/web,apps/admin,mcp/servers,mcp/policies,connectors/brokers,connectors/data-providers,contracts/api,contracts/events,infra/iac,infra/kubernetes,observability,security,test,docs,scripts,.github/workflows}
for s in market-data strategy backtest portfolio risk compliance approval oms execution reconciliation audit identity killswitch tenant notification billing support; do mkdir -p "$ROOT/services/$s"; done
if [ "$ROOT" != "$KIT" ]; then
  cp -r "$KIT/docs/." "$ROOT/docs/"; cp -r "$KIT/goals" "$ROOT/docs/goals"; cp "$KIT/GOAL.md" "$ROOT/docs/GOAL.md"
  cp "$KIT/contracts/api/API_OPENAPI.yaml" "$ROOT/contracts/api/"; cp "$KIT/contracts/events/README.md" "$ROOT/contracts/events/"; cp "$KIT/mcp/policies/README.md" "$ROOT/mcp/policies/"
  cp "$KIT/.github/CODEOWNERS" "$ROOT/.github/CODEOWNERS"
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
fi
cat > "$ROOT/CLAUDE.md" << 'C'
# RoboTrader — instructions for coding agents
Read GOAL.md and goals/build/<epic>.md for the epic you are assigned; follow docs/PROJECT_EXECUTION_PLAN.md.
Never: give AI/MCP components a broker route, a secret, a limit write path, an audit delete path, or a way to change mode.
Always: tests first (control quartet for control-bearing code), correlation_id in logs, RTM row per story, DoD checklist in PR.
Protected paths (see .github/CODEOWNERS) need 2nd-line approval. Run `make all` before pushing.
Environment ladder: dev -> sim -> shadow -> paper -> supervised pilot -> capped autonomous pilot -> controlled GA; never promote past what the gate authorises.
C
echo "Bootstrapped $ROOT"
echo "Next: make install && make all   (see README.md; MISSING_ACTIONS.md lists the human-only steps)"
