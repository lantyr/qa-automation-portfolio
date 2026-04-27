@echo off
REM ASCII-only lines avoid cmd encoding issues. Task Scheduler: run_tests.bat nopause
setlocal EnableExtensions
chcp 65001 >nul 2>&1
cd /d "%~dp0"

REM Same as your Get-Command allure: npm global is under %APPDATA%\npm (allure.cmd).
REM Task Scheduler / cmd often have a short PATH; prepend so "call allure" works.
set "PATH=%APPDATA%\npm;%PATH%"
if exist "%ProgramFiles%\nodejs" set "PATH=%ProgramFiles%\nodejs;%PATH%"
if exist "%LOCALAPPDATA%\Programs\node" set "PATH=%LOCALAPPDATA%\Programs\node;%PATH%"

echo ===================================================
echo Daily automation: pytest + Allure + email
echo Task Scheduler: run_tests.bat nopause
echo ===================================================

if exist "%~dp0.venv\Scripts\python.exe" (
  set "PYEXE=%~dp0.venv\Scripts\python.exe"
) else (
  echo WARNING: .venv not found, using system py. Run setup_venv.bat first.
  set "PYEXE=py"
)

echo [1/6] pytest + allure-results...
REM 第一批：全部測試 + 純點帳 sidebar（--clean-alluredir 清空舊結果）
"%PYEXE%" -m pytest tests/test_pc_homepage.py tests/test_pc_customer_service.py tests/test_pc_navbar_states.py tests/test_openid_login.py "tests/test_pc_sidebar.py::TestPCMemberCenterPureSidebar" tests/test_pc_action_bar.py tests/test_pc_member_center.py tests/test_pc_topup_store.py -p no:cacheprovider --clean-alluredir --alluredir=allure-results --reruns 1 --reruns-delay 3
if errorlevel 1 (
  echo NOTE - first pytest had failures, continuing...
)
REM 第二批：星帳 sidebar（獨立 pytest 呼叫，讓 Chrome 資源完全釋放後再啟動）
"%PYEXE%" -m pytest "tests/test_pc_sidebar.py::TestPCMemberCenterStarSidebar" -p no:cacheprovider --alluredir=allure-results --reruns 1 --reruns-delay 3
if errorlevel 1 (
  echo NOTE - second pytest had failures, continuing with Allure and email steps
)

echo [2/6] merge prior Allure history into allure-results for trend widgets...
REM Copy allure-report\history to allure-results\history before generate.
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
  echo ERROR: allure generate failed. Install JDK and npm install -g allure-commandline
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
  echo WARNING: allure-combine failed. pip install allure-combine in venv.
)

echo [5/6] Archive complete.html to HistoryReports...
if not exist "%~dp0HistoryReports" mkdir "%~dp0HistoryReports"
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set "MY_DATE=%%i"
if exist "%~dp0allure-report\complete.html" (
  copy /Y "%~dp0allure-report\complete.html" "%~dp0HistoryReports\Report_%MY_DATE%.html" >nul
  echo Archived: %~dp0HistoryReports\Report_%MY_DATE%.html
) else (
  echo WARNING: complete.html missing. Fix step 4.
)

echo [6/6] send_report.py...
"%PYEXE%" send_report.py

echo ===================================================
echo Done. Folder: %CD%
echo ===================================================
if /i not "%~1"=="nopause" pause
endlocal
