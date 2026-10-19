#!/usr/bin/env bash
# =============================================================================
# TEMP-ONLY P2 execution runner (lives in Temp\opencode\p2exec\; not committed).
# Runs the FROZEN commands of reports/AUDIT_COLLATZ_PREREG_2026-10-19.md,
# one item per invocation:
#   bash p2_steps.sh <s1|s2|s3|s4|h|s5|w1|w2|esetup|e2|e3|e1>
# All stdout/stderr is appended to the P2 log via tee (single writer: this
# script). Windows tools (curl.exe 8.13.0, Windows git 2.53.0) are invoked via
# WSL interop with Windows-form paths; the CMD lines show the exact command.
# =============================================================================
set -u
cd "/mnt/d/Opencode AI Agent" || { echo "cannot cd"; exit 1; }
D=$(date -u +%Y-%m-%d)
LOG="reports/AUDIT_COLLATZ_LOG_${D}.log"
EXEC="audit_collatz/exec_${D}"
WEXEC="D:/Opencode AI Agent/audit_collatz/exec_${D}"
CURL="/mnt/c/Windows/System32/curl.exe"
GIT="/mnt/c/Program Files/Git/cmd/git.exe"
[ -f "$LOG" ] || { echo "STOP: log not opened"; exit 1; }

r(){ # r "<command>"  -> echo CMD, run under nice -n 19, echo EXIT
  echo "CMD: $1"
  nice -n 19 bash -c "$1"
  echo "EXIT: $?"
}
hdr(){ echo; echo "--- $(date -u +%Y-%m-%dT%H:%M:%SZ) | $1 ---"; }

s1(){
  hdr "S1 site re-fetch and byte-compare (frozen prereg §4)"
  mkdir -p "$EXEC/refetch"
  r "\"$CURL\" -fsSL -w \"%{http_code}\\n\" -o \"$WEXEC/refetch/site_path_records.html\" https://pcbarina.fit.vutbr.cz/path-records.htm"
  r "\"$CURL\" -fsSL -w \"%{http_code}\\n\" -o \"$WEXEC/refetch/site_news.html\" https://pcbarina.fit.vutbr.cz/news.htm"
  r "\"$CURL\" -fsSL -w \"%{http_code}\\n\" -o \"$WEXEC/refetch/site_main.html\" https://pcbarina.fit.vutbr.cz/"
  r "cmp \"$EXEC/refetch/site_path_records.html\" audit_collatz/captures/site_path_records.html"
  r "cmp \"$EXEC/refetch/site_news.html\" audit_collatz/captures/site_news.html"
  r "sed -E 's/Generated: [^<]*/Generated: X/' \"$EXEC/refetch/site_main.html\" > \"$EXEC/n_main_refetched\""
  r "sed -E 's/Generated: [^<]*/Generated: X/' audit_collatz/captures/site_main.html > \"$EXEC/n_main_frozen\""
  r "cmp \"$EXEC/n_main_refetched\" \"$EXEC/n_main_frozen\""
}

s2(){
  hdr "S2 OEIS re-fetch and byte-compare (frozen prereg §4)"
  r "\"$CURL\" -fsSL -w \"%{http_code}\\n\" -o \"$WEXEC/refetch/oeis_A006884.txt\" https://oeis.org/A006884/b006884.txt"
  r "\"$CURL\" -fsSL -w \"%{http_code}\\n\" -o \"$WEXEC/refetch/oeis_A006885.txt\" https://oeis.org/A006885/b006885.txt"
  r "\"$CURL\" -fsSL -w \"%{http_code}\\n\" -o \"$WEXEC/refetch/oeis_A006877.txt\" https://oeis.org/A006877/b006877.txt"
  r "\"$CURL\" -fsSL -w \"%{http_code}\\n\" -o \"$WEXEC/refetch/oeis_A006878.txt\" https://oeis.org/A006878/b006878.txt"
  r "cmp \"$EXEC/refetch/oeis_A006884.txt\" audit_collatz/captures/oeis_A006884.txt"
  r "cmp \"$EXEC/refetch/oeis_A006885.txt\" audit_collatz/captures/oeis_A006885.txt"
  r "cmp \"$EXEC/refetch/oeis_A006877.txt\" audit_collatz/captures/oeis_A006877.txt"
  r "cmp \"$EXEC/refetch/oeis_A006878.txt\" audit_collatz/captures/oeis_A006878.txt"
}

