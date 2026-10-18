#!/usr/bin/env bash
# audit_p1 L1 sweep - step 3 (optional full sweep, prereg section 8; owner-selected
# 2026-10-18): executes the pinned release's own scripts/run_full_sweep.sh
# (complete finite-triangle replay N=690988..3840000, 3,149,013 rows) against the
# pinned image loaded from the verified OCI archive.
# Runs inside the audit WSL2 distro (Ubuntu) as root; appends evidence to the sweep log.
# Environment delta (recorded pre-execution): docker CLI absent -> /usr/local/bin/docker
# shim exec'ing podman; IMAGE + EXPECTED_IMAGE_ID pinned to values measured on this engine.
set -u

LOG='/mnt/d/Opencode AI Agent/reports/audit_p1_l1_sweep_2026-10-18.log'
WORK=/root/l1
TREE="$WORK/tree"
OUT="$WORK/replay-out/sweep"
EXP_COMMIT='2e9976c4becbf97e31c56fe75fce07cdff5dd4ea'
EXP_TREE='7f15ecf8c3dbc73d547a2d4a3f2287bd87802f44'
IMG='localhost/sha256:6e29bc53adc5a4337802da2b5a219720e3da9dcc1b87c546b96b6126d8b9975d'
EXP_IMAGE_ID='5ccd9e3f7f8fdde6ee6a35c2542efc17b6a7247d615ad03c1db5bd47e3c8f42d'

fail=0

mark() { printf '\n--- %s | %s\nCMD: %s\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" "$1" "$2" >>"$LOG"; }
foot() { printf 'EXIT: %s\n' "$1" >>"$LOG"; }

grep -qF '## machine log (appended as executed)' "$LOG" \
  || printf '## machine log (appended as executed)\n' >>"$LOG"
printf '\nscript: %s sha256 %s\n' "$0" "$(sha256sum "$0" | cut -d' ' -f1)" >>"$LOG"
printf 'repo_commit: %s\n' "$(git -C '/mnt/d/Opencode AI Agent' rev-parse HEAD 2>/dev/null || printf 'unavailable')" >>"$LOG"

# --- step 0: docker shim (environment delta; podman backend)
if ! command -v docker >/dev/null 2>&1; then
  mark 'env: create /usr/local/bin/docker shim -> podman (environment delta, recorded pre-execution)' "printf '#!/bin/sh\nexec podman \"\$@\"\n' > /usr/local/bin/docker; chmod 755 /usr/local/bin/docker"
  printf '#!/bin/sh\nexec podman "$@"\n' > /usr/local/bin/docker
  chmod 755 /usr/local/bin/docker
  printf 'shim: /usr/local/bin/docker sha256 %s\n' "$(sha256sum /usr/local/bin/docker | cut -d' ' -f1)" >>"$LOG"
fi

mark 'env: docker --version (shim -> podman)' 'docker --version'
docker --version >>"$LOG" 2>&1; rc=$?
printf '%s\n' "$(podman --version)" >>"$LOG"
foot "$rc"; [ "$rc" -eq 0 ] || fail=1

# --- step 1: preconditions (pinned tree; pinned image identity; fresh output path)
mark "tree: rev-parse HEAD (expect $EXP_COMMIT)" "git -C $TREE rev-parse HEAD"
git -C "$TREE" rev-parse HEAD >>"$LOG" 2>&1; foot "$?"

mark "tree: rev-parse HEAD^{tree} (expect $EXP_TREE)" "git -C $TREE rev-parse 'HEAD^{tree}'"
git -C "$TREE" rev-parse 'HEAD^{tree}' >>"$LOG" 2>&1; foot "$?"

mark 'tree: status porcelain --untracked-files=all (expect empty; run_full_sweep.sh re-checks)' "git -C $TREE status --porcelain --untracked-files=all"
git -C "$TREE" status --porcelain --untracked-files=all >>"$LOG" 2>&1; foot "$?"

mark "image: inspect .Id (expect $EXP_IMAGE_ID; bare hex as reported by this engine)" "docker image inspect --format '{{.Id}}' $IMG"
got_id=$(docker image inspect --format '{{.Id}}' "$IMG" 2>/tmp/l1_sweep.out); rc=$?
cat /tmp/l1_sweep.out >>"$LOG"
printf '%s\n' "$got_id" >>"$LOG"
if [ "$rc" -eq 0 ] && [ "$got_id" = "$EXP_IMAGE_ID" ]; then
  printf 'VERDICT: image id matches the pinned value\n' >>"$LOG"
else
  printf 'VERDICT: IMAGE ID MISMATCH (pinned %s)\n' "$EXP_IMAGE_ID" >>"$LOG"; fail=1
fi
foot "$rc"

mark 'image: reviewed-build identity labels (fallback path run_full_sweep.sh uses when .Id != sha256:bedf7303...)' "docker image inspect --format label queries (x4) $IMG"
for L in org.opencontainers.image.dbn.platform org.opencontainers.image.base.digest org.opencontainers.image.dbn.ubuntu-snapshot org.opencontainers.image.source; do
  printf '%s = %s\n' "$L" "$(docker image inspect --format '{{index .Config.Labels "'"$L"'"}}' "$IMG" 2>&1)" >>"$LOG"
done
foot 0

mark "output: fresh path check (replay_guard.prepare refuses an existing path): $OUT" "test ! -e $OUT"
test ! -e "$OUT"; rc=$?
[ "$rc" -eq 0 ] && printf 'fresh output path confirmed\n' >>"$LOG"
foot "$rc"; [ "$rc" -eq 0 ] || fail=1

# --- step 2: the sweep (release tooling; complete finite-triangle replay)
mark 'sweep: release scripts/run_full_sweep.sh (optional, prereg section 8; IMAGE + EXPECTED_IMAGE_ID pinned; podman via shim)' "IMAGE=$IMG EXPECTED_IMAGE_ID=$EXP_IMAGE_ID bash $TREE/scripts/run_full_sweep.sh $OUT"
IMAGE="$IMG" EXPECTED_IMAGE_ID="$EXP_IMAGE_ID" bash "$TREE/scripts/run_full_sweep.sh" "$OUT" >/tmp/l1_sweep.out 2>&1; rc=$?
cat /tmp/l1_sweep.out >>"$LOG"; foot "$rc"; [ "$rc" -eq 0 ] || fail=1

# --- step 3: evidence (inventory + release-computed sums + metadata)
mark 'evidence: file inventory of the sweep output directory' "find $OUT -type f -exec sha256sum {} +"
find "$OUT" -type f -exec sha256sum {} + >>"$LOG" 2>&1; foot "$?"

mark 'evidence: REPLAY_METADATA.txt (verbatim)' "cat $OUT/REPLAY_METADATA.txt"
cat "$OUT/REPLAY_METADATA.txt" >>"$LOG" 2>&1; foot "$?"

mark 'evidence: REPLAY_SHA256SUMS (computed by the release script)' "cat $OUT/REPLAY_SHA256SUMS"
cat "$OUT/REPLAY_SHA256SUMS" >>"$LOG" 2>&1; foot "$?"

if [ "$fail" -eq 0 ]; then
  printf '\nRESULT: L1-SWEEP COMPLETE (all steps exit 0 as recorded above)\n' >>"$LOG"
else
  printf '\nRESULT: L1-SWEEP COMPLETE WITH FAILURES (see EXIT lines)\n' >>"$LOG"
fi
exit "$fail"
