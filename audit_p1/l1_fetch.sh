#!/usr/bin/env bash
# audit_p1 L1 replay - step 1: fetch the pinned release inputs and verify digests.
# Runs inside the audit WSL2 distro (Ubuntu); appends evidence to the replay log.
# Inputs come only from the public immutable release assets; nothing is fetched from a registry.
set -u

LOG='/mnt/d/Opencode AI Agent/reports/audit_p1_l1_replay_2026-10-18.log'
BASE='https://github.com/judegomila/dbn-lambda-01787854-candidate-audit/releases/download/review-01787854-v3'
WORK=/root/l1
EXP_OCI='87a4695e86b535eac48b0a39e1999028e8a18249eb1c95cc9715e4a91afb83c6'
EXP_BUNDLE='34f8f5239c56b9602d47800f0cac4ef9ee995f845298362fb4a2a95740c5ba92'

mark() { printf '\n--- %s | %s\nCMD: %s\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" "$1" "$2" >>"$LOG"; }
foot() { printf 'EXIT: %s\n' "$1" >>"$LOG"; }

mkdir -p "$WORK"
fail=0

printf '\nscript: %s sha256 %s\n' "$0" "$(sha256sum "$0" | cut -d' ' -f1)" >>"$LOG"

mark 'fetch: OCI archive' "curl -fsSL --retry 3 -o $WORK/dbn-lambda-01787854-review-v3.oci.tar $BASE/dbn-lambda-01787854-review-v3.oci.tar"
curl -fsSL --retry 3 -o "$WORK/dbn-lambda-01787854-review-v3.oci.tar" "$BASE/dbn-lambda-01787854-review-v3.oci.tar" >/tmp/l1_fetch.out 2>&1; rc=$?
cat /tmp/l1_fetch.out >>"$LOG"; foot "$rc"; [ "$rc" -eq 0 ] || fail=1

mark 'verify: OCI archive size' "stat -c %s $WORK/dbn-lambda-01787854-review-v3.oci.tar"
stat -c %s "$WORK/dbn-lambda-01787854-review-v3.oci.tar" >>"$LOG" 2>&1; foot "$?"

mark 'verify: OCI archive sha256 (expected 87a4695e86b535eac48b0a39e1999028e8a18249eb1c95cc9715e4a91afb83c6)' "sha256sum $WORK/dbn-lambda-01787854-review-v3.oci.tar"
oci_sha=$(sha256sum "$WORK/dbn-lambda-01787854-review-v3.oci.tar" | cut -d' ' -f1); rc=$?
printf '%s\n' "$oci_sha" >>"$LOG"
if [ "$oci_sha" = "$EXP_OCI" ]; then printf 'VERDICT: sha256 MATCH\n' >>"$LOG"; else printf 'VERDICT: sha256 MISMATCH\n' >>"$LOG"; fail=1; fi
foot "$rc"

mark 'fetch: git bundle (release tree carrier)' "curl -fsSL --retry 3 -o $WORK/dbn-lambda-01787854-review-v3.bundle $BASE/dbn-lambda-01787854-review-v3.bundle"
curl -fsSL --retry 3 -o "$WORK/dbn-lambda-01787854-review-v3.bundle" "$BASE/dbn-lambda-01787854-review-v3.bundle" >/tmp/l1_fetch.out 2>&1; rc=$?
cat /tmp/l1_fetch.out >>"$LOG"; foot "$rc"; [ "$rc" -eq 0 ] || fail=1

mark 'verify: bundle sha256 (expected 34f8f5239c56b9602d47800f0cac4ef9ee995f845298362fb4a2a95740c5ba92)' "sha256sum $WORK/dbn-lambda-01787854-review-v3.bundle"
bun_sha=$(sha256sum "$WORK/dbn-lambda-01787854-review-v3.bundle" | cut -d' ' -f1); rc=$?
printf '%s\n' "$bun_sha" >>"$LOG"
if [ "$bun_sha" = "$EXP_BUNDLE" ]; then printf 'VERDICT: sha256 MATCH\n' >>"$LOG"; else printf 'VERDICT: sha256 MISMATCH\n' >>"$LOG"; fail=1; fi
foot "$rc"

if [ "$fail" -eq 0 ]; then printf '\nRESULT: FETCH-AND-VERIFY OK\n' >>"$LOG"; else printf '\nRESULT: FETCH-AND-VERIFY FAILED\n' >>"$LOG"; fi
exit "$fail"
