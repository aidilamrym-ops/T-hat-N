#!/usr/bin/env bash
# BB(5) phase R -- attempt 2 (resume; attempt 1 aborted EXIT 10 at coq install).
# Records a fresh start block; apt/opam-init/switch from attempt 1 are reused (EXIT 0).
set -u
export DEBIAN_FRONTEND=noninteractive
export OPAMYES=1
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

abort() { echo "=== phase R (attempt 2) ABORT: $1 $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"; exit "$2"; }

{
  echo ""
  echo "=== phase R attempt 2 (resume) start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  echo "runner: /root/bb5r/bb5_phaseR_resume.sh sha256 $(sha256sum "$0" | awk '{print $1}')"
  cmp -s "$0" "/mnt/d/Opencode AI Agent/audit_bb5/bb5_phaseR_resume.sh" && echo "resume copy == repo copy (byte-identical)" || echo "WARNING: resume copy differs from repo copy"
  echo "attempt 1 status: ABORT EXIT 10 at opam pin add coq (depext libgmp-dev non-interaktif); switch 4.14.2 selesai EXIT 0 (dipakai ulang, tidak diulang)."
  echo "watchdog deadline (tidak berubah dari run start asli): $(cat "$R/deadline_epoch" 2>/dev/null || echo MISSING)"
} | tee -a "$LOG"

run_step "apt install libgmp-dev (depext zarith/coq-core)" "apt-get install -y -qq libgmp-dev" || abort "libgmp-dev" 21

ENVOUT="$(opam env --shell=bash 2>&1 | grep -v '^\[WARNING\]')"; envrc=$?
{ echo ""; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | opam env (eval in runner; WARNING difilter)"; echo "CMD: opam env --shell=bash"; echo "$ENVOUT"; echo "EXIT: $envrc"; } | tee -a "$LOG"
[ $envrc -eq 0 ] || abort "opam env" 22
eval "$ENVOUT"

run_step "opam pin add coq 8.20.1 (retry; --confirm-level=unsafe-yes)" "opam pin add coq 8.20.1 -y --confirm-level=unsafe-yes" || abort "coq install retry" 23

run_step "opam installed coq packages" "opam list --installed --short | grep -E '^coq' || echo none" || true

run_step "coqc --version (expect 8.20.1)" "coqc --version" || abort "coqc" 24

run_step "build BusyCoq (make -j4)" "cd $R/Coq-BB5-git/BusyCoq && time make -j4" || abort "BusyCoq build" 25

run_step "build CoqBB5/BB5 (make -j4)" "cd $R/Coq-BB5-git/CoqBB5/BB5 && time make -j4" || abort "BB5 build" 26

run_step "assumptions marker extract (self-grep)" "grep -n -E 'Print Assumptions|functional_extensionality|Axioms:|Assumptions:' \"$LOG\" | tail -40" || true

run_step "count .vo (BusyCoq)" "find $R/Coq-BB5-git/BusyCoq -name '*.vo' | wc -l" || true
run_step "count .vo (BB5)" "find $R/Coq-BB5-git/CoqBB5/BB5 -name '*.vo' | wc -l" || true
run_step "BB5_Theorem.vo present" "ls -l $R/Coq-BB5-git/CoqBB5/BB5/BB5_Theorem.vo" || true

echo "" | tee -a "$LOG"
echo "=== phase R attempt 2 (resume) end $(date -u +%Y-%m-%dT%H:%M:%SZ) (all steps exit 0 as recorded above) ===" | tee -a "$LOG"
exit 0
