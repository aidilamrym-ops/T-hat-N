#!/usr/bin/env bash
# BB(5) phase R -- attempt 3 (resume; attempt 2 halted by a WSL VM stop mid-build).
# Attempt 1 aborted EXIT 10 at coq install; attempt 2 completed setup + Coq 8.20.1 +
# BusyCoq (25/25) and reached 36/50 .vo in CoqBB5/BB5 before the VM stop
# (see the INTERRUPTION note in the log). This runner reuses all state; make resumes.
set -u
LOG="/mnt/d/Opencode AI Agent/reports/audit_bb5_phaseR_2026-10-18.log"
R=/root/bb5r

run_step() { # run_step <name> <shell-command-string>
  local name="$1" cmd="$2" rc
  echo "" | tee -a "$LOG"
  { echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | $name"; echo "CMD: $cmd"; } | tee -a "$LOG"
  bash -c "$cmd" 2>&1 | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  echo "EXIT: $rc" | tee -a "$LOG"
  return $rc
}

abort() { echo "=== phase R (attempt 3) ABORT: $1 $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"; exit "$2"; }

{
  echo ""
  echo "=== phase R attempt 3 (resume) start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  echo "runner: /root/bb5r/bb5_phaseR_resume2.sh sha256 $(sha256sum "$0" | awk '{print $1}')"
  cmp -s "$0" "/mnt/d/Opencode AI Agent/audit_bb5/bb5_phaseR_resume2.sh" && echo "resume2 copy == repo copy (byte-identical)" || echo "WARNING: resume2 copy differs from repo copy"
  echo "watchdog: /root/bb5r/bb5_phaseR_watchdog.sh sha256 $(sha256sum $R/bb5_phaseR_watchdog.sh 2>/dev/null | awk '{print $1}')"
  echo "attempt 2 status: HALTED by WSL VM stop ca. 07:12:35Z (mid TNF_Root_4_6.v); no audit results; BusyCoq 25/25 .vo; BB5 36/50 .vo; state reused; make resumes."
  echo "hardening: %USERPROFILE%\\.wslconfig [wsl2] vmIdleTimeout=86400000 verified (see INTERRUPTION note in log)."
  echo "watchdog deadline (tidak berubah dari run start asli): $(cat "$R/deadline_epoch" 2>/dev/null || echo MISSING)"
} | tee -a "$LOG"

ENVOUT="$(opam env --shell=bash 2>&1 | grep -v '^\[WARNING\]')"; envrc=$?
{ echo ""; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | opam env (eval in runner; WARNING difilter)"; echo "CMD: opam env --shell=bash"; echo "$ENVOUT"; echo "EXIT: $envrc"; } | tee -a "$LOG"
[ $envrc -eq 0 ] || abort "opam env" 31
eval "$ENVOUT"

run_step "coqc --version (expect 8.20.1)" "coqc --version" || abort "coqc" 32

run_step "build BusyCoq (make -j4; no-op bila lengkap)" "cd $R/Coq-BB5-git/BusyCoq && time make -j4" || abort "BusyCoq build" 33

run_step "build CoqBB5/BB5 (make -j4; melanjutkan dari 36/50)" "cd $R/Coq-BB5-git/CoqBB5/BB5 && time make -j4" || abort "BB5 build" 34

run_step "assumptions marker extract (self-grep)" "grep -n -E 'Print Assumptions|functional_extensionality|Axioms:|Assumptions:' \"$LOG\" | tail -40" || true

run_step "count .vo (BusyCoq)" "find $R/Coq-BB5-git/BusyCoq -name '*.vo' | wc -l" || true
run_step "count .vo (BB5)" "find $R/Coq-BB5-git/CoqBB5/BB5 -name '*.vo' | wc -l" || true
run_step "BB5_Theorem.vo present" "ls -l $R/Coq-BB5-git/CoqBB5/BB5/BB5_Theorem.vo" || true

echo "" | tee -a "$LOG"
echo "=== phase R attempt 3 (resume) end $(date -u +%Y-%m-%dT%H:%M:%SZ) (all steps exit 0 as recorded above) ===" | tee -a "$LOG"
exit 0
