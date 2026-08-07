@echo off
REM LCARS Framework Build Script
REM ============================
REM Windows build system

setlocal
cd /d "%~dp0"

if "%1"=="" goto help
if "%1"=="clean" goto clean
if "%1"=="setup" goto setup
if "%1"=="install" goto install
if "%1"=="build" goto build
if "%1"=="test" goto test
if "%1"=="run" goto run
if "%1"=="package" goto package
if "%1"=="status" goto status
goto help

:clean
echo [BUILD] Cleaning build directories...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
echo Clean completed.
goto end

:setup
echo [BUILD] Setting up virtual environment...
if exist .venv (
    echo Virtual environment already exists.
) else (
    python -m venv .venv
    echo Virtual environment created.
)
goto end

:install
echo [BUILD] Installing dependencies...
if not exist .venv (
    echo Creating virtual environment first...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if "%2"=="--dev" (
    pip install -e ".[dev]"
) else (
    pip install -e .
)
echo Installation completed.
goto end

:build
echo [BUILD] Building project...
call .venv\Scripts\activate.bat
python -m pip install --upgrade build setuptools wheel
python -m build
echo Build completed. Output in dist/
goto end

:test
echo [BUILD] Running tests...
call .venv\Scripts\activate.bat
if exist test (
    python -m pytest test/ -v
) else (
    echo No tests directory found.
)
goto end

:run
echo [BUILD] Running LCARS Framework...
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python launcher.py
) else (
    python launcher.py
)
goto end

:package
echo [BUILD] Creating distribution package...
call :build
echo Distribution package created in dist/
goto end

:status
echo [BUILD] System Status
echo ====================
echo.
echo Python Version:
python --version
echo.
echo Virtual Environment:
if exist .venv (
    echo [OK] .venv exists
) else (
    echo [MISSING] .venv not found
)
echo.
echo Build Directories:
if exist build (
    echo [OK] build/ exists
) else (
    echo [CLEAN] build/ not found
)
if exist dist (
    echo [OK] dist/ exists
) else (
    echo [CLEAN] dist/ not found
)
echo.
echo Key Files:
if exist setup.py (
    echo [OK] setup.py
) else (
    echo [MISSING] setup.py
)
if exist pyproject.toml (
    echo [OK] pyproject.toml
) else (
    echo [MISSING] pyproject.toml
)
if exist launcher.py (
    echo [OK] launcher.py
) else (
    echo [MISSING] launcher.py
)
goto end

:help
echo LCARS Framework Build System
echo ============================
echo.
echo Usage: build.bat [command] [options]
echo.
echo Commands:
echo   clean     - Clean build directories
echo   setup     - Create virtual environment
echo   install   - Install dependencies
echo   install --dev - Install with dev dependencies
echo   build     - Build project
echo   test      - Run tests
echo   run       - Run LCARS Framework
echo   package   - Create distribution package
echo   status    - Show system status
echo.
echo Quick Start:
echo   1. build.bat setup      - Create environment
echo   2. build.bat install    - Install dependencies
echo   3. build.bat run         - Run LCARS
echo.
echo Or just run: install.bat (automated installation)
echo.
goto end

:end
pause