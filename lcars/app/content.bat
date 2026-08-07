@echo off
title LCARS Seed Content
setlocal

cd /d "%~dp0\..\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Seed Content...
start "" %PYTHON_EXEC% "%~dp0content.py"
