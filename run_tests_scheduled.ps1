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

Append-Log '[1/4] pytest'
& $py -m pytest --clean-alluredir --alluredir=allure-results 2>&1 | ForEach-Object { Append-Log $_ }
if ($LASTEXITCODE -ne 0) { Append-Log "NOTE: pytest exit code $LASTEXITCODE (continue)" }

if (-not $env:JAVA_HOME) {
    $jdk = Get-ChildItem 'C:\Program Files\Microsoft\jdk-*' -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($jdk) {
        $env:JAVA_HOME = $jdk.FullName
        $env:PATH = "$($jdk.FullName)\bin;$env:PATH"
    }
}

Append-Log '[2/4] allure generate'
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

Append-Log '[3/4] allure-combine'
$reportDir = Join-Path $root 'allure-report'
$combineScript = Join-Path $root 'tools\run_allure_combine.py'
$hasCombine = Get-Command allure-combine -ErrorAction SilentlyContinue
if ($hasCombine) {
    & allure-combine $reportDir 2>&1 | ForEach-Object { Append-Log $_ }
} elseif (Test-Path -LiteralPath $combineScript) {
    & $py $combineScript $reportDir 2>&1 | ForEach-Object { Append-Log $_ }
} else {
    Append-Log 'ERROR: allure-combine not found and tools\run_allure_combine.py missing'
    exit 1
}

Append-Log '[4/4] send_report'
& $py send_report.py 2>&1 | ForEach-Object { Append-Log $_ }

Append-Log "===== DONE $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====="
exit 0
