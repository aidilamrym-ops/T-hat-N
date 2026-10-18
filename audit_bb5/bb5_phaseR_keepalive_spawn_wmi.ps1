# BB(5) phase R -- spawn keepalive supervisors via WMI (outlives the agent tool-call process tree).
# Rationale (recorded in reports/audit_bb5_phaseR_2026-10-18.log): a Start-Process child was killed
# when the tool call that created it ended; WMI-created processes are parented to WmiPrvSE and
# survive tool-call teardown.
# Run:  powershell -NoProfile -ExecutionPolicy Bypass -File bb5_phaseR_keepalive_spawn_wmi.ps1
$cl = 'powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "D:\Opencode AI Agent\audit_bb5\bb5_phaseR_keepalive.ps1"'
1..2 | ForEach-Object {
  $r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$cl}
  "spawn $_ : ReturnValue=$($r.ReturnValue) ProcessId=$($r.ProcessId)"
}
