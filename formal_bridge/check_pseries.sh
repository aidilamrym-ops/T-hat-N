#!/usr/bin/env bash
# Reproduce the Coq p-series L2 checks (formal_bridge/PseriesL2.v).
#
# Recorded run: Coq 8.20.1, OCaml 4.14.2, 2026-10-19. PseriesL2.v is
# standalone (stdlib only); coqchk re-checks the module with the
# independent kernel checker.
#
# Usage:  ./check_pseries.sh
#         COQC=/path/to/coqc COQCHK=/path/to/coqchk ./check_pseries.sh
#
# Exit status: 0 only if the file compiles, coqchk accepts the module,
# every Lemma/Theorem/Corollary/Remark/Proposition in PseriesL2.v appears
# in the kernel output, and the Print Assumptions audit has one block per
# result. Any failure is loud and non-zero.

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
cp "$here/PseriesL2.v" "$work/"
cd "$work" || exit 2

"$coqc" -Q . "" PseriesL2.v > pseries.log 2>&1
s_compile=$?
"$coqchk" -Q . "" PseriesL2 > kernel.log 2>&1
s_kernel=$?

names="$(grep -hoE '^(Lemma|Theorem|Corollary|Remark|Proposition)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' PseriesL2.v \
  | sed -E 's/^[A-Za-z]+[[:space:]]+//' | sort -u)"
checked_all="$(grep -oE 'checking cst:PseriesL2\.[A-Za-z_][A-Za-z0-9_]*' kernel.log \
  | sed 's/.*PseriesL2\.//' | sort -u)"
checked="$(comm -12 <(echo "$names") <(echo "$checked_all"))"
audit_blocks="$(grep -c '^Axioms:' pseries.log)"

echo "coqc:   $(command -v "$coqc")"
echo "coqchk: $(command -v "$coqchk")"
echo "coqc PseriesL2 exit: $s_compile"
echo "coqchk exit: $s_kernel"
echo "coqchk final line: $(tail -1 kernel.log)"
echo "coqchk full log lines: $(wc -l < kernel.log)"
echo "results in PseriesL2.v: $(echo "$names" | wc -l)"
echo "results checked by coqchk: $(echo "$checked" | wc -l)"
echo "Print Assumptions blocks: $audit_blocks"

missing="$(comm -23 <(echo "$names") <(echo "$checked"))"
if [ -n "$missing" ]; then
  echo "MISSING FROM KERNEL CHECK:" >&2
  echo "$missing" >&2
  exit 1
fi

if [ "$s_compile" -ne 0 ] || [ "$s_kernel" -ne 0 ]; then
  echo "--- compile log ---" >&2; cat pseries.log >&2
  exit 1
fi

if ! grep -q 'Modules were successfully checked' kernel.log; then
  echo "KERNEL CHECK DID NOT REPORT SUCCESS" >&2
  exit 1
fi

if [ "$audit_blocks" -ne "$(echo "$names" | wc -l)" ]; then
  echo "AUDIT BLOCK COUNT MISMATCH: $audit_blocks blocks for $(echo "$names" | wc -l) results" >&2
  exit 1
fi

echo "--- results checked ---"
echo "$checked" | sed 's/^/  /'
echo "--- coqc audit log (Print Assumptions) ---"
cat pseries.log
echo "OK: pseries L2 module kernel-checked; audit block count matches results"
