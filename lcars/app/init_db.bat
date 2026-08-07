@echo off
title LCARS Seed Init DB
setlocal

cd /d "%~dp0\..\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Seed Init DB...
start "" %PYTHON_EXEC% "%~dp0init_db.py"
