#!/usr/bin/env bash
# RR-2026-01 V1 ECDSA execution runner (mechanical).
# The commands below are exactly the frozen prereg section 3 steps.
# Sequential; everything appended to the log via tee; STOP after I1 if it fails.
set -o pipefail
cd "/mnt/d/Opencode AI Agent" || exit 9
LOG="reports/AUDIT_ECDSA_LOG_2026-10-19.log"
EXEC="audit_ecdsa/exec_2026-10-19"
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }

{
echo "=== RR-2026-01 execution start $(ts) ==="
echo "host: $(uname -sr) / $(lsb_release -ds 2>/dev/null) / gcc $(gcc -dumpversion) / python $(python3 -V 2>&1 | cut -d' ' -f2) / nice $(nice --version 2>/dev/null | head -1)"

echo "--- step 0: pin check + build $(ts) ---"
mkdir -p "$EXEC"
echo "$ sha256sum -c audit_ecdsa/PINS.sha256"
sha256sum -c audit_ecdsa/PINS.sha256 || echo "STEP0-PINCHECK-FAILED"
echo "$ gcc -O2 -std=gnu11 -o $EXEC/e1  audit_ecdsa/engine_e1.c"
gcc -O2 -std=gnu11 -o "$EXEC/e1"  audit_ecdsa/engine_e1.c || echo "STEP0-BUILD1-FAILED"
echo "$ gcc -O2 -std=gnu11 -o $EXEC/e1w audit_ecdsa/engine_e1w.c"
gcc -O2 -std=gnu11 -o "$EXEC/e1w" audit_ecdsa/engine_e1w.c || echo "STEP0-BUILD2-FAILED"
echo "$ sha256sum $EXEC/e1 $EXEC/e1w"
sha256sum "$EXEC/e1" "$EXEC/e1w"

echo "--- I1: engine selftests $(ts) ---"
echo "$ nice -n 19 python3 audit_ecdsa/selftest_v1.py --e1 $EXEC/e1 --e1w $EXEC/e1w --e2 audit_ecdsa/engine_e2.py --json $EXEC/i1_selftest.json"
nice -n 19 python3 audit_ecdsa/selftest_v1.py --e1 "$EXEC/e1" --e1w "$EXEC/e1w" --e2 audit_ecdsa/engine_e2.py --json "$EXEC/i1_selftest.json"
I1RC=$?
echo "I1 rc=$I1RC"
if [ "$I1RC" -ne 0 ]; then
  echo "STOP: I1 failed; no further items run (per prereg)."
  echo "=== RR-2026-01 execution halted $(ts) ==="
  exit 1
fi

echo "--- I2: prime rows (R01-R10) $(ts) ---"
echo "$ nice -n 19 python3 audit_ecdsa/run_v1.py i2 --manifest audit_ecdsa/seeds_manifest.json --e1 $EXEC/e1 --e2 audit_ecdsa/engine_e2.py --out $EXEC/i2_prime.json"
nice -n 19 python3 audit_ecdsa/run_v1.py i2 --manifest audit_ecdsa/seeds_manifest.json --e1 "$EXEC/e1" --e2 audit_ecdsa/engine_e2.py --out "$EXEC/i2_prime.json"
echo "I2 rc=$?"

echo "--- I3: binary rows (R11-R14) $(ts) ---"
echo "$ nice -n 19 python3 audit_ecdsa/run_v1.py i3 --manifest audit_ecdsa/seeds_manifest.json --e1 $EXEC/e1 --e2 audit_ecdsa/engine_e2.py --out $EXEC/i3_binary.json"
nice -n 19 python3 audit_ecdsa/run_v1.py i3 --manifest audit_ecdsa/seeds_manifest.json --e1 "$EXEC/e1" --e2 audit_ecdsa/engine_e2.py --out "$EXEC/i3_binary.json"
echo "I3 rc=$?"

echo "--- I4: word-structure statistic (C3) $(ts) ---"
echo "$ nice -n 19 python3 audit_ecdsa/run_v1.py i4 --manifest audit_ecdsa/seeds_manifest.json --out $EXEC/i4_wordstats.json"
nice -n 19 python3 audit_ecdsa/run_v1.py i4 --manifest audit_ecdsa/seeds_manifest.json --out "$EXEC/i4_wordstats.json"
echo "I4 rc=$?"

echo "--- I5: timestamp arithmetic (C4) $(ts) ---"
echo "$ nice -n 19 python3 audit_ecdsa/run_v1.py i5 --manifest audit_ecdsa/seeds_manifest.json --out $EXEC/i5_timestamps.json"
nice -n 19 python3 audit_ecdsa/run_v1.py i5 --manifest audit_ecdsa/seeds_manifest.json --out "$EXEC/i5_timestamps.json"
echo "I5 rc=$?"

echo "--- I6: sources + packaging $(ts) ---"
echo "$ nice -n 19 python3 audit_ecdsa/run_v1.py i6 --manifest audit_ecdsa/seeds_manifest.json --out $EXEC/i6_sources.json"
nice -n 19 python3 audit_ecdsa/run_v1.py i6 --manifest audit_ecdsa/seeds_manifest.json --out "$EXEC/i6_sources.json"
echo "I6 rc=$?"

echo "--- exec artifact hashes (log certificates computed later) $(ts) ---"
sha256sum "$EXEC/e1" "$EXEC/e1w" "$EXEC/i1_selftest.json" "$EXEC/i2_prime.json" "$EXEC/i3_binary.json" "$EXEC/i4_wordstats.json" "$EXEC/i5_timestamps.json" "$EXEC/i6_sources.json"
echo "=== RR-2026-01 execution end $(ts) ==="
} 2>&1 | tee -a "$LOG"
