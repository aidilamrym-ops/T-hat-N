#!/usr/bin/env bash
# BB(5) phase R keepalive tick -- invoked by the Windows-side loop (~10 s) started by
# Scheduled Task 'T-hat-N-BB5-keepalive'. Each tick = one NEW short WSL session (the tick
# itself must stay well under the observed instance-idle window of ~21-23 s).
# Exit codes: 0 = continue; 42 = loop should stop (phase complete or stop requested).
set -u
LOG="/mnt/d/Opencode AI Agent/reports/audit_bb5_phaseR_2026-10-18.log"
R=/root/bb5r
mkdir -p "$R"
date -u +%s > "$R/keepalive.heartbeat"

if [ -f "$R/PHASER_COMPLETE" ] || [ -f "$R/STOP_KEEPALIVE" ]; then exit 42; fi

# deadline backstop (single writer via atomic noclobber claim)
if [ -f "$R/deadline_epoch" ] && [ ! -f "$R/STOP_RECORDED" ]; then
  now=$(date +%s); dl=$(cat "$R/deadline_epoch")
  if [ "$now" -ge "$dl" ]; then
    if ( set -o noclobber; > "$R/STOP_RECORDED" ) 2>/dev/null; then
      pkill -f 'bb5_phaseR_resume[0-9]*\.sh' 2>/dev/null
      pkill -f "$R/Coq-BB5-git" 2>/dev/null
      { echo ""; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | KEEPALIVE STOP: wall backstop reached (deadline epoch $dl); runner killed (best-effort); item recorded UNRESOLVED-BUDGET."; } | tee -a "$LOG"
    fi
    exit 0
  fi
fi

# abort latch: if the runner recorded a failure, do not relaunch (needs attention)
[ -f "$R/DAEMON_FAIL" ] && exit 0

# self-healing: relaunch the detached runner if it is not running (flock; bracket pattern avoids self-match)
flock -n "$R/daemon.flock" bash -c '
  pgrep -f "[b]b5_phaseR_resume3\.sh" >/dev/null 2>&1 && exit 0
  setsid nohup bash "/mnt/d/Opencode AI Agent/audit_bb5/bb5_phaseR_resume3.sh" </dev/null >>/root/bb5r/daemon_stdout.log 2>&1 &
' || true
exit 0
