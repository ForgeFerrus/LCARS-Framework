@echo off
REM LCARS Framework Installation Script
REM =====================================
REM Простий інсталятор для Windows

setlocal
cd /d "%~dp0"

echo [LCARS] Installation System
echo ============================
echo.

REM Check Python
python --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo [4/5] Installing LCARS Framework...
pip install -e .
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    echo Trying alternative installation method...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install from requirements.txt
        pause
        exit /b 1
    )
)

echo [5/5] Creating desktop shortcut...
powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\LCARS.lnk');$s.TargetPath='%CD%\.venv\Scripts\python.exe';$s.Arguments='%CD%\launcher.py';$s.WorkingDirectory='%CD%';$s.Save()"
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to create desktop shortcut (requires admin permissions)
)

echo.
echo [SUCCESS] LCARS Framework installed successfully!
echo.
echo To start LCARS:
echo   - Double-click LCARS.lnk on desktop (if created)
echo   - Or run: start.bat
echo   - Or run: .venv\Scripts\python launcher.py
echo.
pause