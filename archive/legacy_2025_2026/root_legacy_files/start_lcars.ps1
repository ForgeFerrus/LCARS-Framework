#!/usr/bin/env pwsh
# LCARS Framework PowerShell Launcher

# Set working directory to script location
Set-Location $PSScriptRoot

# Check for virtual environment
if (Test-Path ".venv\Scripts\python.exe") {
    $pythonExec = ".venv\Scripts\python.exe"
} else {
    $pythonExec = "python"
}

# Launch LCARS Framework
Write-Host "Запускаю LCARS Framework..." -ForegroundColor Green
& $pythonExec lcars/ui/main_launcher.py
