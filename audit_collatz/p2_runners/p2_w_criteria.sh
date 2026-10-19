#!/usr/bin/env bash
# TEMP-ONLY: append the W1/W2 criteria extraction (fields under top-level "result";
# schema-corrected; the first W1 extraction attempt printed MISSING for these fields
# and is kept in the log as-is).
set -u
cd "/mnt/d/Opencode AI Agent" || exit 1
D=$(date -u +%Y-%m-%d)
LOG="reports/AUDIT_COLLATZ_LOG_${D}.log"
EXEC="audit_collatz/exec_${D}"
[ -f "$LOG" ] || { echo "STOP: log not found"; exit 1; }
{
  echo
  echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | W1/W2 CRITERIA extraction, schema-corrected (fields live under top-level \"result\"; first W1 extraction attempt printed MISSING for result-nested fields and is kept as-is) ---"
  python3 - "$EXEC" <<'PY'
import json, sys
exec_dir = sys.argv[1].replace("\\", "/")
checks = [
    ("w1_p_r1", ("mismatch_path", "mismatch_std", "cap_hits", "path_checked", "std_checked")),
    ("w1_q_r1", ("mismatch_path", "mismatch_std", "cap_hits", "path_checked", "std_checked")),
    ("w2_p_r1", ("mismatches", "cap_hits", "checked")),
    ("w2_q_r1", ("mismatches", "cap_hits", "checked")),
]
for name, keys in checks:
    with open("%s/%s.json" % (exec_dir, name)) as fh:
        d = json.load(fh)
    r = d.get("result", {})
    print("%s:" % name)
    for key in keys:
        v = r.get(key, "MISSING")
        s = json.dumps(v)
        if len(s) > 200:
            s = s[:200] + "...(%d chars total)" % len(s)
        print("  %s = %s" % (key, s))
PY
  echo "--- end W1/W2 criteria ---"
} >> "$LOG"
echo "w1/w2 criteria appended."
