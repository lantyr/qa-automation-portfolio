@echo off
REM Batch 1/3: homepage + customer_service + navbar_states + openid_login
REM Uses --clean-alluredir to start fresh. No report/email steps.
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
echo Batch 1/3: homepage + cs + navbar + openid_login
echo ===================================================

"%PYEXE%" -m pytest tests/test_pc_homepage.py tests/test_pc_customer_service.py tests/test_pc_navbar_states.py tests/test_openid_login.py -p no:cacheprovider --clean-alluredir --alluredir=allure-results --reruns 1 --reruns-delay 3
if errorlevel 1 (
  echo NOTE - Batch 1 had failures, continuing...
)

echo ===================================================
echo Batch 1 done.
echo ===================================================
endlocal
