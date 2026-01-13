@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)
REM Встановлюємо PYTHONPATH для правильного імпорту модулів
set PYTHONPATH=%~dp0..
REM Запуск LCARS без консолі через launcher.py (графічний режим)
start "LCARS" %PYTHON_EXEC% full_theme_demo.py
