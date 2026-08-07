@echo off
title LCARS Maps
setlocal

cd /d "%~dp0\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Maps...
start "" %PYTHON_EXEC% "%~dp0maps.py"
