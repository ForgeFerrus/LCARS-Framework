@echo off
title LCARS Build B1 Chip
setlocal

cd /d "%~dp0\..\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Build B1 Chip...
start "" %PYTHON_EXEC% "%~dp0buildB1Chip.py"
