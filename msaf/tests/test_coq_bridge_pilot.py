# -*- coding: utf-8 -*-
"""Static CI guard for the Coq bridge pilot (``formal_bridge/``).

CI has no Coq toolchain, so this test cannot re-run the kernel. It refuses
instead to let the sealed artifact rot, and it fails loudly on the two
failure modes this repository has already been bitten by:

  * a placeholder hiding in the source -- comments are stripped with a
    nesting counter, because Coq comments nest and a naive regex leaves
    the tail of a nested comment looking like code;
  * an audit that covers fewer results than were proved -- every ``Lemma``
    in the source must have a matching ``Print Assumptions`` line, and the
    frozen log must carry exactly one assumption block per lemma.

The kernel run itself is recorded, not re-executed here: the report names
the exact command, and the registry pins the bytes of both logs. ``coqc``
and ``coqchk`` both exited 0 when the logs were captured (2026-10-19,
Coq 8.20.1).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRIDGE_DIR = ROOT / "formal_bridge"
SOURCE = BRIDGE_DIR / "GeometricBridge.v"
COMPILE_LOG = BRIDGE_DIR / "GeometricBridge.compile.log"
RECEIPT = BRIDGE_DIR / "GeometricBridge.receipt.txt"

# The only assumptions Coq.Reals introduces. Nothing project-specific is
# allowed: an extra name here means the proof rests on something the
# standard library did not supply.
ALLOWED_ASSUMPTIONS = {
    "ClassicalDedekindReals.sig_forall_dec",
    "FunctionalExtensionality.functional_extensionality_dep",
}

PLACEHOLDERS = re.compile(r"\b(admit|Admitted|Axiom|Parameter|Hypothesis|Abort)\b")
LEMMA_RE = re.compile(r"^\s*Lemma\s+([A-Za-z_][A-Za-z0-9_']*)", re.M)
PRINT_RE = re.compile(r"^\s*Print\s+Assumptions\s+([A-Za-z_][A-Za-z0-9_']*)\s*\.",
                      re.M)
ASSUMPTION_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.']*)\s*:$", re.M)


def _strip_comments(text: str) -> str:
    """Remove Coq ``(* ... *)`` comments, counting nesting.

    Coq comments nest, so a non-greedy regex would stop at the first inner
    closer and expose prose as if it were code. Newlines are preserved so
    line numbers in failures stay meaningful.
    """
    out: list[str] = []
    i, n = 0, len(text)
    depth = 0
    while i < n:
        if text.startswith("(*", i):
            depth += 1
            i += 2
            continue
        if depth > 0 and text.startswith("*)", i):
            depth -= 1
            i += 2
            continue
        if depth == 0:
            out.append(text[i])
        else:
            out.append("\n" if text[i] == "\n" else " ")
        i += 1
    assert depth == 0, "unterminated Coq comment"
    return "".join(out)


def _lemmas(text: str) -> list[str]:
    return LEMMA_RE.findall(_strip_comments(text))


def _assumption_blocks(log: str) -> list[list[str]]:
    """Split the frozen log into one block of assumption names per lemma."""
    blocks: list[list[str]] = []
    for chunk in log.split("Axioms:")[1:]:
        blocks.append(ASSUMPTION_RE.findall(chunk))
    return blocks


def test_coq_source_has_no_placeholders():
    assert SOURCE.is_file(), "missing formal_bridge/GeometricBridge.v"
    stripped = _strip_comments(SOURCE.read_text(encoding="utf-8"))
    hit = PLACEHOLDERS.search(stripped)
    assert hit is None, f"{SOURCE.name}: placeholder {hit.group(0)!r}"


def test_every_lemma_is_audited():
    lemmas = _lemmas(SOURCE.read_text(encoding="utf-8"))
    printed = PRINT_RE.findall(SOURCE.read_text(encoding="utf-8"))
    assert lemmas, "no Lemma found: the audit would be vacuous"
    assert sorted(lemmas) == sorted(printed), (
        "Print Assumptions coverage mismatch; lemmas=%r printed=%r"
        % (sorted(lemmas), sorted(printed))
    )


def test_frozen_log_has_one_clean_block_per_lemma():
    lemmas = _lemmas(SOURCE.read_text(encoding="utf-8"))
    blocks = _assumption_blocks(COMPILE_LOG.read_text(encoding="utf-8"))
    assert len(blocks) == len(lemmas), (
        "frozen log covers %d of %d lemmas -- an incomplete audit is a "
        "failure, not a pass" % (len(blocks), len(lemmas))
    )
    for index, names in enumerate(blocks, start=1):
        extra = set(names) - ALLOWED_ASSUMPTIONS
        assert not extra, f"block {index}: non-standard assumptions {sorted(extra)}"
        assert names, f"block {index}: empty assumption list (audit not real)"


def test_frozen_kernel_check_reports_success():
    log = RECEIPT.read_text(encoding="utf-8")
    assert "coqc exit: 0" in log, "coqc did not report exit 0"
    assert "coqchk exit: 0" in log, "coqchk did not report exit 0"
    assert "Modules were successfully checked" in log
    lemmas = _lemmas(SOURCE.read_text(encoding="utf-8"))
    checked_line = re.search(r"^lemmas checked by coqchk: (\d+)$", log, re.M)
    assert checked_line, "receipt does not report the number of checked constants"
    assert int(checked_line.group(1)) >= len(lemmas), (
        "coqchk checked %s constants, source declares %d lemmas"
        % (checked_line.group(1), len(lemmas))
    )
    for name in lemmas:
        assert re.search(r"^\s+%s$" % re.escape(name), log, re.M), (
            "receipt does not list %s as kernel-checked" % name
        )


