@echo off
title LCARS Designer
setlocal

cd /d "%~dp0\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting LCARS Designer...
start "" %PYTHON_EXEC% -m lcars.tools.designer
