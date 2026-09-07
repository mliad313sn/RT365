<#
.SYNOPSIS
  Install the rt365 dev/sim build on Windows.
.DESCRIPTION
  Two modes:
    -Exe   : copies the one-file rt365.exe from dist\bin (built by .github/workflows/release.yml or `make exe`
             on Windows) into $Target\bin and verifies its SHA-256.
    default: creates a virtual environment under $Target and installs the wheel from dist\ (or this checkout).
  Requires Python 3.11+ on PATH for the default mode. Nothing installed is authorised beyond the sim environment.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File installer\install.ps1
  powershell -ExecutionPolicy Bypass -File installer\install.ps1 -Exe
#>
param(
  [string]$Target = "$env:LOCALAPPDATA\rt365",
  [switch]$Exe
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
New-Item -ItemType Directory -Force -Path "$Target\bin" | Out-Null

if ($Exe) {
  $src = Join-Path $Root "dist\bin\rt365.exe"
  if (-not (Test-Path $src)) { throw "dist\bin\rt365.exe not found. Download it from the release assets or build it with: pyinstaller installer\rt365.spec" }
  $sumFile = "$src.sha256"
  if (Test-Path $sumFile) {
    $expected = ((Get-Content $sumFile) -split '\s+')[0].ToLower()
    $actual = (Get-FileHash -Algorithm SHA256 $src).Hash.ToLower()
    if ($expected -ne $actual) { throw "SHA-256 mismatch for rt365.exe: expected $expected, got $actual" }
    Write-Host "SHA-256 verified: $actual"
  }
  Copy-Item $src "$Target\bin\rt365.exe" -Force
} else {
  $py = Get-Command python -ErrorAction SilentlyContinue
  if (-not $py) { throw "python 3.11+ not found on PATH (or use -Exe with the prebuilt rt365.exe)" }
  & python -c "import sys; assert sys.version_info >= (3, 11), 'python >= 3.11 required'"
  & python -m venv "$Target\venv"
  & "$Target\venv\Scripts\python.exe" -m pip install --upgrade pip | Out-Null
  $wheel = Get-ChildItem (Join-Path $Root "dist") -Filter "rt365_robotrader-*.whl" -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($wheel) {
    & "$Target\venv\Scripts\python.exe" -m pip install $wheel.FullName
    $wrapper = "@echo off`r`n`"$Target\venv\Scripts\rt365.exe`" %*`r`n"
  } else {
    & "$Target\venv\Scripts\python.exe" -m pip install $Root
    $wrapper = "@echo off`r`nset RT365_HOME=$Root`r`n`"$Target\venv\Scripts\rt365.exe`" %*`r`n"
  }
  Set-Content -Path "$Target\bin\rt365.cmd" -Value $wrapper -Encoding ASCII
}
$cmd = if ($Exe) { "$Target\bin\rt365.exe" } else { "$Target\bin\rt365.cmd" }
& $cmd version
Write-Host ""
Write-Host "Installed to $Target. Add $Target\bin to PATH, then:"
Write-Host "  rt365 check --env sim      # verify signed registry, policies, planes, audit chain"
Write-Host "  rt365 serve --env sim      # dashboard on http://127.0.0.1:8080 (dev header auth, sim only)"
Write-Host "  rt365 mcp-serve --env sim  # MCP stdio tool server for an agent host (see .mcp.json)"
Write-Host "Nothing installed here is authorised beyond the sim environment (docs/MISSING_ACTIONS.md)."
