@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)
REM Встановлюємо PYTHONPATH для правильного імпорту модулів
set PYTHONPATH=%~dp0..
REM Запуск LCARS System через системний координатор
start "LCARS" %PYTHON_EXEC% system_launcher.py
