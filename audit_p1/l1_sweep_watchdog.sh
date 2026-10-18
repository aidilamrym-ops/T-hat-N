#!/usr/bin/env bash
# audit_p1 L1 sweep - pre-registered wall-cap watchdog (committed 2026-10-18 with the
# sweep pre-registration; see reports/audit_p1_l1_sweep_2026-10-18.log). Waits for the
# sweep's REPLAY_METADATA.txt, then enforces the pre-registered 6 h wall from
# started_utc: if the sweep is still running at the wall, it stops the podman
# containers and the sweep driver and appends the stop record to the sweep log
# (UNRESOLVED-BUDGET). If the sweep finishes first, the repo log is not touched;
# watchdog state goes to /root/l1/replay-out/sweep_watchdog.log (outside the repo).
set -u

LOG='/mnt/d/Opencode AI Agent/reports/audit_p1_l1_sweep_2026-10-18.log'
STATE=/root/l1/replay-out/sweep_watchdog.log
META=/root/l1/replay-out/sweep/REPLAY_METADATA.txt

printf '%s watchdog armed (6 h wall from started_utc)\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" >"$STATE"

st_epoch=0
for _ in $(seq 1 15); do
  if [ -f "$META" ]; then
    st=$(sed -n 's/^started_utc=//p' "$META" | head -n 1)
    if [ -n "$st" ]; then
      st_epoch=$(date -u -d "$st" +%s 2>/dev/null || printf '0')
      if [ "$st_epoch" -gt 0 ]; then break; fi
    fi
  fi
  sleep 60
done
if [ "$st_epoch" -le 0 ]; then st_epoch=$(date +%s); fi
printf '%s started_utc epoch=%s; deadline epoch=%s\n' \
  "$(date +%Y-%m-%dT%H:%M:%S%z)" "$st_epoch" "$((st_epoch + 21600))" >>"$STATE"

deadline=$((st_epoch + 21600))
while [ "$(date +%s)" -lt "$deadline" ]; do
  if ! pgrep -f 'run_full_sweep\.sh' >/dev/null 2>&1; then
    printf '%s sweep not running before the wall; watchdog exits (nothing to stop)\n' \
      "$(date +%Y-%m-%dT%H:%M:%S%z)" >>"$STATE"
    exit 0
  fi
  sleep 30
done

if pgrep -f 'run_full_sweep\.sh' >/dev/null 2>&1; then
  printf '\n--- %s | cap: pre-registered 6 h wall (from started_utc) reached; stopping the sweep (UNRESOLVED-BUDGET per this log header)\nCMD: podman kill --all; pkill -f run_full_sweep.sh\n' \
    "$(date +%Y-%m-%dT%H:%M:%S%z)" >>"$LOG"
  podman kill --all >>"$LOG" 2>&1 || true
  pkill -f 'run_full_sweep\.sh' >>"$LOG" 2>&1 || true
  printf 'EXIT: cap-stop issued\n' >>"$LOG"
  printf '%s cap-stop issued\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" >>"$STATE"
else
  printf '%s wall reached but sweep already stopped; nothing to do\n' \
    "$(date +%Y-%m-%dT%H:%M:%S%z)" >>"$STATE"
fi
exit 0
