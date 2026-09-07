# INSTALLATION — installing and running the dev/sim build

| Owner | Reviewer (different line) | Approving body | First gate | Status |
|---|---|---|---|---|
| Product Owner | SRE Lead | CAB | B | v1.0 — 2026-09-07 |

Everything below installs the **development/simulation** build. It proves the control envelope on simulated data with a simulated broker; it enables no market, strategy, broker or autonomy, and it refuses to run under any environment label other than `sim` (docs/MISSING_ACTIONS.md, docs/GATE_REPORTS/).

## 1. Choose a channel
| Channel | Command | Needs |
|---|---|---|
| Source checkout (developers) | `make install && make all` | Python 3.11+, git |
| Wheel (any OS with Python) | `make package` then `pip install dist/rt365_robotrader-*.whl` | Python 3.11+ |
| Installer script | `installer/install.sh [dir]` (Linux/macOS) · `powershell -ExecutionPolicy Bypass -File installer\install.ps1` (Windows) | Python 3.11+ |
| One-file executable | `dist/bin/rt365` (Linux/macOS via `make exe`) · `rt365.exe` (Windows, from the `release` workflow artefact `rt365-windows-x64`; `installer\install.ps1 -Exe`) | nothing |
| Container | `docker compose -f infra/docker-compose.yml up` | Docker |

Verify checksums: every artefact ships with a `.sha256` file produced by the same build (`sha256sum -c`, or `Get-FileHash` on Windows). Artefacts are not yet signed [Open: O-23].

## 2. Run the self-check
```bash
rt365 version               # prints the version and the resolved resource root
rt365 check --env sim       # signed registry, egress/runtime policy invariants, plane guard, audit chain
rt365 probe --env sim       # synthetic intent through the whole control pipeline; missing spans = failure
```
`--env` (or `RT_ENV`) is mandatory: an unlabelled environment fails closed (IVA-06). `check --env production` must fail while the registry is a sim fixture signed with the dev key.

## 3. Serve
```bash
rt365 serve --env sim --port 8080     # dashboard at http://127.0.0.1:8080 (dev header auth, RAID R-06)
rt365 mcp-serve --env sim             # MCP stdio tool server; declared in .mcp.json as rt365-sim
rt365 certify-broker --env sim --out docs/BROKER_CERTIFICATIONS/sim-broker.md
```
Claude Code picks up `.mcp.json` and `.claude/agents/` from the repository root; `rt365` must be on `PATH` (the installer scripts create a launcher).

## 4. Resource bundle
The signed tool registry, allowlists, egress and runtime policy, risk policy, alert and SLI catalogues and dashboard assets are read from one resource root laid out like the repository. Resolution order: `RT365_HOME` (explicit, never falls back) → PyInstaller bundle → `rt365_cli/_bundle` in the installed wheel → the source checkout. A root without `mcp/policies/tool_registry.signed.json` is refused; a tampered registry fails the signature check (TC-PKG-003/004).

## 5. Build the artefacts yourself
```bash
pip install -e ".[dev,build]"
make package      # dist/*.whl, dist/*.tar.gz + .sha256   (scripts/build_package.sh)
make exe          # dist/bin/rt365[.exe] + .sha256 for the host OS (installer/rt365.spec)
```
Build the executable inside a clean virtual environment: PyInstaller analyses every importable package, and a broken system-wide package (for example a distro `cryptography` without `_cffi_backend`) aborts the build. The Windows `.exe` is produced by `.github/workflows/release.yml` on `windows-latest` and smoke-tested there (`version`, `check`, `probe`, fail-closed rules, `mcp-serve tools/list`); tagging `v*` attaches all artefacts to the GitHub release.

## 6. Uninstall
Delete the install directory (`~/.rt365` or `%LOCALAPPDATA%\rt365`) or `pip uninstall rt365-robotrader`. The build writes no state outside its working directory (audit journals are in-memory in dev/sim; nonce/revocation journals only where a path is configured).
