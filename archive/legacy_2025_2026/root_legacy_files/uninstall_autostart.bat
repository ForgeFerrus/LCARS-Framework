@echo off
REM LCARS OS Auto-Uninstall from Windows Startup
REM Видаляє LCARS з автозапуску Windows

echo Removing LCARS OS from Windows Startup...

set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "autostartFile=%startupFolder%\LCARS_OS.bat"

if exist "%autostartFile%" (
    del "%autostartFile%"
    echo.
    echo LCARS OS видалено з автозапуску Windows!
    echo.
    echo Файл видалено: %autostartFile%
) else (
    echo.
    echo LCARS OS не знайдено в автозапуску Windows.
    echo.
    echo Файл не існує: %autostartFile%
)

echo.
pause
