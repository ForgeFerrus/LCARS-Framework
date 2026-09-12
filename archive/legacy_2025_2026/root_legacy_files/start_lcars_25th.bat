@echo off
cd /d "%~dp0"
echo Starting LCARS 25th Century Interface...
echo.
echo Sequential workflow:
echo 1. Start Screen
echo 2. Faction Selection  
echo 3. Era Selection
echo 4. Palette Demonstration
echo.
python lcars/ui/lcars_interface_25th.py
pause