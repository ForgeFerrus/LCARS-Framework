@echo off
echo ========================================
echo LCARS Framework - Comprehensive Demo
echo ========================================
echo.
echo Starting LCARS Demo Launcher...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "lcars_demo.py" (
    echo ERROR: lcars_demo.py not found
    echo Please run this script from the demo directory
    pause
    exit /b 1
)

REM Check if LCARS modules are available
python -c "import lcars.themes.theme" >nul 2>&1
if errorlevel 1 (
    echo WARNING: LCARS modules not found
    echo Make sure you're running this from the LCARS-Framework root directory
    echo or that LCARS Framework is properly installed
    echo.
)

echo Launching demo...
echo.
python lcars_demo.py

if errorlevel 1 (
    echo.
    echo ERROR: Demo failed to start
    echo Check the error message above for details
    pause
) else (
    echo.
    echo Demo closed successfully
)

pause
