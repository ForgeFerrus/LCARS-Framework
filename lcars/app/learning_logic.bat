@echo off
title LCARS Learning Logic
setlocal

cd /d "%~dp0\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Learning Logic...
start "" %PYTHON_EXEC% "%~dp0logic.py"
