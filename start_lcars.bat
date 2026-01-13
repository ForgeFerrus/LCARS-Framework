@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)
REM Запуск єдиної консолідованої системи LCARS
start "LCARS" %PYTHON_EXEC% start.py
