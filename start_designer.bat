@echo off
title LCARS Engineering Studio Runner
setlocal

:: Переходимо в папку, де лежить сам BAT-файл
cd /d "%~dp0"

echo [SYSTEM] Starting LCARS Environment...
echo [PATH] %cd%

:: 1. Перевірка наявності Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH!
    pause
    exit /b
)

:: 2. Активація .venv (якщо використовуєте)
if exist .venv\Scripts\activate.bat (
    echo [VENV] Activating virtual environment...
    call .venv\Scripts\activate.bat
)

:: 3. Запуск основного конструктора
echo [EXEC] Launching Constructor.py...
python Constructor.py

:: 4. Якщо програма вилетить, консоль не закриється (щоб прочитати помилку)
if %errorlevel% neq 0 (
    echo.
    echo [CRITICAL] Application crashed with exit code %errorlevel%
    pause
)

endlocal