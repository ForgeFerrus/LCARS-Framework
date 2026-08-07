@echo off
title LCARS Avast Interface
setlocal

cd /d "%~dp0\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Avast Interface...
start "" %PYTHON_EXEC% "%~dp0interface.py"
