@echo off
title LCARS Project Explorer
setlocal

cd /d "%~dp0\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Project Explorer...
start "" %PYTHON_EXEC% "%~dp0project_explorer.py"
