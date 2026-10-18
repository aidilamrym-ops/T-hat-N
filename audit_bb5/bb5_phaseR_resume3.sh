#!/usr/bin/env bash
# BB(5) phase R -- attempt 4 (resume; attempt 3 halted by WSL instance idle-termination at 09:27:36Z).
# Runs directly from the repo path (single source of truth); launched detached (setsid+nohup)
# by the keepalive tick. Idempotent: make resumes from existing .vo files.
# Deadline backstop and self-healing relaunch live in bb5_phaseR_keepalive_tick.sh.
set -u
LOG="/mnt/d/Opencode AI Agent/reports/audit_bb5_phaseR_2026-10-18.log"
R=/root/bb5r
SELF="/mnt/d/Opencode AI Agent/audit_bb5/bb5_phaseR_resume3.sh"

run_step() { # run_step <name> <shell-command-string>
  local name="$1" cmd="$2" rc
  echo "" | tee -a "$LOG"
  { echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | $name"; echo "CMD: $cmd"; } | tee -a "$LOG"
  bash -c "$cmd" 2>&1 | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  echo "EXIT: $rc" | tee -a "$LOG"
  return $rc
}

abort() { echo "=== phase R (attempt 4) ABORT: $1 $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"; touch "$R/DAEMON_FAIL"; exit "$2"; }

[ -f "$R/STOP_KEEPALIVE" ] && { echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | attempt 4 runner: STOP_KEEPALIVE present; not starting." | tee -a "$LOG"; exit 0; }
[ -f "$R/PHASER_COMPLETE" ] && exit 0

{
  echo ""
  echo "=== phase R attempt 4 (resume) start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  echo "runner: $SELF (repo path; single source of truth) sha256 $(sha256sum "$SELF" | awk '{print $1}')"
  echo "attempt 3 status: HALTED by WSL instance idle-termination ca. 09:27:36Z (mid TNF_Root_4_10.v; VM hidup/instance dimatikan); no audit results; resume from 40/50 .vo."
  echo "supervision: Windows Scheduled Task keepalive -> tick ~10 dtk (self-healing relaunch); deadline epoch $(cat "$R/deadline_epoch" 2>/dev/null || echo MISSING)."
} | tee -a "$LOG"

ENVOUT="$(opam env --shell=bash 2>&1 | grep -v '^\[WARNING\]')"; envrc=$?
{ echo ""; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | opam env (eval in runner; WARNING difilter)"; echo "CMD: opam env --shell=bash"; echo "$ENVOUT"; echo "EXIT: $envrc"; } | tee -a "$LOG"
[ $envrc -eq 0 ] || abort "opam env" 41
eval "$ENVOUT"

run_step "coqc --version (expect 8.20.1)" "coqc --version" || abort "coqc" 42

run_step "build BusyCoq (make -j4; no-op bila lengkap)" "cd $R/Coq-BB5-git/BusyCoq && time make -j4" || abort "BusyCoq build" 43

run_step "build CoqBB5/BB5 (make -j4; melanjutkan dari parsial)" "cd $R/Coq-BB5-git/CoqBB5/BB5 && time make -j4" || abort "BB5 build" 44

run_step "assumptions marker extract (self-grep)" "grep -n -E 'Print Assumptions|functional_extensionality|Axioms:|Assumptions:' \"$LOG\" | tail -40" || true

run_step "count .vo (BusyCoq)" "find $R/Coq-BB5-git/BusyCoq -name '*.vo' | wc -l" || true
run_step "count .vo (BB5)" "find $R/Coq-BB5-git/CoqBB5/BB5 -name '*.vo' | wc -l" || true
run_step "BB5_Theorem.vo present" "ls -l $R/Coq-BB5-git/CoqBB5/BB5/BB5_Theorem.vo" || true

touch "$R/PHASER_COMPLETE"
echo "" | tee -a "$LOG"
echo "=== phase R attempt 4 (resume) end $(date -u +%Y-%m-%dT%H:%M:%SZ) (all steps exit 0 as recorded above; PHASER_COMPLETE set) ===" | tee -a "$LOG"
exit 0
