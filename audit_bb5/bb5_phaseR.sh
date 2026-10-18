#!/usr/bin/env bash
# BB(5) phase R runner -- executes AFTER the pre-registration header commit.
# Appends block-by-block to reports/audit_bb5_phaseR_2026-10-18.log.
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

abort() { echo "=== phase R ABORT: $1 $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"; exit "$2"; }

{
  echo ""
  echo "=== phase R run start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  echo "runner: /root/bb5r/bb5_phaseR.sh sha256 $(sha256sum "$0" | awk '{print $1}')"
  cmp -s "$0" "/mnt/d/Opencode AI Agent/audit_bb5/bb5_phaseR.sh" && echo "runner copy == repo copy (byte-identical)" || echo "WARNING: runner copy differs from repo copy"
  echo "nproc: $(nproc)"
  grep -m1 'model name' /proc/cpuinfo || true
  free -h | head -2
  df -h / | tail -1
  echo "$(($(date +%s) + 61200))" > "$R/deadline_epoch"
  echo "watchdog deadline epoch: $(cat "$R/deadline_epoch") (run start + 17h backstop)"
  ( cd '/mnt/d/Opencode AI Agent' && echo "T-hat-N repo_commit: $(git rev-parse HEAD)" ) || echo "T-hat-N repo_commit: n/a"
} | tee -a "$LOG"

run_step "clone verify/repair (HEAD / tree / status)" "if [ ! -d $R/Coq-BB5-git ]; then mkdir -p $R; git clone https://github.com/ccz181078/Coq-BB5.git $R/Coq-BB5-git; fi; git -C $R/Coq-BB5-git checkout --detach 9142e219229baf2245d3f70851947230ea28a318; git -C $R/Coq-BB5-git rev-parse HEAD && git -C $R/Coq-BB5-git rev-parse 'HEAD^{tree}' && git -C $R/Coq-BB5-git status --porcelain | head -3" || abort "clone verify" 11

run_step "apt install opam + build tools" "apt-get update -qq && apt-get install -y -qq opam build-essential m4 unzip pkg-config" || abort "apt" 12

run_step "opam --version" "opam --version" || true

run_step "opam init (bare; sandboxing off)" "opam init --disable-sandboxing --bare -y" || abort "opam init" 13

run_step "opam switch create 4.14.2" "opam switch create 4.14.2 -y" || abort "switch create" 14

ENVOUT="$(opam env --shell=bash 2>&1)"; envrc=$?
{ echo ""; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | opam env (eval in runner)"; echo "CMD: opam env --shell=bash"; echo "$ENVOUT"; echo "EXIT: $envrc"; } | tee -a "$LOG"
[ $envrc -eq 0 ] || abort "opam env" 15
eval "$ENVOUT"

run_step "coqc before install (expect absent)" "which coqc || echo coqc-not-yet"

run_step "opam pin add coq 8.20.1 (install/build Coq)" "opam pin add coq 8.20.1 -y" || abort "coq 8.20.1 install" 16

run_step "coqc --version (expect 8.20.1)" "coqc --version" || abort "coqc" 17

run_step "build BusyCoq (make -j4)" "cd $R/Coq-BB5-git/BusyCoq && time make -j4" || abort "BusyCoq build" 18

run_step "build CoqBB5/BB5 (make -j4)" "cd $R/Coq-BB5-git/CoqBB5/BB5 && time make -j4" || abort "BB5 build" 19

run_step "assumptions marker extract (self-grep)" "grep -n -E 'Print Assumptions|functional_extensionality|Axioms:|Assumptions:' \"$LOG\" | tail -40" || true

run_step "count .vo (BusyCoq)" "find $R/Coq-BB5-git/BusyCoq -name '*.vo' | wc -l" || true
run_step "count .vo (BB5)" "find $R/Coq-BB5-git/CoqBB5/BB5 -name '*.vo' | wc -l" || true
run_step "BB5_Theorem.vo present" "ls -l $R/Coq-BB5-git/CoqBB5/BB5/BB5_Theorem.vo" || true

echo "" | tee -a "$LOG"
echo "=== phase R run end $(date -u +%Y-%m-%dT%H:%M:%SZ) (all steps exit 0 as recorded above) ===" | tee -a "$LOG"
exit 0
