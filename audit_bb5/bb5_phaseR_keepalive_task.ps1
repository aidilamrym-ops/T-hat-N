# BB(5) phase R -- register + start the keepalive Scheduled Task (attempt 4).
# Task 'T-hat-N-BB5-keepalive' runs: powershell -File <repo>\audit_bb5\bb5_phaseR_keepalive.ps1
# Recorded for audit. Cleanup after phase R:
#   Unregister-ScheduledTask -TaskName 'T-hat-N-BB5-keepalive' -Confirm:$false
$ErrorActionPreference = 'Stop'
$taskName = 'T-hat-N-BB5-keepalive'
$ps1 = 'D:\Opencode AI Agent\audit_bb5\bb5_phaseR_keepalive.ps1'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $ps1)
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description 'T-hat-N audit: keep WSL Ubuntu alive + self-heal BB(5) phase R build (attempt 4). Remove after phase R completes.' -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 3
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName,State | Format-Table -AutoSize
Get-ScheduledTaskInfo -TaskName $taskName | Select-Object LastRunTime,LastTaskResult | Format-Table -AutoSize
