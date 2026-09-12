@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)
REM Запуск LCARS без консолі через launcher.py (графічний режим)
start "LCARS" %PYTHON_EXEC% PCARS_23rd.py