@echo off
REM Convert all Qt Designer .ui files to Python
REM Usage: convert_ui.bat

setlocal enabledelayedexpansion

echo.
echo ===== Converting Qt Designer UI files to Python =====
echo.

cd /d "%~dp0"

REM Find all .ui files in current directory and subdirectories
for /R . %%F in (*.ui) do (
    set "ui_file=%%F"
    set "py_file=!ui_file:.ui=.py!"
    
    echo Converting: !ui_file!
    echo To:         !py_file!
    
    pyuic6 -o "!py_file!" "!ui_file!"
    
    if errorlevel 1 (
        echo ERROR: Failed to convert !ui_file!
    ) else (
        echo SUCCESS
    )
    echo.
)

echo.
echo ===== Conversion Complete =====
echo.
pause
