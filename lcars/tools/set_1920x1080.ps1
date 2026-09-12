# Run this script as Administrator
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class NativeMethods {
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Ansi)]
  public struct DEVMODE {
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string dmDeviceName;
    public short dmSpecVersion; public short dmDriverVersion; public short dmSize; public short dmDriverExtra;
    public int dmFields; public int dmPelsWidth; public int dmPelsHeight; public int dmDisplayFlags; public int dmDisplayFrequency;
  }
  [DllImport("user32.dll", CharSet=CharSet.Ansi)]
  public static extern bool EnumDisplaySettings(string lpszDeviceName, int iModeNum, ref DEVMODE lpDevMode);
  [DllImport("user32.dll", CharSet=CharSet.Ansi)]
  public static extern int ChangeDisplaySettingsEx(string lpszDeviceName, ref DEVMODE lpDevMode, IntPtr hwnd, int dwflags, IntPtr lParam);
}
"@

$device = $null   # primary display
$targetW = 1920
$targetH = 1080

$mode = New-Object NativeMethods+DEVMODE
$mode.dmSize = [Runtime.InteropServices.Marshal]::SizeOf($mode)

$i=0; $found = $false; $foundIndex = -1; $foundFreq = 0
while([NativeMethods]::EnumDisplaySettings($device, $i, [ref]$mode)) {
  if ($mode.dmPelsWidth -eq $targetW -and $mode.dmPelsHeight -eq $targetH) {
    $found = $true; $foundIndex = $i; $foundFreq = $mode.dmDisplayFrequency; break
  }
  $i++
}

if (-not $found) {
  Write-Output "Mode 1920x1080 not found among available modes. Run the enumerator script to list modes."
  exit 2
}

Write-Output ("Found mode index {0} with {1}Hz" -f $foundIndex, $foundFreq)

# load the desired mode into dm and apply
$dm = New-Object NativeMethods+DEVMODE
$dm.dmSize = [Runtime.InteropServices.Marshal]::SizeOf($dm)
[NativeMethods]::EnumDisplaySettings($device, $foundIndex, [ref]$dm) | Out-Null
$DM_PELSWIDTH = 0x80000
$DM_PELSHEIGHT = 0x100000
$dm.dmFields = $DM_PELSWIDTH -bor $DM_PELSHEIGHT
$dm.dmPelsWidth = $targetW
$dm.dmPelsHeight = $targetH
$CDS_UPDATEREGISTRY = 0x00000001
$res = [NativeMethods]::ChangeDisplaySettingsEx($device, [ref]$dm, [IntPtr]::Zero, $CDS_UPDATEREGISTRY, [IntPtr]::Zero)
if ($res -eq 0) { Write-Output "Success: resolution applied."; exit 0 } else { Write-Output ("Error: code {0}" -f $res); exit 1 }
