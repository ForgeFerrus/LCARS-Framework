@echo off
REM LCARS OS Auto-Start
REM Запускає LCARS операційну систему

cd /d "%~dp0"

REM Запускаємо LCARS OS через lock screen
python start_lcars.py

REM Якщо Python не знайдено, спробуємо py
if errorlevel 1 (
    py loading.py
)

REM Якщо і це не спрацювало, показуємо помилку
if errorlevel 1 (
    echo ERROR: Python not found or LCARS failed to start
    echo Please check Python installation
    pause
)