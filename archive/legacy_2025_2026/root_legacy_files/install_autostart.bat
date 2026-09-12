@echo off
REM LCARS OS Auto-Install to Windows Startup
REM Додає LCARS в автозапуск Windows

echo Installing LCARS OS to Windows Startup...

set "startupFolder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "currentDir=%~dp0"

REM Створюємо батник в папці автозапуску
echo @echo off > "%startupFolder%\LCARS_OS.bat"
echo cd /d "%currentDir%" >> "%startupFolder%\LCARS_OS.bat"
echo python start.py >> "%startupFolder%\LCARS_OS.bat"

echo.
echo LCARS OS додано в автозапуск Windows!
echo.
echo Тепер LCARS запускатиметься автоматично при вході в систему.
echo.
echo Для видалення з автозапуску, видаліть файл:
echo %startupFolder%\LCARS_OS.bat
echo.

pause