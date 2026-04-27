@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ===================================================
echo Create/update .venv and pip install -r requirements.txt
echo ===================================================

if not exist ".venv\Scripts\python.exe" (
  echo [1/2] Creating .venv ...
  py -m venv .venv
  if errorlevel 1 (
    echo FAILED: Install Python and ensure "py" launcher works.
    pause
    exit /b 1
  )
) else (
  echo [1/2] .venv already exists, skip create.
)

echo [2/2] pip install -r requirements.txt ...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  pause
  exit /b 1
)

echo.
echo OK. Next: run run_tests.bat
echo ===================================================
pause
endlocal
