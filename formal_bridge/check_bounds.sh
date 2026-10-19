#!/usr/bin/env bash
# Reproduce the Coq conditional L2-bounds checks (formal_bridge/PseriesL2Bounds.v).
#
# Recorded run: Coq 8.20.1, OCaml 4.14.2, 2026-10-20. PseriesL2.v
# (A-2026-0010, frozen) is compiled first; PseriesL2Bounds.v imports it.
# coqchk then re-checks the bounds module with the independent kernel.
#
# Usage:  ./check_bounds.sh
#         COQC=/path/to/coqc COQCHK=/path/to/coqchk ./check_bounds.sh
#
# Exit status: 0 only if BOTH files compile, coqchk accepts the bounds
# module, the single exported result appears in the kernel output, the
# Print Assumptions audit has exactly one block with exactly the two
# allowed stdlib axioms, and sig_not_dec is absent. Any failure is loud
# and non-zero.

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
cp "$here/PseriesL2.v" "$here/PseriesL2Bounds.v" "$work/"
cd "$work" || exit 2

"$coqc" -Q . "" PseriesL2.v > pseries.log 2>&1
s_pseries=$?
"$coqc" -Q . "" PseriesL2Bounds.v > bounds.log 2>&1
s_bounds=$?
"$coqchk" -Q . "" PseriesL2Bounds > kernel.log 2>&1
s_kernel=$?

names="$(grep -hoE '^(Lemma|Theorem|Corollary|Remark|Proposition)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' PseriesL2Bounds.v \
  | sed -E 's/^[A-Za-z]+[[:space:]]+//' | sort -u)"
checked="$(grep -oE 'checking cst:PseriesL2Bounds\.[A-Za-z_][A-Za-z0-9_]*' kernel.log \
  | sed 's/.*PseriesL2Bounds\.//' | sort -u)"
audit_blocks="$(grep -c '^Axioms:' bounds.log)"
audit_names="$(grep -v '^Axioms:' bounds.log \
  | grep -oE '^[A-Za-z_][A-Za-z0-9_.]*[[:space:]]*:' \
  | sed -E 's/[[:space:]]*:$//' | sort -u)"
expected_two="ClassicalDedekindReals.sig_forall_dec
FunctionalExtensionality.functional_extensionality_dep"

echo "coqc:   $(command -v "$coqc")"
echo "coqchk: $(command -v "$coqchk")"
echo "coqc PseriesL2 exit: $s_pseries"
echo "coqc PseriesL2Bounds exit: $s_bounds"
echo "coqchk exit: $s_kernel"
echo "coqchk final line: $(tail -1 kernel.log)"
echo "coqchk full log lines: $(wc -l < kernel.log)"
echo "results in PseriesL2Bounds.v: $(echo "$names" | wc -l)"
echo "results checked by coqchk: $(echo "$checked" | wc -l)"
echo "Print Assumptions blocks: $audit_blocks"
echo "audit axiom names: $(echo "$audit_names" | tr '\n' ' ')"

missing="$(comm -23 <(echo "$names") <(echo "$checked"))"
if [ -n "$missing" ]; then
  echo "MISSING FROM KERNEL CHECK:" >&2
  echo "$missing" >&2
  exit 1
fi

if [ "$s_pseries" -ne 0 ] || [ "$s_bounds" -ne 0 ] || [ "$s_kernel" -ne 0 ]; then
  echo "--- pseries.log ---" >&2; cat pseries.log >&2
  echo "--- bounds.log ---" >&2; cat bounds.log >&2
  exit 1
fi

if ! grep -q 'Modules were successfully checked' kernel.log; then
  echo "KERNEL CHECK DID NOT REPORT SUCCESS" >&2
  exit 1
fi

if [ "$audit_blocks" -ne 1 ]; then
  echo "AUDIT BLOCK COUNT MISMATCH: $audit_blocks blocks (expected 1)" >&2
  exit 1
fi

if [ "$audit_names" != "$expected_two" ]; then
  echo "AUDIT AXIOM SET MISMATCH: got [$audit_names]" >&2
  echo "expected [$expected_two]" >&2
  exit 1
fi

if grep -q 'sig_not_dec' bounds.log; then
  echo "FORBIDDEN AXIOM PRESENT: sig_not_dec" >&2
  exit 1
fi

echo "--- results checked ---"
echo "$checked" | sed 's/^/  /'
echo "--- coqc audit log (Print Assumptions) ---"
cat bounds.log
echo "OK: conditional bounds module kernel-checked; exactly two stdlib axioms; no sig_not_dec"
