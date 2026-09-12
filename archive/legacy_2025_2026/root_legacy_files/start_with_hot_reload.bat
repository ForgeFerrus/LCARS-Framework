@echo off
echo 🔥 LCARS Hot Reload Launcher
echo ========================
echo 📝 Зміни в коді автоматично перезапустять систему
echo ⌨️  Натисніть Ctrl+C для зупинки
echo.

cd /d "%~dp0"

python hot_reload_lcars.py

pause
