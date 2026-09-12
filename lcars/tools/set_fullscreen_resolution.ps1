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

$device = $null   # $null = primary display. Use "\\.\DISPLAY2" to target another display.
# read current mode (-1)
$curr = New-Object NativeMethods+DEVMODE
$curr.dmSize = [Runtime.InteropServices.Marshal]::SizeOf($curr)
[NativeMethods]::EnumDisplaySettings($device, -1, [ref]$curr) | Out-Null
"Поточна роздільність: {0}x{1}, {2}Hz" -f $curr.dmPelsWidth, $curr.dmPelsHeight, $curr.dmDisplayFrequency

# enumerate supported modes
$modes = @()
$mode = New-Object NativeMethods+DEVMODE
$mode.dmSize = [Runtime.InteropServices.Marshal]::SizeOf($mode)
$i=0
while([NativeMethods]::EnumDisplaySettings($device, $i, [ref]$mode)) {
  $modes += [PSCustomObject]@{Index=$i;Width=$mode.dmPelsWidth;Height=$mode.dmPelsHeight;Freq=$mode.dmDisplayFrequency}
  $i++
}
if ($modes.Count -eq 0) { Write-Error "Не знайдено режимів."; exit 1 }

# choose best mode by area (width*height), then by frequency
$best = $modes | Sort-Object @{Expression={$_.Width*$_.Height};Descending=$true}, @{Expression={$_.Freq};Descending=$true} | Select-Object -First 1
"Вибрано режим: {0}x{1}, {2}Hz (index {3})" -f $best.Width, $best.Height, $best.Freq, $best.Index

# apply chosen mode
$dm = New-Object Win32Api.User32+DEVMODE
$dm.dmSize = [Runtime.InteropServices.Marshal]::SizeOf($dm)
$([NativeMethods]::EnumDisplaySettings($device, $best.Index, [ref]$dm)) | Out-Null
$DM_PELSWIDTH = 0x80000
$DM_PELSHEIGHT = 0x100000
$dm.dmFields = $DM_PELSWIDTH -bor $DM_PELSHEIGHT
$dm.dmPelsWidth = $best.Width
$dm.dmPelsHeight = $best.Height
$CDS_UPDATEREGISTRY = 0x00000001
$res = [Win32Api.User32]::ChangeDisplaySettingsEx($device, [ref]$dm, [IntPtr]::Zero, $CDS_UPDATEREGISTRY, [IntPtr]::Zero)
if ($res -eq 0) { "Успіх: налаштування застосовано." } else { "Помилка: код {0}" -f $res }

Write-Output "To revert, run the script again using the target width/height shown above."
Write-Output ("  $targetW = {0}; $targetH = {1}" -f $curr.dmPelsWidth, $curr.dmPelsHeight)
