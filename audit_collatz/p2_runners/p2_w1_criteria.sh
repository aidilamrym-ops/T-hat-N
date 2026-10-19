#!/usr/bin/env bash
# TEMP-ONLY: extract and append the W1a/W1b criteria fields from the W1 result JSONs (prereg §5).
set -u
cd "/mnt/d/Opencode AI Agent" || exit 1
D=$(date -u +%Y-%m-%d)
LOG="reports/AUDIT_COLLATZ_LOG_${D}.log"
EXEC="audit_collatz/exec_${D}"
[ -f "$LOG" ] || { echo "STOP: log not found"; exit 1; }
{
  echo
  echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | W1 CRITERIA extraction from result JSONs (prereg §5) ---"
  python3 - "$EXEC" <<'PY'
import json, sys
exec_dir = sys.argv[1].replace("\\", "/")
for name in ("w1_p_r1", "w1_q_r1"):
    with open("%s/%s.json" % (exec_dir, name)) as fh:
        d = json.load(fh)
    print("%s: top-level keys = %s" % (name, sorted(d.keys())))
    for key in ("mismatch_path", "mismatch_std", "cap_hits", "path_checked", "std_checked"):
        v = d.get(key, "MISSING")
        s = json.dumps(v)
        if len(s) > 240:
            s = s[:240] + "...(%d chars total)" % len(s)
        print("  %s = %s" % (key, s))
PY
  echo "--- end W1 criteria ---"
} >> "$LOG"
echo "w1 criteria appended."
