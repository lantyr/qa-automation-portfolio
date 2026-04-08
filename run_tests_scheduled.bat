@echo off
REM For Windows Task Scheduler ONLY: no pause, no user input (avoids 0xC000013A).
setlocal EnableExtensions
chcp 65001 >nul 2>&1
cd /d "%~dp0"

set "LOG=%~dp0logs\last_run.log"
mkdir "%~dp0logs" 2>nul
echo ===== START %date% %time% =====>> "%LOG%"

if exist "%~dp0.venv\Scripts\python.exe" (
  set "PYEXE=%~dp0.venv\Scripts\python.exe"
) else (
  echo WARNING: .venv not found, using py.>> "%LOG%"
  set "PYEXE=py"
)

echo [1/4] pytest>> "%LOG%"
"%PYEXE%" -m pytest --clean-alluredir --alluredir=allure-results >> "%LOG%" 2>&1
if errorlevel 1 echo NOTE: pytest failures, continue>> "%LOG%"

echo [2/4] allure generate>> "%LOG%"
if not defined JAVA_HOME (
  for /d %%J in ("C:\Program Files\Microsoft\jdk-*") do set "JAVA_HOME=%%~J" & goto have_java
)
:have_java
if defined JAVA_HOME set "PATH=%JAVA_HOME%\bin;%PATH%"
call allure generate allure-results -o allure-report --clean >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERROR: allure generate failed>> "%LOG%"
  echo ===== END ERROR %date% %time% =====>> "%LOG%"
  exit /b 1
)

echo [3/4] allure-combine>> "%LOG%"
where allure-combine >nul 2>&1
if %ERRORLEVEL% equ 0 (
  call allure-combine allure-report >> "%LOG%" 2>&1
) else (
  "%PYEXE%" -m allure_combine allure-report >> "%LOG%" 2>&1
)

echo [4/4] send_report>> "%LOG%"
"%PYEXE%" send_report.py >> "%LOG%" 2>&1

echo ===== DONE %date% %time% =====>> "%LOG%"
endlocal
exit /b 0
