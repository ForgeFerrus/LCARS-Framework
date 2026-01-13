; Inno Setup script for portable LCARS Framework installer
; Зберегти як build_lcars_installer.iss і зібрати через Inno Setup Compiler

[Setup]
AppName=LCARS Framework
AppVersion=1.0.0
DefaultDirName={pf}\LCARS_Framework
DefaultGroupName=LCARS Framework
Uninstallable=yes
Compression=lzma
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=LCARS_Framework_Installer

[Files]
Source: "dist\LCARS_Framework.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "lcars\*"; DestDir: "{app}\lcars"; Flags: recursesubdirs ignoreversion
Source: "config\*"; DestDir: "{app}\config"; Flags: recursesubdirs ignoreversion
Source: "resources\*"; DestDir: "{app}\resources"; Flags: recursesubdirs ignoreversion
Source: "themes\*"; DestDir: "{app}\themes"; Flags: recursesubdirs ignoreversion
Source: "plugins\*"; DestDir: "{app}\plugins"; Flags: recursesubdirs ignoreversion
Source: "lcars_data\*"; DestDir: "{app}\lcars_data"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\LCARS Framework"; Filename: "{app}\LCARS_Framework.exe"
Name: "{group}\LCARS Dev Editor"; Filename: "{app}\devtools\editor.pyw"

[Run]
Filename: "{app}\LCARS_Framework.exe"; Description: "Запустити LCARS Framework"; Flags: nowait postinstall skipifsilent
