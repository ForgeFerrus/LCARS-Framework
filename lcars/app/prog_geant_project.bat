@echo off
title LCARS Geant Project
setlocal

cd /d "%~dp0\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Geant Project...
start "" %PYTHON_EXEC% "%~dp0geant_project.py"
