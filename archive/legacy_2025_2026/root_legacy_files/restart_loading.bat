@echo off
echo Restarting LCARS Loading Screen...
echo.

REM Kill any existing Python processes running loading.py
taskkill /f /im python.exe /fi "WINDOWTITLE eq LCARS*" 2>nul
timeout /t 1 /nobreak >nul

REM Start the loading screen
cd /d "C:\Users\Forge\MyProject\LCARS-Framework"
python lcars\ui\loading.py

pause
