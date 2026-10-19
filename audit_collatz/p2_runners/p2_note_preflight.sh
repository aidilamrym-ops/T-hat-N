#!/usr/bin/env bash
# TEMP-ONLY: append the as-is P2 preflight record to the P2 log.
# Run exactly once, right after p2_open_log.sh created the log.
set -u
cd "/mnt/d/Opencode AI Agent" || exit 1
D=$(date -u +%Y-%m-%d)
LOG="reports/AUDIT_COLLATZ_LOG_${D}.log"
[ -f "$LOG" ] || { echo "STOP: log not found"; exit 1; }
{
  echo
  echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | PREFLIGHT (PowerShell; recorded as-is; run before open) ---"
  echo "STATUS_PORCELAIN: []"
  echo "HEAD: 9d9c358798ab4859dd024759bedd8b90cc4aac6c"
  echo "git merge-base --is-ancestor bbbe9ae HEAD -> exit 0"
  echo "git diff --quiet bbbe9ae HEAD -- reports/AUDIT_COLLATZ_PREREG_2026-10-19.md -> exit 0"
  echo "git ls-remote origin main -> 9d9c358798ab4859dd024759bedd8b90cc4aac6c refs/heads/main (origin/main == HEAD)"
  echo "CI run 39181863147 (push 9d9c358): python-tests success (1m13s); lean-kernel success (2m10s)"
  echo "Windows git: C:\\Program Files\\Git\\cmd\\git.exe (git version 2.53.0.windows.3)"
  echo "--- end preflight ---"
} >> "$LOG"
echo "preflight note appended."
