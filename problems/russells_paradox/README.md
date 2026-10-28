# Problem
Russell’s Paradox – set of all sets that do not contain themselves.

## Statement
Define \(R = \{x \mid x \notin x\}\). Show that \(R\in R\) leads to contradiction, i.e., \(R\in R \iff R\notin R\).

## Remarks
- Classic paradox in naive set theory.
- Formalizable in Lean using `set` and `¬`. Provide stub Lean file under `problems/russells_paradox/lean/` for later formal proof.
- Useful test of logical framework handling of self‑reference.
