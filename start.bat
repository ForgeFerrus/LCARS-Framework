@echo off
chcp 65001 > nul
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" start_lcars.py %*
) else if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" start_lcars.py %*
) else (
    start "" pythonw start_lcars.py %*
)
exit
