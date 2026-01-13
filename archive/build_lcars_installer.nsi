; NSIS script for portable LCARS Framework installer
; Зберегти як build_lcars_installer.nsi і зібрати через NSIS

Name "LCARS Framework"
OutFile "dist\LCARS_Framework_Installer.exe"
InstallDir "$PROGRAMFILES\LCARS_Framework"
RequestExecutionLevel admin

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\LCARS_Framework.exe"
  File /r "lcars\*.*"
  File /r "config\*.*"
  File /r "resources\*.*"
  File /r "themes\*.*"
  File /r "plugins\*.*"
  File /r "lcars_data\*.*"
SectionEnd

Section "Shortcuts"
  CreateShortCut "$DESKTOP\LCARS Framework.lnk" "$INSTDIR\LCARS_Framework.exe"
  CreateShortCut "$DESKTOP\LCARS Dev Editor.lnk" "$INSTDIR\devtools\editor.pyw"
SectionEnd
