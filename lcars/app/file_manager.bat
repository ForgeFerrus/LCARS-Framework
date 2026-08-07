@echo off
title LCARS File Manager
setlocal

cd /d "%~dp0\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting File Manager...
start "" %PYTHON_EXEC% "%~dp0file_manager.py"
