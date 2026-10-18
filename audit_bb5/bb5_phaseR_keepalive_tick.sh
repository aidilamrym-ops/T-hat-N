#!/usr/bin/env bash
# BB(5) phase R keepalive tick v4 -- invoked by Windows-side loops (~10 s) from the
# supervisor hosts (WMI-created loops / harness shell / Startup item). Each tick = one NEW
# short WSL session (well under the observed instance-idle window of ~21-23 s).
# v4 (committed BEFORE retry): relaunch targets bb5_phaseR_resume4.sh (attempt 5, make -j2
# -- OOM mitigation) and a one-shot approval (APPROVE_ATTEMPT5) clears DAEMON_FAIL after
# the expected attempt-4 abort, letting the relaunch proceed exactly once. Any NEW failure
# re-latches DAEMON_FAIL and again requires attention.
# v4.1 (2026-10-18; attempt 5 running; committed BEFORE the wall branch could execute):
# wall backstop is record-only -- the v4 kill was defective (pkill -f "$R/Coq-BB5-git"
# matched only the bash -c wrapper; make/coqc run with relative paths and would be
# orphaned while the self-healing relaunch re-ran the same targets: double compile, OOM
# risk). See the deadline block below + pre-registered decision D-R5 in the transcript.
# Exit codes: 0 = continue; 42 = loop should stop (phase complete or stop requested).
set -u
LOG="/mnt/d/Opencode AI Agent/reports/audit_bb5_phaseR_2026-10-18.log"
R=/root/bb5r
mkdir -p "$R"
date -u +%s > "$R/keepalive.heartbeat"

if [ -f "$R/PHASER_COMPLETE" ] || [ -f "$R/STOP_KEEPALIVE" ]; then exit 42; fi

# deadline backstop (single writer via atomic noclobber claim).
# v4.1: record-only -- the v4 kill was defective (see header); Decision D-R5 (pre-registered
# in the phase-R transcript BEFORE the wall): leave attempt 5 running undisturbed at the
# wall; record the event as-is; no kill, no relaunch, no parameter changes.
if [ -f "$R/deadline_epoch" ] && [ ! -f "$R/STOP_RECORDED" ]; then
  now=$(date +%s); dl=$(cat "$R/deadline_epoch")
  if [ "$now" -ge "$dl" ]; then
    if ( set -o noclobber; > "$R/STOP_RECORDED" ) 2>/dev/null; then
      { echo ""; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | KEEPALIVE STOP: wall backstop reached (deadline epoch $dl); kill SUPPRESSED (pre-registered D-R5: attempt 5 continues undisturbed, no parameter changes); item recorded UNRESOLVED-BUDGET."; } | tee -a "$LOG"
    fi
    exit 0
  fi
fi

# one-shot approval (recorded BEFORE retry in the transcript): after the expected attempt-4
# abort (OOM; DAEMON_FAIL latched by the runner), consume APPROVE_ATTEMPT5, clear the latch
# once, and let the relaunch below start attempt 5 (make -j2).
if [ -f "$R/APPROVE_ATTEMPT5" ] && [ -f "$R/DAEMON_FAIL" ] && [ -f "/mnt/d/Opencode AI Agent/audit_bb5/bb5_phaseR_resume4.sh" ] && ! pgrep -f 'bb5_phaseR_resume[0-9]*\.sh' >/dev/null 2>&1; then
  rm -f "$R/DAEMON_FAIL" "$R/APPROVE_ATTEMPT5"
  { echo ""; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | APPROVE_ATTEMPT5: abort attempt 4 terdeteksi (DAEMON_FAIL); latch dihapus sekali-pakai; relaunch attempt 5 (make -j2). ---"; } | tee -a "$LOG"
fi

# abort latch: if the runner recorded a failure, do not relaunch (needs attention)
[ -f "$R/DAEMON_FAIL" ] && exit 0

# self-healing relaunch (v4: targets resume4 = attempt 5). NOTE: the pgrep is OUTSIDE the
# flock wrapper on purpose -- the wrapper's own cmdline contains the runner path (an inside
# pgrep would self-match and always exit early). The 2 s hold inside the wrapper closes the
# double-launch race between concurrent ticks.
if ! pgrep -f 'bb5_phaseR_resume[0-9]*\.sh' >/dev/null 2>&1; then
  flock -n "$R/daemon.flock" bash -c '
    setsid nohup bash "/mnt/d/Opencode AI Agent/audit_bb5/bb5_phaseR_resume4.sh" </dev/null >>/root/bb5r/daemon_stdout.log 2>&1 &
    sleep 2
  ' || true
fi
exit 0
