@echo off
title LCARS Vocabulary
setlocal

cd /d "%~dp0\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Vocabulary...
start "" %PYTHON_EXEC% "%~dp0vocabulary.py"
