# BB(5) phase R -- Windows-side keepalive loop (attempt 4).
# Runs a short WSL tick every ~10 s (a NEW session each tick; no long-lived session needed).
# Also started by Scheduled Task 'T-hat-N-BB5-keepalive' (registered by bb5_phaseR_keepalive_task.ps1).
# Exits when the tick returns 42 (PHASER_COMPLETE or STOP_KEEPALIVE present).
$tick = '/mnt/d/Opencode AI Agent/audit_bb5/bb5_phaseR_keepalive_tick.sh'
for (;;) {
  & wsl.exe -d Ubuntu -u root -- bash $tick *> $null
  if ($LASTEXITCODE -eq 42) { break }
  Start-Sleep -Seconds 10
}
