#!/usr/bin/env bash
# Build the installable distribution: stages the resource bundle into the rt365_cli package, then builds
# the wheel and sdist into dist/ with SHA-256 checksums [ADR-016]. Usage: scripts/build_package.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BUNDLE="apps/cli/rt365_cli/_bundle"
rm -rf "$BUNDLE" dist build
mkdir -p "$BUNDLE"
for rel in mcp/policies observability/alerts.yaml observability/slis.yaml services/risk/policies apps/web/static; do
  mkdir -p "$BUNDLE/$(dirname "$rel")"
  cp -r "$rel" "$BUNDLE/$rel"
done
python3 -m build --wheel --sdist
( cd dist && for f in *; do
    if command -v sha256sum >/dev/null 2>&1; then sha256sum "$f" > "$f.sha256"; else shasum -a 256 "$f" > "$f.sha256"; fi
  done )
rm -rf "$BUNDLE"
echo "built:"; ls -1 dist
echo "install with: pip install dist/rt365_robotrader-*.whl   (then: rt365 check --env sim)"
