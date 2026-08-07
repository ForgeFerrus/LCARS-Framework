@echo off
title LCARS Keyboard
setlocal

cd /d "%~dp0\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting LCARS Keyboard...
start "" %PYTHON_EXEC% -m lcars.tools.keyboard
