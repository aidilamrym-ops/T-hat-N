#!/usr/bin/env bash
# audit_p1 L1 replay - step 2: release tree from bundle, offline podman load,
# verify.sh (stored entry point), container review (image default CMD = fresh critical lanes).
# Runs inside the audit WSL2 distro (Ubuntu) as root; appends evidence to the replay log.
set -u

LOG='/mnt/d/Opencode AI Agent/reports/audit_p1_l1_replay_2026-10-18.log'
WORK=/root/l1
TREE="$WORK/tree"
OUT="$WORK/replay-out"
EXP_COMMIT='2e9976c4becbf97e31c56fe75fce07cdff5dd4ea'
EXP_TREE='7f15ecf8c3dbc73d547a2d4a3f2287bd87802f44'

fail=0

printf '\nscript: %s sha256 %s\n' "$0" "$(sha256sum "$0" | cut -d' ' -f1)" >>"$LOG"

mark() { printf '\n--- %s | %s\nCMD: %s\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" "$1" "$2" >>"$LOG"; }
foot() { printf 'EXIT: %s\n' "$1" >>"$LOG"; }

# --- step 1: release tree from the pinned git bundle
if [ ! -d "$TREE/.git" ]; then
  mark 'tree: git clone from release bundle' "git clone --quiet $WORK/dbn-lambda-01787854-review-v3.bundle $TREE"
  git clone --quiet "$WORK/dbn-lambda-01787854-review-v3.bundle" "$TREE" >/tmp/l1_run.out 2>&1; rc=$?
  cat /tmp/l1_run.out >>"$LOG"; foot "$rc"; [ "$rc" -eq 0 ] || fail=1
fi

mark 'tree: checkout pinned commit' "git -C $TREE checkout --quiet $EXP_COMMIT"
git -C "$TREE" checkout --quiet "$EXP_COMMIT" >/tmp/l1_run.out 2>&1; rc=$?
cat /tmp/l1_run.out >>"$LOG"; foot "$rc"; [ "$rc" -eq 0 ] || fail=1

mark "tree: rev-parse HEAD (expect $EXP_COMMIT)" "git -C $TREE rev-parse HEAD"
git -C "$TREE" rev-parse HEAD >>"$LOG" 2>&1; foot "$?"

mark "tree: rev-parse HEAD^{tree} (expect $EXP_TREE)" "git -C $TREE rev-parse HEAD^{tree}"
git -C "$TREE" rev-parse 'HEAD^{tree}' >>"$LOG" 2>&1; foot "$?"

mark 'tree: status porcelain (expect empty)' "git -C $TREE status --porcelain"
git -C "$TREE" status --porcelain >>"$LOG" 2>&1; foot "$?"

# --- step 2: load the image offline (no registry)
mark 'podman: load release archive (no registry)' "podman load --input $WORK/dbn-lambda-01787854-review-v3.oci.tar"
podman load --input "$WORK/dbn-lambda-01787854-review-v3.oci.tar" >/tmp/l1_run.out 2>&1; rc=$?
cat /tmp/l1_run.out >>"$LOG"; foot "$rc"; [ "$rc" -eq 0 ] || fail=1

mark 'podman: images --digests' "podman images --digests"
podman images --digests >/tmp/l1_run.out 2>&1; rc=$?
cat /tmp/l1_run.out >>"$LOG"; foot "$rc"

img=$(podman images --noheading --format '{{.Id}}' 2>/dev/null | head -n1)
printf 'image_id_selected=%s\n' "$img" >>"$LOG"

mark 'podman: image inspect (identity)' "podman image inspect --format '{{.Id}}|{{.Digest}}|{{.RepoTags}}' $img"
podman image inspect --format '{{.Id}}|{{.Digest}}|{{.RepoTags}}' "$img" >/tmp/l1_run.out 2>&1; rc=$?
cat /tmp/l1_run.out >>"$LOG"; foot "$rc"

# --- step 3: stored entry point (Level A)
mark 'replay: ./verify.sh in pinned image (stored entry point)' "podman run --rm --platform linux/amd64 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user 0:0 --tmpfs /tmp:rw,exec,nosuid,size=4g -v $TREE:/work:ro -w /work $img ./verify.sh"
podman run --rm --platform linux/amd64 --network none --read-only \
  --cap-drop ALL --security-opt no-new-privileges \
  --user 0:0 --tmpfs /tmp:rw,exec,nosuid,size=4g \
  -v "$TREE:/work:ro" -w /work "$img" ./verify.sh >/tmp/l1_run.out 2>&1; rc=$?
cat /tmp/l1_run.out >>"$LOG"; foot "$rc"; [ "$rc" -eq 0 ] || fail=1

# --- step 4: container review = the image's own default CMD (same command their tag
#     workflow ran); covers the fresh critical lanes (triangle arb, normalizer,
#     tail, tail_arb with sanitizers, direct singletons, barrier replay).
mkdir -p "$OUT"
mark 'replay: container review (image default CMD; same as their tag workflow)' "podman run --rm --platform linux/amd64 --network none --read-only --cap-drop ALL --security-opt no-new-privileges --user 0:0 --tmpfs /tmp:rw,exec,nosuid,size=4g -e REVIEW_OUTPUT=/review-output/evidence -v $TREE:/work:ro -v $OUT:/review-output -w /work $img"
podman run --rm --platform linux/amd64 --network none --read-only \
  --cap-drop ALL --security-opt no-new-privileges \
  --user 0:0 --tmpfs /tmp:rw,exec,nosuid,size=4g \
  -e REVIEW_OUTPUT=/review-output/evidence \
  -v "$TREE:/work:ro" -v "$OUT:/review-output" -w /work "$img" >/tmp/l1_run.out 2>&1; rc=$?
cat /tmp/l1_run.out >>"$LOG"; foot "$rc"; [ "$rc" -eq 0 ] || fail=1

# --- step 5: evidence inventory (files produced by replay_guard under REVIEW_OUTPUT)
mark 'evidence: sha256 inventory of produced files (REVIEW_OUTPUT)' "find $OUT -type f -exec sha256sum {} +"
find "$OUT" -type f -exec sha256sum {} + >/tmp/l1_run.out 2>&1; rc=$?
cat /tmp/l1_run.out >>"$LOG"; foot "$rc"

if [ "$fail" -eq 0 ]; then printf '\nRESULT: L1-RUN COMPLETE (all steps exit 0 as recorded above)\n' >>"$LOG"; else printf '\nRESULT: L1-RUN COMPLETE WITH FAILURES (see EXIT lines)\n' >>"$LOG"; fi
exit "$fail"
