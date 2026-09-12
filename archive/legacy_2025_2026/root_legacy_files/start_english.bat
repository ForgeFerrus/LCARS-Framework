@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" programs\learning\English.py %*
) else (
    python programs\learning\English.py %*
)

endlocal
