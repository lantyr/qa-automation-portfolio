@echo off
REM Batch 2/3: sidebar + member_center
REM NO --clean-alluredir (accumulate results from batch 1). No report/email steps.
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
echo Batch 2/3: sidebar + member_center
echo ===================================================

"%PYEXE%" -m pytest tests/test_pc_sidebar.py tests/test_pc_member_center.py -p no:cacheprovider --alluredir=allure-results --reruns 1 --reruns-delay 3
if errorlevel 1 (
  echo NOTE - Batch 2 had failures, continuing...
)

echo ===================================================
echo Batch 2 done.
echo ===================================================
endlocal
