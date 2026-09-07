#!/usr/bin/env bash
# Install the rt365 dev/sim build into a virtual environment (Linux/macOS).
# Usage: installer/install.sh [target-dir]   (default: ~/.rt365)
# Needs: python3 >= 3.11. Installs from dist/*.whl when present (see scripts/build_package.sh), else from this checkout.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-$HOME/.rt365}"
python3 - << 'PY'
import sys
assert sys.version_info >= (3, 11), f"python >= 3.11 required, found {sys.version.split()[0]}"
PY
python3 -m venv "$TARGET/venv"
"$TARGET/venv/bin/python" -m pip install --upgrade pip >/dev/null
WHEEL="$(ls "$ROOT"/dist/rt365_robotrader-*.whl 2>/dev/null | head -n1 || true)"
if [ -n "$WHEEL" ]; then
  if [ -f "$WHEEL.sha256" ]; then ( cd "$(dirname "$WHEEL")" && (sha256sum -c "$(basename "$WHEEL").sha256" 2>/dev/null || shasum -a 256 -c "$(basename "$WHEEL").sha256") ); fi
  "$TARGET/venv/bin/python" -m pip install "$WHEEL"
else
  "$TARGET/venv/bin/python" -m pip install "$ROOT"
  # a checkout install has no bundled resources: point the CLI at the checkout
  echo "export RT365_HOME=\"$ROOT\"" > "$TARGET/env.sh"
fi
mkdir -p "$TARGET/bin"
cat > "$TARGET/bin/rt365" << WRAP
#!/usr/bin/env bash
[ -f "$TARGET/env.sh" ] && . "$TARGET/env.sh"
exec "$TARGET/venv/bin/rt365" "\$@"
WRAP
chmod +x "$TARGET/bin/rt365"
"$TARGET/bin/rt365" version
echo
echo "Installed to $TARGET. Add $TARGET/bin to PATH, then:"
echo "  rt365 check --env sim      # verify signed registry, policies, planes, audit chain"
echo "  rt365 serve --env sim      # dashboard on http://127.0.0.1:8080 (dev header auth, sim only)"
echo "  rt365 mcp-serve --env sim  # MCP stdio tool server for an agent host (see .mcp.json)"
echo "Nothing installed here is authorised beyond the sim environment (docs/MISSING_ACTIONS.md)."
