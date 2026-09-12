& "C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe" -t:Restore c:\Users\Forge\MyProject\LCARSToolkit\LCARSToolkit\LCARSToolkit.sln
if($?) { & "C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe" c:\Users\Forge\MyProject\LCARSToolkit\LCARSToolkit\LCARSToolkit.Example\LCARSToolkit.Example.csproj /p:Configuration=Debug /p:Platform=x86 }
if($?) { Add-AppxPackage -Register "C:\Users\Forge\MyProject\LCARSToolkit\LCARSToolkit\LCARSToolkit.Example\bin\x86\Debug\AppxManifest.xml" -ForceApplicationShutdown }
if($?) { 
    $familyName = (Get-AppxPackage -Name "ed9c805a-33b2-4fa5-95cc-0ab80edd2854").PackageFamilyName
    Start-Process "shell:AppsFolder\$familyName!App"
    Start-Sleep -Seconds 5
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bitmap = New-Object System.Drawing.Bitmap $bounds.width, $bounds.height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.size)
    $bitmap.Save('C:\Users\Forge\.gemini\antigravity\brain\da459370-778e-45a2-9b52-a9373f671431\app_screenshot.png', [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    Stop-Process -Name LCARSToolkit.Example -ErrorAction SilentlyContinue
}
