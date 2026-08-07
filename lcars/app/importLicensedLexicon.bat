@echo off
title LCARS Seed Licensed Lexicon
setlocal

cd /d "%~dp0\..\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Seed Licensed Lexicon...
start "" %PYTHON_EXEC% "%~dp0importLicensedLexicon.py"
