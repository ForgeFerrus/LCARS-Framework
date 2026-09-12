@echo off
title LCARS ISOLINEAR ARCHITECT
setlocal

cd /d "%~dp0"

echo [SYSTEM] Initializing Isolinear Substrate...
if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Architect via unified launcher...
%PYTHON_EXEC% launcher.py designer

if %ERRORLEVEL% NEQ 0 (
    echo [CRITICAL] System crash detected.
    pause
)
