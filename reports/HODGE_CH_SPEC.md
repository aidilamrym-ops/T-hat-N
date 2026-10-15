# HODGE-CH Specification: the Last Trace via Couveignes–Henocq

Status: SPECIFICATION + combiner sealed; residue engine OPEN.
Target: the single missing trace a_11 of the certified smooth
quartic over F_3 (ten exact traces a_1..a_10 serve as the oracle;
a_10 pending the offline artifact).

## 1. Problem statement (exact)

The degree-22 Newton reconstruction needs power sums p_1..p_11 with
p_k = a_k = #X(F_{3^k}) - 1 - 3^{2k}. We hold p_1..p_10 exactly.
Missing: p_11 = a_11, with the Weil envelope |a_11| <= B,
B = 22 * 3^11 = 3,897,234. Direct counting costs ~19 h (measured);
the residue route below needs only the already-held counts.

## 2. Architecture (three parts, two sealed)

```
                  +------------------+
                  |  residue engine  |  OPEN (section 4)
                  |  r_l = a_11 mod l|
                  +--------+---------+
                           | residues (+ moduli)
                           v
                  +------------------+
                  | crt_combine.py   |  SEALED + tested
                  |  CRT + Weil cert |
                  +--------+---------+
                           | candidate integer or INCONCLUSIVE
                           v
                  +------------------+
                  |   oracle gate    |  SEALED + tested
                  | engine must also |
                  | reproduce a_1..  |
                  | a_10 or refused  |
                  +------------------+
```

**Part A — CRT combiner (sealed).** `crt_combine.recover_integer`
takes residues r_l = a mod l over distinct primes l, forms
x mod M by exact Garner CRT, and returns the symmetric
representative ONLY if M > 2B (uniqueness certificate: any two
candidates differ by a multiple of M). Otherwise INCONCLUSIVE --
never a guess. Input gates: pairwise coprimality asserted (gcd),
residues in range asserted, no floats, no bools.

**Part B — oracle gate (sealed).** The residue engine is untrusted
until it reproduces the KNOWN: it must emit residues for a_1..a_10
(computed by whatever method it uses for a_11); the combiner
recovers each; `oracle_check` compares against the locked exact
integers. Any mismatch -> the engine is refused for a_11, loudly.
A corrupted residue otherwise yields a wrong-but-in-envelope
integer that NOTHING would catch -- this gate exists because of
exactly that failure mode (found by reasoning, locked by test).

**Part C — residue engine (OPEN).** Source of r_l = a_11 mod l.
Options, honestly graded:
  1. *Schoof-Pila on the K3*: needs explicit l-torsion in a
     22-dimensional cohomology -- heavy algebraic geometry, no
     prototype exists here. Most principled, most expensive.
  2. *Weil-constraint search*: enumerate candidate a_11 in
     [-B, B] (7.8M values), keep those whose completed char poly
     (Newton + FE) has all roots on |z| = 3^11 via exact
     Schur-Cohn recursion; uniqueness NOT guaranteed a priori --
     measures first whether it isolates one value. Cheapest to try.
  3. *Kedlaya p-adic cohomology*: the industrial route (Lauder,
     Costa et al.), a full implementation project on its own.

  Decision rule (binding): prototype option 2 first (days, not
  months); adopt it ONLY if it isolates a_11 uniquely on the
  measured data AND reproduces a_1..a_10 in a leave-one-out rehearsal
  (drop each known trace in turn, recover it by the same method).
  Otherwise fall to option 1 or 3 -- explicitly, not silently.

## 3. Acceptance criteria for closing HODGE-CH

1. a_11 integer with |a_11| <= B, recovered via combiner (M > 2B).
2. Oracle gate HOLD on all of a_1..a_10 from the same engine.
3. Leave-one-out rehearsal passes for every k = 1..10.
4. Completed char poly closes FE (leading coeff 3^22, sign recorded)
   and Picard bound reported with the same honesty flags as F_5
   (whatever the number -- including 20).
5. Full suite green, seal per workflow.

## 4. Explicit non-claims

- A recovered a_11 is a point-count-derived integer, not a theorem
  about the surface beyond what the pipeline certifies.
- The Picard bound that follows is an upper bound for one surface
  over F_3 (same scope discipline as F_5).
- If option 2 fails to isolate uniquely, that failure is REPORTED
  (measured non-uniqueness counts), not worked around.
