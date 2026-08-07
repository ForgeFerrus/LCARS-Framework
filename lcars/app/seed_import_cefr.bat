@echo off
title LCARS Seed Import CEFR
setlocal

cd /d "%~dp0\..\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Seed Import CEFR...
start "" %PYTHON_EXEC% "%~dp0import_cefr.py"
