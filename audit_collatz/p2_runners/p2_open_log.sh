#!/usr/bin/env bash
# =============================================================================
# DRAFT / TEMP-ONLY  (C:\Users\usER\AppData\Local\Temp\opencode\p2exec\)
# P2 (audit_collatz) execution opener -- mirrors reports/AUDIT_COLLATZ_PREREG_2026-10-19.md §3:
#   "execution starts by creating reports/AUDIT_COLLATZ_LOG_<YYYY-MM-DD>.log
#    (all stdout/stderr appended via tee) and the directory
#    audit_collatz/exec_<YYYY-MM-DD>/ ... First log entries: current date -u,
#    host, git rev-parse HEAD (must equal the commit that pushed this file),
#    sha256LF of the §2(b)/(c) files, sha256 of this file."
#
# RUN ONLY AFTER: (1) BB5 phase R complete, (2) explicit owner signal for P2.
# PREFLIGHT first: see p2_preflight.md (PowerShell, Windows git; do NOT run git
# from WSL). This script runs NO audit item (S/W/E/H/P) -- it only opens the log.
# WSL note: no `git` binary usage here (rule); HEAD is read from .git refs files.
#
# Expected sha256LF values (prereg §2, for eyeball check at execution):
#   battery_path_records.tsv         faa157b296f6fe4924b81eead8dd1182b4104e4af04110075a2bc6f22a0e54ad
#   battery_heights_std_a006885.tsv  9f5bed262520a10bafb292d3f1cf689fc6914062ba70d24cb256e07db28cdbe0
#   battery_delay_records.tsv        09a252407f6cc89e40499b341671014a8622d3c545d2b636b9ec8a1b45f85cf5
#   (8 engine/tool/claims files: see prereg §2(c); all 11 must match §2)
#   artifact_checks.py (reused)      03d69223587e4fcae9ecab30e96931de99ccb531db5e20ff988ba7cfd4762ff4
# =============================================================================
set -u
cd "/mnt/d/Opencode AI Agent" || { echo "cannot cd to repo"; exit 1; }

D=$(date -u +%Y-%m-%d)
LOG="reports/AUDIT_COLLATZ_LOG_${D}.log"
EXEC="audit_collatz/exec_${D}"

if [ -e "$LOG" ]; then echo "REFUSE: $LOG already exists -- stop and inspect."; exit 1; fi
mkdir -p "$EXEC" || exit 1

HEADHASH=""
if [ -f .git/refs/heads/main ]; then
  HEADHASH=$(tr -d ' \r\n' < .git/refs/heads/main)
elif [ -f .git/packed-refs ]; then
  HEADHASH=$(grep -E ' refs/heads/main$' .git/packed-refs | head -n1 | cut -d' ' -f1)
fi

{
  echo "=== audit_collatz exec open $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  echo "date -u: $(date -u)"
  echo "host: $(hostname) / $(uname -sr)"
  echo "HEAD (read from .git refs; no git binary): ${HEADHASH:-UNRESOLVED -- see preflight step 2}"
  echo "NOTE: preflight (PowerShell): HEAD vs bbbe9ae ancestry + prereg blob equality, recorded as-is."
  echo "-- sha256LF of section 2(b)/(c) files (artifact_checks.py, reused unmodified) --"
  python3 audit_bb5/artifact_checks.py sha256lf \
    audit_collatz/battery_path_records.tsv \
    audit_collatz/battery_heights_std_a006885.tsv \
    audit_collatz/battery_delay_records.tsv \
    audit_collatz/collatz_engine_p.py \
    audit_collatz/collatz_engine_q.py \
    audit_collatz/collatz_sweep.c \
    audit_collatz/collatz_tools.py \
    audit_collatz/build_batteries.py \
    audit_collatz/claims_check.py \
    audit_collatz/claims_site.tsv \
    audit_collatz/claims_repo.tsv
  echo "-- sha256 of this prereg file --"
  sha256sum reports/AUDIT_COLLATZ_PREREG_2026-10-19.md
  echo "EXEC DIR: $EXEC"
  echo "=== open block end ==="
} | tee "$LOG"

echo
echo "Log opened: $LOG"
echo "Next: follow prereg sections in order (S -> W -> E -> H -> P), one at a time;"
echo "append every command's stdout/stderr via 'tee -a \"$LOG\"'; nice -n 19."
