@echo off
setlocal
cd /d "%~dp0\..\.."

if "%1"=="--setup-startup" goto setup_startup

if exist ".venv\Scripts\python.exe" (
  set PYTHON_EXEC=.venv\Scripts\python.exe
) else (
  set PYTHON_EXEC=python
)

REM Launch LCARS through the unified launcher
start "LCARS Terminal" %PYTHON_EXEC% launcher.py full
exit /b

:setup_startup
echo [SYSTEM] Configuring LCARS Auto-Start...
set SCRIPT_PATH=%~dp0terminal.bat
set SHORTCUT_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\LCARS.lnk
powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%SHORTCUT_PATH%');$s.TargetPath='%SCRIPT_PATH%';$s.WorkingDirectory='%~dp0..\..';$s.Save()"
echo [SYSTEM] Shortcut created in Startup folder.
pause
exit /b
