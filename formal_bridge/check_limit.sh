#!/usr/bin/env bash
# Reproduce the Coq geometric-limit checks (formal_bridge/GeometricLimit.v).
#
# Recorded run: Coq 8.20.1, OCaml 4.14.2, 2026-10-19. GeometricBridge.v
# (A-2026-0008, frozen) is compiled first, then GeometricLimit.v imports it;
# coqchk then re-checks the module with the independent kernel checker.
#
# Usage:  ./check_limit.sh
#         COQC=/path/to/coqc COQCHK=/path/to/coqchk ./check_limit.sh
#
# Exit status: 0 only if BOTH files compile, coqchk accepts the limit
# module, and every Lemma/Theorem/Corollary/Remark in GeometricLimit.v
# appears in the kernel output. Any failure is loud and non-zero.

set -u

here="$(cd "$(dirname "$0")" && pwd)"
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
cp "$here/GeometricBridge.v" "$here/GeometricLimit.v" "$work/"
cd "$work" || exit 2

"$coqc" GeometricBridge.v > bridge.log 2>&1
s_bridge=$?
"$coqc" -Q . "" GeometricLimit.v > limit.log 2>&1
s_limit=$?

"$coqchk" -Q . "" GeometricLimit > kernel.log 2>&1
s_kernel=$?

names="$(grep -hoE '^(Lemma|Theorem|Corollary|Remark|Proposition)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' GeometricLimit.v \
  | sed -E 's/^[A-Za-z]+[[:space:]]+//' | sort -u)"
checked="$(grep -oE 'checking cst:GeometricLimit\.[A-Za-z_][A-Za-z0-9_]*' kernel.log \
  | sed 's/.*GeometricLimit\.//' | sort -u)"

echo "coqc:   $(command -v "$coqc")"
echo "coqchk: $(command -v "$coqchk")"
echo "coqc GeometricBridge exit: $s_bridge"
echo "coqc GeometricLimit exit: $s_limit"
echo "coqchk exit: $s_kernel"
echo "coqchk final line: $(tail -1 kernel.log)"
echo "coqchk full log lines: $(wc -l < kernel.log)"
echo "results in GeometricLimit.v: $(echo "$names" | wc -l)"
echo "results checked by coqchk: $(echo "$checked" | wc -l)"

missing="$(comm -23 <(echo "$names") <(echo "$checked"))"
if [ -n "$missing" ]; then
  echo "MISSING FROM KERNEL CHECK:" >&2
  echo "$missing" >&2
  exit 1
fi

if [ "$s_bridge" -ne 0 ] || [ "$s_limit" -ne 0 ] || [ "$s_kernel" -ne 0 ]; then
  echo "--- bridge log ---" >&2; cat bridge.log >&2
  echo "--- limit log ---" >&2; cat limit.log >&2
  exit 1
fi

if ! grep -q 'Modules were successfully checked' kernel.log; then
  echo "KERNEL CHECK DID NOT REPORT SUCCESS" >&2
  exit 1
fi

echo "--- results checked ---"
echo "$checked" | sed 's/^/  /'
echo "--- coqc audit log (Print Assumptions) ---"
cat limit.log
echo "OK: imported bridge unchanged, limit module kernel-checked"
