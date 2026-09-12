@echo off
chcp 65001 > nul
title LCARS SCIENCE WORKSPACE // MULTI-STATION HUB
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" lcars/ui/workbench.py %*
) else (
    python lcars/ui/workbench.py %*
)
pause
