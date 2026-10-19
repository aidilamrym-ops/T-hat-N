#!/usr/bin/env bash
# Reproduce the Coq L5 limit-step checks
# (formal_bridge/IntegralComparisonLimit.v).
#
# Recorded run: Coq 8.20.1, OCaml 4.14.2, 2026-10-20.  The module imports
# the sealed Paket 7 finite-core module (IntegralComparison.v, registry
# A-2026-0012); both sources are copied to a temporary directory, compiled
# with coqc, and re-checked with the independent coqchk kernel checker.
#
# Usage:  ./check_integral_limit.sh
#         COQC=/path/to/coqc COQCHK=/path/to/coqchk ./check_integral_limit.sh
#
# Exit status: 0 only if both modules compile, coqchk accepts the new
# module, every Lemma/Theorem in IntegralComparisonLimit.v appears in the
# kernel output, the Print Assumptions sections match the result count,
# every axiom name belongs to the four allowed stdlib axioms, and the final
# block (the main theorem) carries exactly that four-axiom set.  Any
# failure is loud and non-zero.
#
# Trusted base: the same four stdlib axioms as Paket 7.  The limit step is
# conditional: existence of the limits is not proved here (that is Paket 9).

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
cp "$here/IntegralComparison.v" "$work/"
cp "$here/IntegralComparisonLimit.v" "$work/"
cd "$work" || exit 2

"$coqc" -Q . "" IntegralComparison.v > dep.log 2>&1
s_dep=$?
"$coqc" -Q . "" IntegralComparisonLimit.v > limit.log 2>&1
s_compile=$?
"$coqchk" -Q . "" IntegralComparisonLimit > kernel.log 2>&1
s_kernel=$?

names="$(grep -hoE '^(Lemma|Theorem|Corollary|Remark|Proposition)[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' IntegralComparisonLimit.v \
  | sed -E 's/^[A-Za-z]+[[:space:]]+//' | sort -u)"
checked_all="$(grep -oE 'checking cst:IntegralComparisonLimit\.[A-Za-z_][A-Za-z0-9_]*' kernel.log \
  | sed 's/.*IntegralComparisonLimit\.//' | sort -u)"
checked="$(comm -12 <(echo "$names") <(echo "$checked_all"))"
n_names="$(echo "$names" | wc -l)"
n_checked="$(echo "$checked" | wc -l)"

audit_axioms="$(grep -c '^Axioms:' limit.log)"
audit_closed="$(grep -c '^Closed under the global context$' limit.log)"
audit_sections=$((audit_axioms + audit_closed))

audit_names="$(grep -v '^Axioms:' limit.log \
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
' limit.log | sort -u)"

expected_four="ClassicalDedekindReals.sig_forall_dec
ClassicalDedekindReals.sig_not_dec
Classical_Prop.classic
FunctionalExtensionality.functional_extensionality_dep"

echo "coqc:   $(command -v "$coqc")"
echo "coqchk: $(command -v "$coqchk")"
echo "coqc IntegralComparison (dependency) exit: $s_dep"
echo "coqc IntegralComparisonLimit exit: $s_compile"
echo "coqchk exit: $s_kernel"
echo "coqchk final line: $(tail -1 kernel.log)"
echo "coqchk full log lines: $(wc -l < kernel.log)"
echo "results in IntegralComparisonLimit.v: $n_names"
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

if [ "$s_dep" -ne 0 ] || [ "$s_compile" -ne 0 ] || [ "$s_kernel" -ne 0 ]; then
  echo "--- dep.log ---" >&2; cat dep.log >&2
  echo "--- limit.log ---" >&2; cat limit.log >&2
  echo "--- kernel.log (tail) ---" >&2; tail -50 kernel.log >&2
  exit 1
fi

if ! grep -q 'Modules were successfully checked' kernel.log; then
  echo "KERNEL CHECK DID NOT REPORT SUCCESS" >&2
  exit 1
fi

if [ "$n_names" -ne 4 ] || [ "$n_checked" -ne 4 ]; then
  echo "RESULT COUNT MISMATCH: source=$n_names checked=$n_checked (expected 4/4)" >&2
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
cat limit.log
echo "OK: L5 limit-step module kernel-checked; 4/4 results; final audit = 4 stdlib axioms; no project axioms"
