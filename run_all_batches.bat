@echo off
REM Orchestrator: run all 3 batches with 15-minute gaps between each.
REM Usage: run_all_batches.bat [nopause]
REM If 15 min is not enough, increase WAIT_SECONDS below (1800=30min, 3600=1hr).
setlocal EnableExtensions
chcp 65001 >nul 2>&1
cd /d "%~dp0"

set "WAIT_SECONDS=900"

echo ===================================================
echo All-batch runner: 3 batches x 15-min gaps
echo ===================================================

echo [BATCH 1/3] Starting...
call "%~dp0run_batch1.bat" nopause
echo [BATCH 1/3] Done.

echo.
echo Waiting %WAIT_SECONDS% seconds before Batch 2 (429 cooldown)...
timeout /t %WAIT_SECONDS% /nobreak

echo.
echo [BATCH 2/3] Starting...
call "%~dp0run_batch2.bat" nopause
echo [BATCH 2/3] Done.

echo.
echo Waiting %WAIT_SECONDS% seconds before Batch 3 (429 cooldown)...
timeout /t %WAIT_SECONDS% /nobreak

echo.
echo [BATCH 3/3] Starting...
call "%~dp0run_batch3.bat" nopause
echo [BATCH 3/3] Done.

echo.
echo ===================================================
echo All batches finished.
echo ===================================================
if /i not "%~1"=="nopause" pause
endlocal
