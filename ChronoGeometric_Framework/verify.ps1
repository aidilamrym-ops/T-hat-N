# Verification entry point for the Chrono-Geometric Framework (Windows / PowerShell).
#
# Runs the two checks this subproject can actually make:
#   1. `lake build`  -- every Lean module compiles with no sorry/admit/unsafe;
#   2. the enclosure consistency suite -- the Lean constants still mirror
#      lean/enclosures/*.json and the recorded derivative enclosure recomputes.
#
# It does NOT run the external anti-circularity skill script (`gate.py`), which
# lives outside this repository and is invoked from the T-hat-N root instead.
#
# Usage:  pwsh -File verify.ps1     (or: powershell -File verify.ps1)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

Write-Host "== lake build =="
lake build
if ($LASTEXITCODE -ne 0) { throw "lake build failed with exit code $LASTEXITCODE" }

Write-Host "== enclosure consistency =="
python -m pytest python/test_enclosure_consistency.py -q
if ($LASTEXITCODE -ne 0) { throw "enclosure consistency suite failed with exit code $LASTEXITCODE" }

# A placeholder scan over the Lean sources: `Shape` has no payload, so a
# `sorry` here would be invisible in the build log otherwise.
$forbidden = Select-String -Path lean/*.lean -Pattern '\b(sorry|admit|unsafe)\b'
if ($forbidden) {
    $forbidden | ForEach-Object { Write-Host $_ }
    throw "forbidden placeholder token in lean/*.lean"
}

Write-Host "verify: PASS"