s3(){
  hdr "S3 clone at the pin (frozen prereg §4; git = Windows git.exe via interop)"
  r "\"$GIT\" -c core.autocrlf=false clone https://github.com/xbarin02/collatz.git \"$WEXEC/clone\""
  r "\"$GIT\" -c core.autocrlf=false -C \"$WEXEC/clone\" checkout --detach e98d0294a7ff77e783907e307a80e83b92f4a164"
  r "\"$GIT\" -C \"$WEXEC/clone\" rev-parse HEAD"
  r "\"$GIT\" -C \"$WEXEC/clone\" rev-parse 'HEAD^{tree}'"
}

s4(){
  hdr "S4/P pinned archive fetch + weld (frozen prereg §4)"
  r "\"$CURL\" -fsSL -w \"%{http_code}\\n\" -o \"$WEXEC/collatz-e98d0294.tar.gz\" https://codeload.github.com/xbarin02/collatz/tar.gz/e98d0294a7ff77e783907e307a80e83b92f4a164"
  r "python3 audit_bb5/artifact_checks.py sha256lf \"$EXEC/collatz-e98d0294.tar.gz\""
  r "python3 audit_bb5/artifact_checks.py weld-tar \"$EXEC/collatz-e98d0294.tar.gz\" \"$EXEC/clone\" --out \"$EXEC/weld.json\""
}

h(){
  hdr "H1+H2 textual claims (frozen prereg §7)"
  r "python3 audit_collatz/claims_check.py audit_collatz/claims_site.tsv \"$EXEC/refetch\""
  r "python3 audit_collatz/claims_check.py audit_collatz/claims_repo.tsv \"$EXEC/clone\""
}

s5(){
  hdr "S5 battery re-derivation (frozen prereg §4)"
  r "python3 audit_collatz/build_batteries.py \"$EXEC/refetch\" \"$EXEC/batteries_re\""
  r "cmp \"$EXEC/batteries_re/battery_path_records.tsv\" audit_collatz/battery_path_records.tsv"
  r "cmp \"$EXEC/batteries_re/battery_heights_std_a006885.tsv\" audit_collatz/battery_heights_std_a006885.tsv"
  r "cmp \"$EXEC/batteries_re/battery_delay_records.tsv\" audit_collatz/battery_delay_records.tsv"
}

w1(){
  hdr "W1a/W1b records replay P/Q (frozen prereg §5)"
  r "python3 audit_collatz/collatz_engine_p.py w1 --path-battery audit_collatz/battery_path_records.tsv --std-battery audit_collatz/battery_heights_std_a006885.tsv --out \"$EXEC/w1_p_r1.json\""
  r "python3 audit_collatz/collatz_engine_p.py w1 --path-battery audit_collatz/battery_path_records.tsv --std-battery audit_collatz/battery_heights_std_a006885.tsv --out \"$EXEC/w1_p_r2.json\""
  r "python3 audit_collatz/collatz_tools.py compare \"$EXEC/w1_p_r1.json\" \"$EXEC/w1_p_r2.json\""
  r "python3 audit_collatz/collatz_engine_q.py w1 --path-battery audit_collatz/battery_path_records.tsv --std-battery audit_collatz/battery_heights_std_a006885.tsv --out \"$EXEC/w1_q_r1.json\""
  r "python3 audit_collatz/collatz_engine_q.py w1 --path-battery audit_collatz/battery_path_records.tsv --std-battery audit_collatz/battery_heights_std_a006885.tsv --out \"$EXEC/w1_q_r2.json\""
  r "python3 audit_collatz/collatz_tools.py compare \"$EXEC/w1_q_r1.json\" \"$EXEC/w1_q_r2.json\""
  r "python3 audit_collatz/collatz_tools.py compare \"$EXEC/w1_p_r1.json\" \"$EXEC/w1_q_r1.json\""
}

