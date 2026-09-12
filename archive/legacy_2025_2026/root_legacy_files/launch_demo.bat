@echo off
setlocal
cd /d "%~dp0"

echo [LCARS] Launching Standalone Demo...
echo.

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
  echo [LCARS] Using virtual environment Python
) else (
  set PYTHON_EXEC=python
  echo [LCARS] Using system Python
)

echo [LCARS] Starting demo...
%PYTHON_EXEC% standalone_demo.py

if errorlevel 1 (
  echo.
  echo [ERROR] Demo failed to start. Check Python installation.
  pause
)
