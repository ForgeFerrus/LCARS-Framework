# Реєстрація LCARS Autocommit Watch у Windows Task Scheduler (без прав адміна)
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PythonPath  = (Get-Command py -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) { $PythonPath = "py" }
$ScriptPath  = Join-Path $ProjectRoot "scripts\autocommit.py"
$IntervalMin = 15

$Action  = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`" --watch $IntervalMin" `
    -WorkingDirectory $ProjectRoot

$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -MultipleInstances IgnoreNew `
    -Hidden

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName    "LCARS-Autocommit" `
    -Action      $Action `
    -Trigger     $Trigger `
    -Settings    $Settings `
    -Principal   $Principal `
    -Description "LCARS Framework auto-commit every $IntervalMin minutes" `
    -Force

Write-Host "OK: Task LCARS-Autocommit зареєстровано."
Write-Host "Запуск зараз..."
Start-ScheduledTask -TaskName "LCARS-Autocommit"
Write-Host "Watch запущено у фоні (кожні $IntervalMin хв)."
