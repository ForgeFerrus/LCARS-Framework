@echo off
:MENU
cls
echo ======================================================
echo           LCARS FRAMEWORK - PROTOTYPE MENU
echo ======================================================
echo.
echo 1. Klingon Battle Station (Battle Edition)
echo 2. Romulan Strategic Interface (Classic)
echo 3. Romulan Strategic V2 
echo 4. LCARS 22nd Century (NX-01 Era)
echo 5. LCARS 23rd Century (Constitution Era)
echo 6. LCARS 24th Century (TNG/DS9 Era) - HIGH DETAIL
echo 7. LCARS 25th Century (Picard Era) - HIGH DETAIL
echo 8. LCARS 29th Century (TCARS/Temporal)
echo 9. PCARS 22nd Century (Utilitarian) - ADVANCED
echo 10. PCARS 23rd Century (Pre-LCARS) - ADVANCED
echo 11. LCARS Unified System (Integrated Hub)
echo 12. Simple Demo
echo 13. Diagnose Prototypes
echo 14. Exit

set /p choice=Select interface (1-14): 

if "%choice%"=="1" start "" python Klingon_system.py & goto MENU
if "%choice%"=="2" start "" python Romulan_interface.py & goto MENU
if "%choice%"=="3" start "" python Romulan_interface_v2.py & goto MENU
if "%choice%"=="4" start "" python COMS_22nd.py & goto MENU
if "%choice%"=="5" start "" python LCARS_23rd.py & goto MENU
if "%choice%"=="6" start "" python LCARS_24th.py & goto MENU
if "%choice%"=="7" start "" python LCARS_25th.py & goto MENU
if "%choice%"=="8" start "" python TCARS_29th.py & goto MENU
if "%choice%"=="9" start "" python PCARS_22nd.py & goto MENU
if "%choice%"=="10" start "" python PCARS_23rd.py & goto MENU
if "%choice%"=="11" start "" python lcars_unified_system.py & goto MENU
if "%choice%"=="12" start "" python ..\simple_demo.py & goto MENU
if "%choice%"=="13" start "" python diagnose_prototypes.py & goto MENU
if "%choice%"=="14" exit
exit

echo Invalid choice, try again.
pause
goto MENU
