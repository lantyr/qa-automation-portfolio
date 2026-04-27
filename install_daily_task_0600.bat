@echo off
REM Register Windows Task Scheduler: daily at 06:00, runs run_tests_scheduled.ps1 (no pause).
REM Run this BAT once as Administrator if "Access denied".

setlocal EnableExtensions
set "TASK_NAME=TestAutomation-Daily-0600"
set "PS1=%~dp0run_tests_scheduled.ps1"

if not exist "%PS1%" (
  echo ERROR: not found: %PS1%
  exit /b 1
)

echo Registering task "%TASK_NAME%" ...
echo Runner: PowerShell (avoids 0xC000013A from cmd closing too early)
echo Script: %PS1%
echo Schedule: every day at 06:00
echo.

REM Path contains spaces -> wrap PS1 with escaped quotes inside the /tr string.
schtasks /delete /tn "%TASK_NAME%" /f 2>nul
schtasks /create /tn "%TASK_NAME%" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%PS1%\"" /sc daily /st 06:00 /f
if errorlevel 1 (
  echo.
  echo Failed. Try: right-click this file -^> Run as administrator.
  exit /b 1
)

echo.
echo OK. Task "%TASK_NAME%" is registered.
echo To run only when logged in: open Task Scheduler -^> task properties -^> General.
echo To run after logout too: set "Run whether user is logged on or not" and save password.
pause
endlocal
