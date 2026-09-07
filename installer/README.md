# installer/ — installation package and executables [Source: 16; ADR-016]

| Artefact | Produced by | Platform | Contents |
|---|---|---|---|
| `dist/rt365_robotrader-<version>-py3-none-any.whl`, `.tar.gz` (+ `.sha256`) | `make package` (`scripts/build_package.sh`) | any with Python 3.11+ | all packages, the `rt365` console script and the resource bundle (`rt365_cli/_bundle`) |
| `dist/bin/rt365` (+ `.sha256`) | `make exe` (`scripts/build_exe.sh`, PyInstaller spec `rt365.spec`) | the host OS (Linux/macOS) | one-file executable with the resource bundle |
| `dist/bin/rt365.exe` (+ `.sha256`) | `.github/workflows/release.yml` job `exe-windows` (windows-latest), or `make exe` on a Windows machine | Windows x64 | one-file executable with the resource bundle |
| `install.sh`, `install.ps1` | this directory | Linux/macOS, Windows | create a venv and install the wheel (or copy the `.exe` with `-Exe`), verify checksums, create a `rt365` launcher |

Every artefact carries the dev/sim posture: `rt365` refuses an unlabelled environment, serves only `--env sim`, refuses a missing or tampered signed registry and a fixture registry outside dev/sim (TC-PKG-001..004). The release workflow signs nothing yet: artefact signing (T-04) is an ARB decision [Open: O-23]; until then verify the SHA-256 files against the workflow run that produced them.

See docs/INSTALLATION.md for the step-by-step guide.
