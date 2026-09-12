@echo off
title LCARS Unified Framework - Single Entry Point
cd /d "%~dp0python"

echo [LCARS] Unified Framework - Single Entry Point
echo.

if exist ".venv\Scripts\python.exe" (
    echo [LCARS] Using virtual environment...
    set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
    echo [LCARS] Using system Python...
    set PYTHON_EXEC=python
)

echo [LCARS] Starting LCARS framework...
%PYTHON_EXEC% -c "import lcars; print('LCARS Framework ready!')"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start unified LCARS
    echo [INFO] Make sure dependencies are installed:
    echo [INFO] pip install PyQt6
    pause
)
