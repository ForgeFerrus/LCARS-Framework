@echo off
REM LCARS Framework Quick Start
REM ============================
REM Швидкий запуск LCARS Framework

setlocal
cd /d "%~dp0"

REM Check if venv exists
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
    set PYTHON_EXEC=python
)

REM Check if launcher exists
if not exist "launcher.py" (
    echo [ERROR] launcher.py not found!
    echo Please run this script from the LCARS Framework root directory.
    pause
    exit /b 1
)

REM Run LCARS
echo [LCARS] Starting LCARS Framework...
echo Using Python: %PYTHON_EXEC%
echo.

%PYTHON_EXEC% launcher.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to start LCARS
    echo.
    echo Possible solutions:
    echo   1. Run install.bat to set up the environment
    echo   2. Run build.bat install to install dependencies
    echo   3. Check Python installation (requires Python 3.8+)
    echo.
    pause
    exit /b 1
)