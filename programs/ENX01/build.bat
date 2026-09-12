@echo off
REM Proxy build script for ENX01 located in the LCARS `programs` folder.
REM This forwards to the actual Geant4 project helper.

setlocal
set ROOT=%~dp0
set REPO_ROOT=%~dp0\..\..\
set TARGET=%REPO_ROOT%Geant4\Enterprise\ENX01\build_ENX01.bat

if exist "%TARGET%" (
  pushd "%REPO_ROOT%Geant4\Enterprise\ENX01"
  call "%TARGET%"
  popd
  endlocal
  exit /b %errorlevel%
)

echo ERROR: ENX01 build helper not found at %TARGET%
exit /b 1
