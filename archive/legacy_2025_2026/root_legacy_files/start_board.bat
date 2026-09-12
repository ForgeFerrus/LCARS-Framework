@echo off
title LCARS PyQt6 Repair

echo ========================================
echo LCARS PYQT6 REPAIR
echo ========================================

call .venv\Scripts\activate.bat

echo.
echo Removing broken PyQt packages...
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-WebEngine PyQt6-WebEngine-Qt6 PyQt6_sip

echo.
echo Cleaning leftovers...
rmdir /s /q .venv\Lib\site-packages\PyQt6 2>nul

for /d %%i in (.venv\Lib\site-packages\PyQt6*) do (
    rmdir /s /q "%%i" 2>nul
)

echo.
echo Installing fresh build for Python 3.14...
pip install --no-cache-dir PyQt6 PyQt6-WebEngine

echo.
echo Testing...
python -c "from PyQt6.QtWidgets import QApplication; print('PYQT6_OK')"

echo.
echo Finished.
pause