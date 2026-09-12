@echo off
chcp 65001 > nul
title Nova IDE Launcher
cd /d "%~dp0"
py programs/Nova/app.py
pause
