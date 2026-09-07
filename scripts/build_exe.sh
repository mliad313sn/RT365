#!/usr/bin/env bash
# Build the one-file executable for the current platform with PyInstaller (rt365 on Linux/macOS, rt365.exe on Windows).
# The Windows .exe is produced by .github/workflows/release.yml on a windows runner; this script builds only for the host OS.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m PyInstaller --clean --noconfirm --distpath dist/bin --workpath build/pyinstaller installer/rt365.spec
BIN="dist/bin/rt365"; [ -f "$BIN.exe" ] && BIN="$BIN.exe"
if command -v sha256sum >/dev/null 2>&1; then sha256sum "$BIN" > "$BIN.sha256"; else shasum -a 256 "$BIN" > "$BIN.sha256"; fi
echo "built $BIN"; "$BIN" version
