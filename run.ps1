# Windows PowerShell launcher.  Usage:
#   .\run.ps1 -Smoke                  # free pipeline test with reference scripts
#   .\run.ps1 -Limit 8                # cheap pilot: 8 real API attempts
#   .\run.ps1                         # full experiment (asks for the key, confirms cost)
#   .\run.ps1 -ReportOnly             # rebuild metrics/report from saved results
param([switch]$Smoke, [int]$Limit = 0, [switch]$ReportOnly, [switch]$Yes, [switch]$NoBuild)
$ErrorActionPreference = "Stop"
$Image = "blender-llm-bench"

if (-not $NoBuild) { docker build -t $Image . ; if ($LASTEXITCODE) { exit 1 } }

$argsList = @()
if ($Smoke) { $argsList += "--smoke" }
if ($Limit -gt 0) { $argsList += @("--limit", "$Limit") }
if ($ReportOnly) { $argsList += "--report-only" }
if ($Yes) { $argsList += "--yes" }

if (-not $Smoke -and -not $ReportOnly -and -not $env:AI_GATEWAY_API_KEY) {
    $sec = Read-Host "Paste your Vercel AI Gateway API key" -AsSecureString
    $env:AI_GATEWAY_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
}

New-Item -ItemType Directory -Force -Path "$PWD\results" | Out-Null
# -e NAME (without =value) passes the variable from this shell; the key never touches disk
docker run --rm -it -e AI_GATEWAY_API_KEY -v "${PWD}\results:/work/results" $Image @argsList
