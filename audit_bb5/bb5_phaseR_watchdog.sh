#!/usr/bin/env bash
# BB(5) phase R watchdog -- mechanical wall backstop (17 h from run start).
# v2 (2026-10-18): pattern diperluas untuk runner resume (attempt 2).
set -u
LOG="/mnt/d/Opencode AI Agent/reports/audit_bb5_phaseR_2026-10-18.log"
R=/root/bb5r
PAT='/root/bb5r/bb5_phaseR(_resume)?.sh'
sleep 120
for i in $(seq 1 1080); do
  if ! pgrep -f "$PAT" >/dev/null 2>&1; then
    echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | WATCHDOG(v2): runner no longer present; exiting normally (no stop record)." | tee -a "$LOG"
    exit 0
  fi
  if [ -f "$R/deadline_epoch" ]; then
    now=$(date +%s)
    dl=$(cat "$R/deadline_epoch")
    if [ "$now" -ge "$dl" ]; then
      pkill -f "$PAT" 2>/dev/null
      pkill -f "$R/Coq-BB5-git" 2>/dev/null
      { echo ""; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | WATCHDOG STOP: wall backstop reached (deadline epoch $dl); runner killed (best-effort child kill on build tree); item recorded UNRESOLVED-BUDGET."; } | tee -a "$LOG"
      exit 0
    fi
  fi
  sleep 60
done
echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | WATCHDOG(v2): loop limit reached; exiting." | tee -a "$LOG"
exit 0
