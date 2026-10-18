# BB(5) phase R -- OPTIONAL elevated path: register + start the keepalive Scheduled Task.
# STATUS 2026-10-18 ~10:55Z: non-admin registration DENIED on this host
#   (Register-ScheduledTask: Access is denied 0x80070005; schtasks /create: same class,
#    and no elevation available non-interactively). Non-admin supervisors are used instead
#   (see the log note "UPDATE PRA-LAUNCH attempt 4" in reports/audit_bb5_phaseR_2026-10-18.log).
# If the OWNER runs this from an ELEVATED PowerShell, the Scheduled Task becomes the
# strongest persistence path (AtLogOn trigger + restart-on-failure every 1 min).
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
