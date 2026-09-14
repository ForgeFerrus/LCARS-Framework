# Реєстрація LCARS Autocommit Watch у Windows Task Scheduler
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonExe   = (Get-Command py).Source
$ScriptPath  = Join-Path $ProjectRoot "scripts\autocommit.py"
$IntervalMin = 15

$Action  = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ScriptPath`" --watch $IntervalMin" -WorkingDirectory $ProjectRoot
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 0) -MultipleInstances IgnoreNew -Hidden

Register-ScheduledTask `
    -TaskName "LCARS-Autocommit" `
    -Action   $Action `
    -Trigger  $Trigger `
    -Settings $Settings `
    -Description "LCARS Framework auto-commit every $IntervalMin minutes" `
    -Force

Write-Host "OK: Task LCARS-Autocommit зареєстровано."
Write-Host "Запуск зараз..."
Start-ScheduledTask -TaskName "LCARS-Autocommit"
Write-Host "Watch запущено у фоні."
