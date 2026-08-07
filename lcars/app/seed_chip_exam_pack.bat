@echo off
title LCARS Seed Chip Exam Pack
setlocal

cd /d "%~dp0\..\..\.."

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

echo [LAUNCH] Starting Seed Chip Exam Pack...
start "" %PYTHON_EXEC% "%~dp0seed_chip_exam_pack.py"
