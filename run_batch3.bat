@echo off
REM Batch 3/3: action_bar + topup_store
REM NO --clean-alluredir (accumulate results from batches 1+2).
REM Runs full Allure generate + combine + archive + email after tests.
setlocal EnableExtensions
chcp 65001 >nul 2>&1
cd /d "%~dp0"

set "PATH=%APPDATA%\npm;%PATH%"
if exist "%ProgramFiles%\nodejs" set "PATH=%ProgramFiles%\nodejs;%PATH%"
if exist "%LOCALAPPDATA%\Programs\node" set "PATH=%LOCALAPPDATA%\Programs\node;%PATH%"

if exist "%~dp0.venv\Scripts\python.exe" (
  set "PYEXE=%~dp0.venv\Scripts\python.exe"
) else (
  set "PYEXE=py"
)

echo ===================================================
echo Batch 3/3: action_bar + topup_store
echo ===================================================

"%PYEXE%" -m pytest tests/test_pc_action_bar.py tests/test_pc_topup_store.py -p no:cacheprovider --alluredir=allure-results --reruns 1 --reruns-delay 3
if errorlevel 1 (
  echo NOTE - Batch 3 had failures, continuing with Allure and email steps
)

echo [2/6] merge prior Allure history into allure-results for trend widgets...
if exist "%~dp0allure-report\history" (
  if not exist "%~dp0allure-results\history" mkdir "%~dp0allure-results\history"
  xcopy /E /I /Y "%~dp0allure-report\history\*" "%~dp0allure-results\history\" >nul 2>&1
  if errorlevel 1 (
    echo WARNING: copy history failed
  ) else (
    echo OK: merged prior history
  )
) else (
  echo NOTE: no previous allure-report\history folder.
)

echo [2b/6] copy categories.json for Allure blocked category...
if exist "%~dp0categories.json" copy /Y "%~dp0categories.json" "%~dp0allure-results\categories.json" >nul

echo [3/6] allure generate...
if not defined JAVA_HOME (
  for /d %%J in ("C:\Program Files\Microsoft\jdk-*") do set "JAVA_HOME=%%~J" & goto have_java
)
:have_java
if defined JAVA_HOME set "PATH=%JAVA_HOME%\bin;%PATH%"
call allure generate allure-results -o allure-report --clean
if errorlevel 1 (
  echo ERROR: allure generate failed.
  if /i not "%~1"=="nopause" pause
  exit /b 1
)

echo [4/6] allure-combine - build complete.html...
set "ALLURE_REP=%~dp0allure-report"
set "COMBINED=0"

if exist "%~dp0.venv\Scripts\allure-combine.exe" (
  call "%~dp0.venv\Scripts\allure-combine.exe" "%ALLURE_REP%"
  if not errorlevel 1 set "COMBINED=1"
)
if "%COMBINED%"=="0" if exist "%~dp0.venv\Scripts\ac.exe" (
  call "%~dp0.venv\Scripts\ac.exe" "%ALLURE_REP%"
  if not errorlevel 1 set "COMBINED=1"
)
if "%COMBINED%"=="0" (
  where allure-combine >nul 2>&1
  if not errorlevel 1 (
    call allure-combine "%ALLURE_REP%"
    if not errorlevel 1 set "COMBINED=1"
  )
)
if "%COMBINED%"=="0" (
  where ac >nul 2>&1
  if not errorlevel 1 (
    call ac "%ALLURE_REP%"
    if not errorlevel 1 set "COMBINED=1"
  )
)
if "%COMBINED%"=="0" (
  echo Fallback: tools\run_allure_combine.py
  "%PYEXE%" "%~dp0tools\run_allure_combine.py" "%ALLURE_REP%"
  if not errorlevel 1 set "COMBINED=1"
)
if "%COMBINED%"=="0" (
  echo WARNING: allure-combine failed.
)

echo [5/6] Archive complete.html to HistoryReports...
if not exist "%~dp0HistoryReports" mkdir "%~dp0HistoryReports"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set "MY_DATE=%%i"
if exist "%~dp0allure-report\complete.html" (
  copy /Y "%~dp0allure-report\complete.html" "%~dp0HistoryReports\Report_%MY_DATE%.html" >nul
  echo Archived: %~dp0HistoryReports\Report_%MY_DATE%.html
) else (
  echo WARNING: complete.html missing.
)

echo [6/6] send_report.py...
"%PYEXE%" send_report.py

echo ===================================================
echo All 3 batches complete. Folder: %CD%
echo ===================================================
if /i not "%~1"=="nopause" pause
endlocal
