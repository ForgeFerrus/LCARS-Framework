@echo off
title LCARS Geant4 Wrapper
setlocal

cd /d "%~dp0\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Geant4 Wrapper...
start "" %PYTHON_EXEC% "%~dp0geant4_wrapper.py"
