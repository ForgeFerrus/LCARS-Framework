@echo off
REM Proxy run script for ENX01 in LCARS `programs` folder.

setlocal
set ROOT=%~dp0
set REPO_ROOT=%~dp0\..\..\
set TARGET=%REPO_ROOT%Geant4\Enterprise\ENX01\run_ENX01.bat

if exist "%TARGET%" (
  pushd "%REPO_ROOT%Geant4\Enterprise\ENX01"
  call "%TARGET%" %*
  popd
  endlocal
  exit /b %errorlevel%
)

echo ERROR: ENX01 run helper not found at %TARGET%
exit /b 1
