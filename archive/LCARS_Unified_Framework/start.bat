@echo off
title LCARS Unified Framework Launcher
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    LCARS UNIFIED FRAMEWORK                   ║
echo ║                 Select Platform to Launch                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:menu
echo [1] Unified Framework (Single Entry)
echo [2] Modules Demo (GUI)
echo [3] Toolkit Demo (Professional)
echo [4] Install Python Dependencies
echo [5] Build WPF Project
echo [6] Exit
echo.
set /p choice="Select option [1-6]: "

if "%choice%"=="1" goto unified
if "%choice%"=="2" goto modules_demo
if "%choice%"=="3" goto toolkit_demo
if "%choice%"=="4" goto install_python
if "%choice%"=="5" goto build_wpf
if "%choice%"=="6" goto exit
echo Invalid choice. Please try again.
goto menu

:unified
call run_unified.bat
goto menu

:modules_demo
echo [LCARS] Starting Modules Demo...
cd python
python modules_demo.py
cd ..
goto menu

:toolkit_demo
echo [LCARS] Starting Toolkit Demo (Professional)...
cd python
python toolkit_demo.py
cd ..
goto menu

:install_python
echo [LCARS] Installing Python dependencies...
cd python
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\pip.exe install -r requirements.txt
) else (
    python -m pip install -r requirements.txt
)
cd ..
echo [LCARS] Dependencies installed successfully!
pause
goto menu

:build_wpf
echo [LCARS] Building WPF project...
cd wpf
dotnet build LCARS.csproj --configuration Release
cd ..
echo [LCARS] Build completed!
pause
goto menu

:exit
echo [LCARS] Goodbye!
exit /b 0
