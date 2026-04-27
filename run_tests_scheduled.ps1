# Scheduled task runner (no console pause). Log: logs\last_run.log
# Register: powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "...\run_tests_scheduled.ps1"
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $root

# Task Scheduler / non-interactive sessions often have a short PATH (no npm global).
# Interactive PowerShell may find "allure" while schtasks does not — same PC, different PATH.
$pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
$pathExtras = @(
    (Join-Path $env:APPDATA 'npm'),
    (Join-Path $env:LOCALAPPDATA 'Programs\node'),
    (Join-Path $env:ProgramFiles 'nodejs'),
    $(if ($pf86) { Join-Path $pf86 'nodejs' } else { $null })
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }
foreach ($d in $pathExtras) {
    if ($env:PATH -notlike "*$d*") {
        $env:PATH = "$d;$env:PATH"
    }
}

$logDir = Join-Path $root 'logs'
$logFile = Join-Path $logDir 'last_run.log'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Append-Log([string]$s) {
    Add-Content -LiteralPath $logFile -Value $s -Encoding UTF8
}

Append-Log "===== START $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====="

$py = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $py)) {
    Append-Log 'WARNING: .venv missing, using py'
    $py = 'py'
}

# [1/7] pytest 第一批：全部測試（純點帳 sidebar）
Append-Log '[1/7] pytest batch-1'
& $py -m pytest `
    tests/test_pc_homepage.py `
    tests/test_pc_customer_service.py `
    tests/test_pc_navbar_states.py `
    tests/test_openid_login.py `
    "tests/test_pc_sidebar.py::TestPCMemberCenterPureSidebar" `
    tests/test_pc_action_bar.py `
    tests/test_pc_member_center.py `
    tests/test_pc_topup_store.py `
    -p no:cacheprovider --clean-alluredir --alluredir=allure-results --reruns 1 --reruns-delay 3 `
    2>&1 | ForEach-Object { Append-Log $_ }
if ($LASTEXITCODE -ne 0) { Append-Log "NOTE: pytest batch-1 exit code $LASTEXITCODE (continue)" }

# [1b/7] pytest 第二批：星帳 sidebar（獨立呼叫讓 Chrome 資源釋放）
Append-Log '[1b/7] pytest batch-2 (star sidebar)'
& $py -m pytest `
    "tests/test_pc_sidebar.py::TestPCMemberCenterStarSidebar" `
    -p no:cacheprovider --alluredir=allure-results --reruns 1 --reruns-delay 3 `
    2>&1 | ForEach-Object { Append-Log $_ }
if ($LASTEXITCODE -ne 0) { Append-Log "NOTE: pytest batch-2 exit code $LASTEXITCODE (continue)" }

# [2/7] merge prior Allure history into allure-results for trend widgets
Append-Log '[2/7] merge Allure history'
$histSrc = Join-Path $root 'allure-report\history'
$histDst = Join-Path $root 'allure-results\history'
if (Test-Path -LiteralPath $histSrc) {
    New-Item -ItemType Directory -Force -Path $histDst | Out-Null
    Copy-Item -Path "$histSrc\*" -Destination $histDst -Recurse -Force -ErrorAction SilentlyContinue
    Append-Log 'OK: merged prior history'
} else {
    Append-Log 'NOTE: no previous allure-report\history folder'
}

# [2b/7] copy categories.json
$catSrc = Join-Path $root 'categories.json'
$catDst = Join-Path $root 'allure-results\categories.json'
if (Test-Path -LiteralPath $catSrc) {
    Copy-Item -LiteralPath $catSrc -Destination $catDst -Force
    Append-Log 'OK: copied categories.json'
}

# [3/7] allure generate
Append-Log '[3/7] allure generate'
if (-not $env:JAVA_HOME) {
    $jdk = Get-ChildItem 'C:\Program Files\Microsoft\jdk-*' -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($jdk) {
        $env:JAVA_HOME = $jdk.FullName
        $env:PATH = "$($jdk.FullName)\bin;$env:PATH"
    }
}
$allureCmd = Get-Command allure -ErrorAction SilentlyContinue
if (-not $allureCmd) {
    Append-Log 'ERROR: allure not in PATH (Task Scheduler often lacks npm global). Add npm folder to system PATH or install allure-commandline globally.'
    exit 1
}
& allure generate allure-results -o allure-report --clean 2>&1 | ForEach-Object { Append-Log $_ }
if ($LASTEXITCODE -ne 0) {
    Append-Log "ERROR: allure generate failed ($LASTEXITCODE)"
    exit 1
}

# [4/7] allure-combine
Append-Log '[4/7] allure-combine'
$reportDir = Join-Path $root 'allure-report'
$combineScript = Join-Path $root 'tools\run_allure_combine.py'
$combined = $false

$acExe = Join-Path $root '.venv\Scripts\allure-combine.exe'
if (Test-Path -LiteralPath $acExe) {
    & $acExe $reportDir 2>&1 | ForEach-Object { Append-Log $_ }
    if ($LASTEXITCODE -eq 0) { $combined = $true }
}
if (-not $combined) {
    $acExe2 = Join-Path $root '.venv\Scripts\ac.exe'
    if (Test-Path -LiteralPath $acExe2) {
        & $acExe2 $reportDir 2>&1 | ForEach-Object { Append-Log $_ }
        if ($LASTEXITCODE -eq 0) { $combined = $true }
    }
}
if (-not $combined) {
    $hasCombine = Get-Command allure-combine -ErrorAction SilentlyContinue
    if ($hasCombine) {
        & allure-combine $reportDir 2>&1 | ForEach-Object { Append-Log $_ }
        if ($LASTEXITCODE -eq 0) { $combined = $true }
    }
}
if (-not $combined -and (Test-Path -LiteralPath $combineScript)) {
    & $py $combineScript $reportDir 2>&1 | ForEach-Object { Append-Log $_ }
    if ($LASTEXITCODE -eq 0) { $combined = $true }
}
if (-not $combined) {
    Append-Log 'WARNING: allure-combine failed. pip install allure-combine in venv.'
}

# [5/7] Archive complete.html to HistoryReports
Append-Log '[5/7] archive complete.html'
$histReports = Join-Path $root 'HistoryReports'
New-Item -ItemType Directory -Force -Path $histReports | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$completeHtml = Join-Path $reportDir 'complete.html'
if (Test-Path -LiteralPath $completeHtml) {
    Copy-Item -LiteralPath $completeHtml -Destination (Join-Path $histReports "Report_$stamp.html") -Force
    Append-Log "Archived: HistoryReports\Report_$stamp.html"
} else {
    Append-Log 'WARNING: complete.html missing'
}

# [6/7] send_report
Append-Log '[6/7] send_report'
& $py send_report.py 2>&1 | ForEach-Object { Append-Log $_ }

Append-Log "===== DONE $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====="
exit 0
