@echo off
setlocal EnableExtensions

set "ROOT=%~dp0.."
set "PYEXE=%ROOT%\.venv\Scripts\python.exe"

if not "%~1"=="" goto run_args

echo LCARS AI model diagnostics
echo.
echo 1. Full matrix
echo 2. Local backends ^(hf_local + gemma^)
echo 3. hf_local only
echo 4. gemma only
echo 5. Remote backends ^(groqwen + mistral^)
echo 6. Custom backend
echo 7. Single model
echo 0. Exit
echo.
choice /c 12345670 /n /m "Select:"
set "SEL=%errorlevel%"

if "%SEL%"=="8" exit /b 0
if "%SEL%"=="1" set "ARGS=--full"
if "%SEL%"=="2" set "ARGS=--backend hf_local --backend gemma"
if "%SEL%"=="3" set "ARGS=--backend hf_local"
if "%SEL%"=="4" set "ARGS=--backend gemma"
if "%SEL%"=="5" set "ARGS=--backend groqwen"
if "%SEL%"=="6" set "ARGS=--backend mistral"
if "%SEL%"=="7" goto single_model
goto run

:custom_backend
set /p "BACKEND=Backend name (nova/hf_local/gemma/groqwen/mistral): "
set "ARGS=--backend %BACKEND%"
goto run

:single_model
set /p "BACKEND=Backend name (hf_local/gemma/groqwen/mistral): "
set /p "MODEL=Model name: "
set "ARGS=--backend %BACKEND% --model %MODEL%"
goto run

:run_args
set "ARGS=%*"

:run
if exist "%PYEXE%" (
    "%PYEXE%" "%ROOT%\test\ai_models.py" %ARGS%
    exit /b %errorlevel%
)

py -3 "%ROOT%\test\ai_models.py" %ARGS%
if not errorlevel 1 exit /b 0

python "%ROOT%\test\ai_models.py" %ARGS%
exit /b %errorlevel%
