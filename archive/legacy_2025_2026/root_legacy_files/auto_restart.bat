@echo off
echo Auto-restart LCARS Loading Screen on changes...
echo Press Ctrl+C to stop
echo.

cd /d "C:\Users\Forge\MyProject\LCARS-Framework"

:loop
echo Starting LCARS Loading Screen...
python lcars\ui\loading.py
echo.
echo Program closed. Restarting in 2 seconds...
timeout /t 2 /nobreak >nul
goto loop
