#!/usr/bin/env bash
# Reproduce the Coq bridge pilot checks (formal_bridge/GeometricBridge.v).
#
# Recorded run: Coq 8.20.1, OCaml 4.14.2, 2026-10-19. Other versions are
# untested; the frozen receipt in this directory is the record, not this
# script's future output.
#
# Usage:  ./check.sh            # compile + kernel check, print a receipt
#         COQC=/path/to/coqc COQCHK=/path/to/coqchk ./check.sh
#
# Exit status: 0 only if the source compiles, the independent kernel
# checker accepts it, and every Lemma in the source appears in the
# kernel-check output. Any failure is loud and non-zero.

set -u

here="$(cd "$(dirname "$0")" && pwd)"
src="$here/GeometricBridge.v"
coqc="${COQC:-coqc}"
coqchk="${COQCHK:-coqchk}"

for tool in "$coqc" "$coqchk"; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "MISSING TOOL: $tool" >&2
    exit 2
  }
done

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cp "$src" "$work/GeometricBridge.v"
cd "$work" || exit 2

"$coqc" GeometricBridge.v > compile.log 2>&1
coqc_status=$?

"$coqchk" -Q . '' GeometricBridge > coqchk.full.log 2>&1
coqchk_status=$?

lemmas="$(grep -oE '^Lemma[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' GeometricBridge.v \
  | sed -E 's/^Lemma[[:space:]]+//' | sort -u)"
checked="$(grep -oE 'checking cst:GeometricBridge\.[A-Za-z_][A-Za-z0-9_]*' \
  coqchk.full.log | sed 's/.*GeometricBridge\.//' | sort -u)"

echo "coqc:   $(command -v "$coqc")"
echo "coqchk: $(command -v "$coqchk")"
echo "coqc exit: $coqc_status"
echo "coqchk exit: $coqchk_status"
echo "coqchk final line: $(tail -1 coqchk.full.log)"
echo "coqchk full log lines: $(wc -l < coqchk.full.log)"
echo "lemmas in source: $(echo "$lemmas" | wc -l)"
echo "lemmas checked by coqchk: $(echo "$checked" | wc -l)"

missing="$(comm -23 <(echo "$lemmas") <(echo "$checked"))"
if [ -n "$missing" ]; then
  echo "MISSING FROM KERNEL CHECK:" >&2
  echo "$missing" >&2
  exit 1
fi

if [ "$coqc_status" -ne 0 ] || [ "$coqchk_status" -ne 0 ]; then
  echo "--- coqc log ---" >&2
  cat compile.log >&2
  exit 1
fi

if ! grep -q 'Modules were successfully checked' coqchk.full.log; then
  echo "KERNEL CHECK DID NOT REPORT SUCCESS" >&2
  exit 1
fi

echo "--- lemmas checked ---"
echo "$checked" | sed 's/^/  /'
echo "--- coqc audit log (Print Assumptions) ---"
cat compile.log
echo "OK: compiled and kernel-checked"
