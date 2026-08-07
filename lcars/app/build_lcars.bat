@echo off
echo Building LCARS DirectX 11...
echo.

REM Перевіряємо наявність Visual Studio
where cl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Visual Studio compiler not found!
    echo Please install Visual Studio with C++ development tools
    pause
    exit /b 1
)

echo Compiling LCARS DirectX 11...
cl /EHsc /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22000.0\um" ^
   /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22000.0\shared" ^
   /I"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22000.0\ucrt" ^
   /I"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130\include" ^
   lcars_dx11.cpp ^
   /link /LIBPATH:"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.22000.0\um\x64" ^
         /LIBPATH:"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130\lib\x64" ^
         d3d11.lib d3dcompiler.lib dxgi.lib user32.lib gdi32.lib ^
         /OUT:lcars_dx11.exe

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! LCARS DirectX 11 compiled successfully!
    echo Running LCARS...
    echo.
    lcars_dx11.exe
) else (
    echo.
    echo FAILED to compile LCARS DirectX 11
    pause
)
