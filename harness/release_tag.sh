#!/usr/bin/env bash
# T-hat-N v1.1.0 local release gate.
# Runs the full verification pipeline and locks the annotated tag v1.1.0
# in the LOCAL repository topology only. This script never pushes: publication
# remains an explicit, separate human decision.
set -euo pipefail

TAG="v1.1.0"
TAG_MESSAGE="T-hat-N v1.1.0: sealed GRH Dirichlet campaign. 85 green regression tests, dual replayed SHA-256 ledgers V(L)=True, holographic seal SAFE-COMPUTATION, multiresolution chi_4 bracket dossier, landmine register L1-L38."

fail() {
  echo "RELEASE ABORTED: $1" >&2
  exit 1
}

echo "==> Stage 1/5: local unit test suite"
python3 -m pytest msaf -q || fail "pytest suite reported failures"

echo "==> Stage 2/5: rigid ledger audit verification"
python3 -m msaf.audit --prec 256 --newton_max_iter 16 --final-audit \
  || fail "ledger audit verification reported failure"

echo "==> Stage 3/5: working tree cleanliness"
test -z "$(git status --porcelain)" \
  || fail "working tree is not clean; commit or stash all changes first"
echo "working tree is clean"

echo "==> Stage 4/5: git identity signature"
EMAIL="$(git config user.email || true)"
test -n "$EMAIL" || fail "git user.email is empty; configure an identity first"
case "$EMAIL" in
  *example.com*)
    fail "git user.email still contains placeholder domain 'example.com': $EMAIL"
    ;;
esac
echo "git identity accepted: $(git config user.name) <$EMAIL>"

echo "==> Stage 5/5: locking local annotated tag $TAG"
git rev-parse "$TAG" >/dev/null 2>&1 \
  && fail "tag $TAG already exists locally; delete it explicitly to re-release"
git tag -a "$TAG" -m "$TAG_MESSAGE"
echo "locked: $(git rev-parse "$TAG")"

echo "RELEASE GATE COMPLETE: $TAG is sealed locally. No remote was contacted."
