<#
.SYNOPSIS
    Scheduled QA runner: tests → Allure → archive → email → Drive → Slack.
.DESCRIPTION
    Runs mobile (Selenium) and PC (Playwright + API) test suites, generates
    an Allure HTML report, archives it, then dispatches email/Slack notifications.
    Attach this script to Windows Task Scheduler for automated daily execution.
#>

$ErrorActionPreference = "Continue"
$Root      = Split-Path -Parent $MyInvocation.MyCommand.Path
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Results   = Join-Path $Root "allure-results"
$Report    = Join-Path $Root "allure-report"
$Archive   = Join-Path $Root "HistoryReports"

Set-Location $Root

# ── 1. Run tests ─────────────────────────────────────────────────────────────
Write-Host "`n=== [1/6] Mobile UI tests (Selenium) ===" -ForegroundColor Cyan
pytest mobile_pack/tests/ui -m "ui and mobile" --alluredir="$Results" -q

Write-Host "`n=== [2/6] PC UI tests (Playwright) ===" -ForegroundColor Cyan
pytest web_pack/tests/ui -m "ui and web" --alluredir="$Results" -q

Write-Host "`n=== [3/6] API tests (reqres.in) ===" -ForegroundColor Cyan
pytest web_pack/tests/api -m api --alluredir="$Results" -q

# ── 2. Merge Allure history ───────────────────────────────────────────────────
$HistorySrc  = Join-Path $Report  "history"
$HistoryDest = Join-Path $Results "history"
if (Test-Path $HistorySrc) {
    Write-Host "`n=== Merging Allure history ===" -ForegroundColor DarkCyan
    Copy-Item -Path $HistorySrc -Destination $HistoryDest -Recurse -Force
}

# ── 3. Generate Allure HTML report ───────────────────────────────────────────
Write-Host "`n=== [4/6] Generating Allure report ===" -ForegroundColor Cyan
allure generate "$Results" -o "$Report" --clean
python utils/report/patch_trend_dates.py

# ── 4. Archive report ────────────────────────────────────────────────────────
Write-Host "`n=== Archiving report ===" -ForegroundColor DarkCyan
New-Item -ItemType Directory -Force -Path $Archive | Out-Null
Copy-Item -Path $Report -Destination (Join-Path $Archive "report-$Timestamp") -Recurse -Force

# ── 5. Send email + upload to Drive ──────────────────────────────────────────
Write-Host "`n=== [5/6] Sending report (email + Drive) ===" -ForegroundColor Cyan
python utils/report/send_report.py

# ── 6. Done ──────────────────────────────────────────────────────────────────
Write-Host "`n=== [6/6] All done — $Timestamp ===" -ForegroundColor Green
