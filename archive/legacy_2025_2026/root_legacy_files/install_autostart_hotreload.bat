@echo off
REM LCARS OS Auto-Install to Windows Startup (Hot Reload Version)
REM Додає LCARS з hot reload в автозапуск Windows

echo Installing LCARS OS (Hot Reload) to Windows Startup...

set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "currentDir=%~dp0"

REM Створюємо батник в папці автозапуску
echo @echo off > "%startupFolder%\LCARS_OS_HotReload.bat"
echo cd /d "%currentDir%" >> "%startupFolder%\LCARS_OS_HotReload.bat"
echo python hot_reload_lcars.py >> "%startupFolder%\LCARS_OS_HotReload.bat"

echo.
echo LCARS OS (Hot Reload) додано в автозапуск Windows!
echo.
echo Тепер LCARS з hot reload запускатиметься автоматично при вході в систему.
echo.
echo Для видалення з автозапуску, видаліть файл:
echo %startupFolder%\LCARS_OS_HotReload.bat
echo.

pause
