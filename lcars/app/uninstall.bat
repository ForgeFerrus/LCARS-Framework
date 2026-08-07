@echo off
REM LCARS Framework Uninstallation Script
REM ======================================
REM Видалення LCARS Framework

setlocal
cd /d "%~dp0"

echo [LCARS] Uninstallation
echo =====================
echo.

REM Remove desktop shortcut
echo [1/3] Removing desktop shortcut...
if exist "%USERPROFILE%\Desktop\LCARS.lnk" (
    del "%USERPROFILE%\Desktop\LCARS.lnk"
    echo Desktop shortcut removed.
) else (
    echo No desktop shortcut found.
)

REM Deactivate if running in venv
echo [2/3] Deactivating virtual environment...
if defined VIRTUAL_ENV (
    call deactivate
)

echo [3/3] Cleanup information...
echo.
echo To completely remove LCARS Framework:
echo   - Delete this directory: %CD%
echo   - Delete virtual environment: %CD%\.venv
echo.
echo Uninstall complete.
echo.
pause