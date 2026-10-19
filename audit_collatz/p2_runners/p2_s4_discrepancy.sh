#!/usr/bin/env bash
# TEMP-ONLY: S4/P discrepancy record + prereg §9 exact-command rerun + in-budget
# investigation. All output is appended to the P2 log as-is.
set -u
cd "/mnt/d/Opencode AI Agent" || exit 1
D=$(date -u +%Y-%m-%d)
LOG="reports/AUDIT_COLLATZ_LOG_${D}.log"
EXEC="audit_collatz/exec_${D}"
WEXEC="D:/Opencode AI Agent/audit_collatz/exec_${D}"
GIT="/mnt/c/Program Files/Git/cmd/git.exe"
[ -f "$LOG" ] || { echo "STOP: log not found"; exit 1; }

r(){ echo "CMD: $1"; nice -n 19 bash -c "$1"; echo "EXIT: $?"; }
hdr(){ echo; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | $1 ---"; }

main(){
  hdr "S4/P DISCREPANCY (§9): observed only_in_clone=15, identical=147 vs frozen expectation 0/162 -- exact-command rerun, then in-budget investigation, all recorded as-is; no parameters changed"
  r "python3 audit_bb5/artifact_checks.py weld-tar \"$EXEC/collatz-e98d0294.tar.gz\" \"$EXEC/clone\" --out \"$EXEC/weld.json\""
  hdr "S4 INVESTIGATION (§9, in budget): (1) tar member types for the 15 paths; (2) clone ls-tree mode-120000 list; (3) symlink counts both sides; (4) sample materialized files' content (= link targets); (5) clone entry count"
  r "tar -tvzf \"$EXEC/collatz-e98d0294.tar.gz\" | grep -E 'compat\.h|wideint\.h|kernel\.cl'"
  r "\"$GIT\" -C \"$WEXEC/clone\" ls-tree -r HEAD | grep '^120000'"
  r "\"$GIT\" -C \"$WEXEC/clone\" ls-tree -r HEAD | grep -c '^120000'"
  r "tar -tvzf \"$EXEC/collatz-e98d0294.tar.gz\" | grep -c '^l'"
  r "cat \"$EXEC/clone/src/worker/wideint.h\" \"$EXEC/clone/src/gpuworker/kernel.cl\""
  r "\"$GIT\" -C \"$WEXEC/clone\" ls-tree -r HEAD | wc -l"
}
main 2>&1 | tee -a "$LOG"
