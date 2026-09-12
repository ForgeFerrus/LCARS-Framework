@echo off
chcp 65001 > nul
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" terminal.py %*
) else if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" terminal.py %*
) else (
    start "" pythonw terminal.py %*
)
exit
