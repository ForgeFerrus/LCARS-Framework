@echo off
title LCARS Task Manager
setlocal

cd /d "%~dp0\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Task Manager...
start "" %PYTHON_EXEC% "%~dp0TaskManager.py"
