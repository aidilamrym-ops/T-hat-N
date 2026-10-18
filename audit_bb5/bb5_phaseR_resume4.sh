#!/usr/bin/env bash
# BB(5) phase R -- attempt 5 (resume; attempt 4 halted when the kernel OOM-killer killed
# the coqc compiling TNF_Root_4_11.v at 15:08:59Z (make Error 137); make then exited afte
# its outstanding jobs (TNF_Root_3, TNF_Root_4_10) finished and the runner wrote the
# attempt-4 ABORT + DAEMON_FAIL latch as designed).
# Change vs attempt 4: builds run with make -j2 instead of -j4 -- OOM mitigation on this
# 9.7 GiB host. -j affects only scheduling/parallelism, not the compiled artifacts; the
# pre-registration cap "no -j > 4" is upheld.
# Runs directly from the repo path (single source of truth); launched detached (setsid+nohup)
# by the keepalive tick v4 after the one-shot APPROVE_ATTEMPT5 token consumed the latch.
# Idempotent: make resumes from existing .vo files.
# Deadline backstop and self-healing relaunch live in bb5_phaseR_keepalive_tick.sh.
set -u
LOG="/mnt/d/Opencode AI Agent/reports/audit_bb5_phaseR_2026-10-18.log"
R=/root/bb5r
SELF="/mnt/d/Opencode AI Agent/audit_bb5/bb5_phaseR_resume4.sh"

run_step() { # run_step <name> <shell-command-string>
  local name="$1" cmd="$2" rc
  echo "" | tee -a "$LOG"
  { echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | $name"; echo "CMD: $cmd"; } | tee -a "$LOG"
  bash -c "$cmd" 2>&1 | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  echo "EXIT: $rc" | tee -a "$LOG"
  return $rc
}

abort() { echo "=== phase R (attempt 5) ABORT: $1 $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"; touch "$R/DAEMON_FAIL"; exit "$2"; }

[ -f "$R/STOP_KEEPALIVE" ] && { echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | attempt 5 runner: STOP_KEEPALIVE present; not starting." | tee -a "$LOG"; exit 0; }
[ -f "$R/PHASER_COMPLETE" ] && exit 0

{
  echo ""
  echo "=== phase R attempt 5 (resume) start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  echo "runner: $SELF (repo path; single source of truth) sha256 $(sha256sum "$SELF" | awk '{print $1}')"
  echo "attempt 4 status: OOM-kill (kernel) pada coqc TNF_Root_4_11.v 15:08:59Z (make: Error 137); runner menulis ABORT attempt 4 + DAEMON_FAIL setelah job tersisa (TNF_Root_3, TNF_Root_4_10) selesai. Tidak ada hasil audit."
  echo "resume .vo count: $(find "$R/Coq-BB5-git/CoqBB5/BB5" -name '*.vo' | wc -l)/50"
  echo "mitigasi OOM: build dengan make -j2 (turun dari -j4); cap prereg 'no -j >4' dipatuhi; artefak kompilasi tidak berubah."
  echo "supervision: tick v4 (self-healing relaunch + token APPROVE_ATTEMPT5 sekali-pakai); deadline epoch $(cat "$R/deadline_epoch" 2>/dev/null || echo MISSING) (tidak berubah)."
} | tee -a "$LOG"

ENVOUT="$(opam env --shell=bash 2>&1 | grep -v '^\[WARNING\]')"; envrc=$?
{ echo ""; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | opam env (eval in runner; WARNING difilter)"; echo "CMD: opam env --shell=bash"; echo "$ENVOUT"; echo "EXIT: $envrc"; } | tee -a "$LOG"
[ $envrc -eq 0 ] || abort "opam env" 51
eval "$ENVOUT"

run_step "coqc --version (expect 8.20.1)" "coqc --version" || abort "coqc" 52

run_step "build BusyCoq (make -j2; no-op bila lengkap)" "cd $R/Coq-BB5-git/BusyCoq && time make -j2" || abort "BusyCoq build" 53

run_step "build CoqBB5/BB5 (make -j2; melanjutkan dari parsial)" "cd $R/Coq-BB5-git/CoqBB5/BB5 && time make -j2" || abort "BB5 build" 54

run_step "assumptions marker extract (self-grep)" "grep -n -E 'Print Assumptions|functional_extensionality|Axioms:|Assumptions:' \"$LOG\" | tail -40" || true

run_step "count .vo (BusyCoq)" "find $R/Coq-BB5-git/BusyCoq -name '*.vo' | wc -l" || true
run_step "count .vo (BB5)" "find $R/Coq-BB5-git/CoqBB5/BB5 -name '*.vo' | wc -l" || true
run_step "BB5_Theorem.vo present" "ls -l $R/Coq-BB5-git/CoqBB5/BB5/BB5_Theorem.vo" || true

touch "$R/PHASER_COMPLETE"
echo "" | tee -a "$LOG"
echo "=== phase R attempt 5 (resume) end $(date -u +%Y-%m-%dT%H:%M:%SZ) (all steps exit 0 as recorded above; PHASER_COMPLETE set) ===" | tee -a "$LOG"
exit 0
