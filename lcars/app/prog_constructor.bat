@echo off
title LCARS Constructor
setlocal

cd /d "%~dp0\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Constructor...
start "" %PYTHON_EXEC% "%~dp0constructor.py"
