#!/usr/bin/env bash
# Reproduce the Coq L5 infinite (unconditional) checks
# (formal_bridge/IntegralComparisonInfinite.v).
#
# Recorded run: Coq 8.20.1, OCaml 4.14.2, 2026-10-20.  The module imports
# the sealed Paket 7 finite-core module (IntegralComparison.v, A-2026-0012),
# the sealed Paket 8 conditional limit module (IntegralComparisonLimit.v,
# A-2026-0013) and the sealed p-series module (PseriesL2.v, A-2026-0010);
# all four sources are copied to a temporary directory, compiled with coqc,
# and the new module is re-checked with the independent coqchk checker.
#
# Usage:  ./check_integral_infinite.sh
#         COQC=/path/to/coqc COQCHK=/path/to/coqchk ./check_integral_infinite.sh
#
# Exit status: 0 only if all modules compile, coqchk accepts the new
# module, every Lemma/Theorem in IntegralComparisonInfinite.v appears in
# the kernel output, the Print Assumptions sections match the result count,
# every axiom name belongs to the four allowed stdlib axioms, and the final
# block (the main theorem) carries exactly that four-axiom set.  Any
# failure is loud and non-zero.
#
# Trusted base: the same four stdlib axioms as Paket 7/8.  This package
# proves existence of the three limits for f_k; the only f_k instance is
# covered (no general f, no real exponent).

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
cp "$here/IntegralComparison.v" "$work/"
cp "$here/IntegralComparisonLimit.v" "$work/"
cp "$here/IntegralComparisonInfinite.v" "$work/"
cd "$work" || exit 2

"$coqc" -Q . "" PseriesL2.v > pseries.log 2>&1
s_pseries=$?
"$coqc" -Q . "" IntegralComparison.v > dep.log 2>&1
s_dep=$?
"$coqc" -Q . "" IntegralComparisonLimit.v > limit.log 2>&1
s_limit=$?
"$coqc" -Q . "" IntegralComparisonInfinite.v > inf.log 2>&1
s_compile=$?
"$coqchk" -Q . "" IntegralComparisonInfinite > kernel.log 2>&1
s_kernel=$?

names="$(grep -hoE '^(Lemma|Theorem|Corollary|Remark|Proposition)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' IntegralComparisonInfinite.v \
  | sed -E 's/^[A-Za-z]+[[:space:]]+//' | sort -u)"
checked_all="$(grep -oE 'checking cst:IntegralComparisonInfinite\.[A-Za-z_][A-Za-z0-9_]*' kernel.log \
  | sed 's/.*IntegralComparisonInfinite\.//' | sort -u)"
checked="$(comm -12 <(echo "$names") <(echo "$checked_all"))"
n_names="$(echo "$names" | wc -l)"
n_checked="$(echo "$checked" | wc -l)"

audit_axioms="$(grep -c '^Axioms:' inf.log)"
audit_closed="$(grep -c '^Closed under the global context$' inf.log)"
audit_sections=$((audit_axioms + audit_closed))

audit_names="$(grep -v '^Axioms:' inf.log \
  | grep -v '^Closed under the global context$' \
  | grep -oE '^[A-Za-z_][A-Za-z0-9_.]*[[:space:]]*:' \
  | sed -E 's/[[:space:]]*:$//' | sort -u)"

final_names="$(awk '
  /^Axioms:/ { block = ""; inblock = 1; next }
  /^Closed under the global context$/ { inblock = 0; next }
  inblock && /^[A-Za-z_][A-Za-z0-9_.]*[[:space:]]*:/ {
    line = $0
    sub(/[[:space:]]*:.*/, "", line)
    block = block line "\n"
  }
  END { printf "%s", block }
' inf.log | sort -u)"

expected_four="ClassicalDedekindReals.sig_forall_dec
ClassicalDedekindReals.sig_not_dec
Classical_Prop.classic
FunctionalExtensionality.functional_extensionality_dep"

echo "coqc:   $(command -v "$coqc")"
echo "coqchk: $(command -v "$coqchk")"
echo "coqc PseriesL2 (dependency) exit: $s_pseries"
echo "coqc IntegralComparison (dependency) exit: $s_dep"
echo "coqc IntegralComparisonLimit (dependency) exit: $s_limit"
echo "coqc IntegralComparisonInfinite exit: $s_compile"
echo "coqchk exit: $s_kernel"
echo "coqchk final line: $(tail -1 kernel.log)"
echo "coqchk full log lines: $(wc -l < kernel.log)"
echo "results in IntegralComparisonInfinite.v: $n_names"
echo "results checked by coqchk: $n_checked"
echo "Print Assumptions sections: $audit_sections ($audit_axioms Axioms, $audit_closed Closed)"
echo "audit axiom names: $(echo "$audit_names" | tr '\n' ' ')"
echo "final audit block (main theorem): $(echo "$final_names" | tr '\n' ' ')"

missing="$(comm -23 <(echo "$names") <(echo "$checked"))"
if [ -n "$missing" ]; then
  echo "MISSING FROM KERNEL CHECK:" >&2
  echo "$missing" >&2
  exit 1
fi

if [ "$s_pseries" -ne 0 ] || [ "$s_dep" -ne 0 ] || [ "$s_limit" -ne 0 ] || [ "$s_compile" -ne 0 ] || [ "$s_kernel" -ne 0 ]; then
  echo "--- pseries.log ---" >&2; cat pseries.log >&2
  echo "--- dep.log ---" >&2; cat dep.log >&2
  echo "--- limit.log ---" >&2; cat limit.log >&2
  echo "--- inf.log ---" >&2; cat inf.log >&2
  echo "--- kernel.log (tail) ---" >&2; tail -50 kernel.log >&2
  exit 1
fi

if ! grep -q 'Modules were successfully checked' kernel.log; then
  echo "KERNEL CHECK DID NOT REPORT SUCCESS" >&2
  exit 1
fi

if [ "$n_names" -ne 17 ] || [ "$n_checked" -ne 17 ]; then
  echo "RESULT COUNT MISMATCH: source=$n_names checked=$n_checked (expected 17/17)" >&2
  exit 1
fi

if [ "$audit_sections" -ne "$n_names" ]; then
  echo "AUDIT SECTION MISMATCH: $audit_sections sections for $n_names results" >&2
  exit 1
fi

if [ "$audit_names" != "$expected_four" ]; then
  echo "AUDIT AXIOM SET MISMATCH: got [$audit_names]" >&2
  echo "expected [$expected_four]" >&2
  exit 1
fi

if [ "$final_names" != "$expected_four" ]; then
  echo "FINAL AUDIT BLOCK MISMATCH: got [$final_names]" >&2
  echo "expected [$expected_four]" >&2
  exit 1
fi

echo "--- results checked ---"
echo "$checked" | sed 's/^/  /'
echo "--- coqc audit log (Print Assumptions) ---"
cat inf.log
echo "OK: L5 infinite module kernel-checked; 17/17 results; final audit = 4 stdlib axioms; no project axioms"
