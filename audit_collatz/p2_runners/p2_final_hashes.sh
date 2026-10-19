#!/usr/bin/env bash
# TEMP-ONLY: post-E1 summary + sha256LF of the frozen log and executed artifacts.
# Prints to stdout only (the audit log is frozen at this point; nothing is appended).
set -u
cd "/mnt/d/Opencode AI Agent" || exit 1
D=2026-10-19
LOG="reports/AUDIT_COLLATZ_LOG_${D}.log"
EXEC="audit_collatz/exec_${D}"
FILES=(
  "$LOG"
  "$EXEC/w1_p_r1.json" "$EXEC/w1_p_r2.json" "$EXEC/w1_q_r1.json" "$EXEC/w1_q_r2.json"
  "$EXEC/w2_p_r1.json" "$EXEC/w2_p_r2.json" "$EXEC/w2_q_r1.json" "$EXEC/w2_q_r2.json"
  "$EXEC/c_drop24.json" "$EXEC/p_e2_24.json" "$EXEC/p_e3_24.json" "$EXEC/c_rec24.json"
  "$EXEC/weld.json" "$EXEC/refetch/battery_build_report.txt"
)
if [ -f "$EXEC/c_drop34.json" ]; then FILES+=("$EXEC/c_drop34.json"); fi
echo "=== E1 block: control lines ==="
awk '/\| E1 2\^34 sweep/{f=1} f && (/^CMD:/ || /^EXIT:/ || /^MATCH/ || /^MISMATCH/ || /^--- / || /^note:/ || /not produced/){print}' "$LOG"
echo "=== E1: last 4 progress lines in log ==="
grep -a '^progress' "$LOG" | tail -n 4
echo "=== E1: c_drop34.json (if present) ==="
if [ -f "$EXEC/c_drop34.json" ]; then cat "$EXEC/c_drop34.json"; else echo "(absent)"; fi
echo "=== sha256LF list ==="
python3 audit_bb5/artifact_checks.py sha256lf "${FILES[@]}"
echo "=== sizes ==="
wc -l -c "$LOG"
du -sh "$EXEC" "$EXEC/clone" "$EXEC/refetch" 2>/dev/null
ls -l "$EXEC/collatz-e98d0294.tar.gz" "$EXEC/collatz_sweep" 2>/dev/null
echo "=== S3 retry block: control lines ==="
awk '/NOTE: S3 first attempt/{f=1} f && (/^--- / || /^EXIT:/ || /^CMD:/){print}' "$LOG" | head -n 16
echo "=== S4 investigation block (for report; up to 80 lines) ==="
sed -n '/S4 INVESTIGATION/,/W1a\/W1b/p' "$LOG" | head -n 80
echo "=== all block headers ==="
grep -n '^--- ' "$LOG"
