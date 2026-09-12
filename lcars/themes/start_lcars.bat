@echo off
cd /d "%~dp0"
cd ..\..
if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)
REM Запуск LCARS без консолі через launcher.py (графічний режим)
start "LCARS" %PYTHON_EXEC% lcars\themes\theme_demo.py
