@echo off
title LCARS Klingon Learning
setlocal

cd /d "%~dp0\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Klingon Learning...
start "" %PYTHON_EXEC% "%~dp0klingon.py"
