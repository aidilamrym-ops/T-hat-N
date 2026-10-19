#!/usr/bin/env bash
# TEMP-ONLY: append the as-is S3 first-attempt failure note + §9 retry rule to the P2 log.
set -u
cd "/mnt/d/Opencode AI Agent" || exit 1
D=$(date -u +%Y-%m-%d)
LOG="reports/AUDIT_COLLATZ_LOG_${D}.log"
[ -f "$LOG" ] || { echo "STOP: log not found"; exit 1; }
{
  echo
  echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | NOTE: S3 first attempt failed mid-transfer (git exit 128: 'RPC failed; curl 56 Recv failure: Connection was reset'; 'fatal: early EOF'); the partially created clone directory was removed by git itself; per prereg §9 the exact command block is rerun once, recorded as-is; no parameters changed. ---"
} >> "$LOG"
echo "s3 retry note appended."