w2(){
  hdr "W2 delay records replay P/Q (frozen prereg §5)"
  r "python3 audit_collatz/collatz_engine_p.py w2 --battery audit_collatz/battery_delay_records.tsv --out \"$EXEC/w2_p_r1.json\""
  r "python3 audit_collatz/collatz_engine_p.py w2 --battery audit_collatz/battery_delay_records.tsv --out \"$EXEC/w2_p_r2.json\""
  r "python3 audit_collatz/collatz_tools.py compare \"$EXEC/w2_p_r1.json\" \"$EXEC/w2_p_r2.json\""
  r "python3 audit_collatz/collatz_engine_q.py w2 --battery audit_collatz/battery_delay_records.tsv --out \"$EXEC/w2_q_r1.json\""
  r "python3 audit_collatz/collatz_engine_q.py w2 --battery audit_collatz/battery_delay_records.tsv --out \"$EXEC/w2_q_r2.json\""
  r "python3 audit_collatz/collatz_tools.py compare \"$EXEC/w2_q_r1.json\" \"$EXEC/w2_q_r2.json\""
  r "python3 audit_collatz/collatz_tools.py compare \"$EXEC/w2_p_r1.json\" \"$EXEC/w2_q_r1.json\""
}

esetup(){
  hdr "E setup: C engine build (frozen prereg §6; counts against setup cap)"
  r "gcc --version | head -n1"
  r "gcc -O2 -std=gnu11 -o \"$EXEC/collatz_sweep\" audit_collatz/collatz_sweep.c"
  r "sha256sum \"$EXEC/collatz_sweep\""
}

e2(){
  hdr "E2 2^24 cross-check C vs Python (frozen prereg §6)"
  r "\"$EXEC/collatz_sweep\" drop 24 --out \"$EXEC/c_drop24.json\""
  r "python3 audit_collatz/collatz_engine_p.py e2 --bound 16777216 --out \"$EXEC/p_e2_24.json\""
  r "python3 audit_collatz/collatz_tools.py compare-prefix \"$EXEC/c_drop24.json\" \"$EXEC/p_e2_24.json\""
}

e3(){
  hdr "E3 records prefix at 2^24 (frozen prereg §6)"
  r "python3 audit_collatz/collatz_engine_p.py e3 --bound 16777216 --path-battery audit_collatz/battery_path_records.tsv --out \"$EXEC/p_e3_24.json\""
  r "\"$EXEC/collatz_sweep\" records 24 --out \"$EXEC/c_rec24.json\""
  r "python3 audit_collatz/collatz_tools.py compare-fields \"$EXEC/p_e3_24.json\" \"$EXEC/c_rec24.json\" records record_count"
  r "python3 audit_collatz/collatz_tools.py check-prefix \"$EXEC/c_rec24.json\" audit_collatz/battery_path_records.tsv"
}

e1(){
  hdr "E1 2^34 sweep (frozen prereg §6; hard wall 3.5 h via timeout -s INT 12600)"
  echo "note: timeout wrapper implements the pre-registered hard wall (SIGINT at 3.5 h; exit 124 recorded as-is)."
  r "timeout -s INT 12600 \"$EXEC/collatz_sweep\" drop 34 --out \"$EXEC/c_drop34.json\""
  if [ -f "$EXEC/c_drop34.json" ]; then
    r "python3 audit_collatz/collatz_tools.py compare-prefix \"$EXEC/c_drop34.json\" \"$EXEC/c_drop24.json\""
  else
    echo "c_drop34.json not produced (interrupted or failed) -- prefix compare skipped, recorded as not produced (prereg §6)."
  fi
}

run_it(){
  case "${1:-}" in
    s1) s1 ;;
    s2) s2 ;;
    s3) s3 ;;
    s4) s4 ;;
    h)  h ;;
    s5) s5 ;;
    w1) w1 ;;
    w2) w2 ;;
    esetup) esetup ;;
    e2) e2 ;;
    e3) e3 ;;
    e1) e1 ;;
    *) echo "usage: bash p2_steps.sh <s1|s2|s3|s4|h|s5|w1|w2|esetup|e2|e3|e1>"; exit 2 ;;
  esac
}
run_it "$@" 2>&1 | tee -a "$LOG"
