@echo off
REM LCARS Framework - Quick Health Check
REM Перевіряє встановлення та готовність до роботи

title LCARS Framework - Health Check

cls
echo.
echo ================================
echo |  LCARS Framework - Health Check  |
echo |  System Diagnostics              |
echo ================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python NOT installed
    goto :error
) else (
    for /f "tokens=*" %%i in ('python --version') do echo ✓ %%i
)

echo.

REM Check PyQt6
echo [2/5] Checking PyQt6...
python -c "import PyQt6; print('✓ PyQt6 installed')" 2>nul
if errorlevel 1 (
    echo ✗ PyQt6 NOT installed
    echo    Run: pip install PyQt6
) else (
    for /f "tokens=*" %%i in ('python -c "import PyQt6; print('✓ PyQt6 installed')"') do echo %%i
)

echo.

REM Check LCARS Framework
echo [3/5] Checking LCARS Framework...
python -c "from lcars.core.environment import EnvironmentManager; print('✓ LCARS Framework OK')" 2>nul
if errorlevel 1 (
    echo ✗ LCARS Framework NOT accessible
) else (
    for /f "tokens=*" %%i in ('python -c "from lcars.core.environment import EnvironmentManager; print('✓ LCARS Framework OK')"') do echo %%i
)

echo.

REM Check Geant4
echo [4/5] Checking Geant4...
python -c "from lcars.core.environment import EnvironmentManager; e=EnvironmentManager(); s=e.get_status(); print('✓ Geant4 Detected' if s['geant4_detected'] else '⚠ Geant4 NOT found')" 2>nul
if errorlevel 1 (
    echo ⚠ Could not check Geant4
) else (
    for /f "tokens=*" %%i in ('python -c "from lcars.core.environment import EnvironmentManager; e=EnvironmentManager(); s=e.get_status(); print('✓ Geant4 Detected' if s['geant4_detected'] else '⚠ Geant4 NOT found')"') do echo %%i
)

echo.

REM Check Projects
echo [5/5] Checking Projects...
python -c "from lcars.core.project_manager import ProjectManager; from pathlib import Path; pm=ProjectManager(Path('.')); print(f'✓ Found {len(pm.projects)} projects')" 2>nul
if errorlevel 1 (
    echo ⚠ Could not discover projects
) else (
    for /f "tokens=*" %%i in ('python -c "from lcars.core.project_manager import ProjectManager; from pathlib import Path; pm=ProjectManager(Path('.')); print(f'✓ Found {len(pm.projects)} projects')"') do echo %%i
)

echo.
echo ================================

REM Summary
echo Health check complete!
echo You can now run: python run.py
echo.

goto :end

:error
echo.
echo ================================
echo ERRORS DETECTED
echo.
echo Please install Python from:
echo   https://www.python.org/
echo.
echo Then run:
echo   pip install -r requirements.txt
echo.

:end
pause
