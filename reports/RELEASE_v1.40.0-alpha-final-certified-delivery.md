# GitHub Release -- v1.40.0-alpha-final-certified-delivery

TEMPLATE for the GitHub Release of the EXISTING annotated tag. Do NOT
create a new tag. Status 2026-10-16: PUBLISHED via `gh` (release page
live). Zenodo: this delivery is archived as a new version of the T-hat-N
record -- version DOI `10.5281/zenodo.23410894`, concept DOI
`10.5281/zenodo.23338271`; archive `T-hat-N-a37b50b7dbdd.tar.gz`,
sha256 `44bdfb87788b1f1da687b2d8e852641385b5c80de99c072768f6b67120198f61`.
Republish or edit with:

    gh release create v1.40.0-alpha-final-certified-delivery --verify-tag \
      --notes-file reports/RELEASE_v1.40.0-alpha-final-certified-delivery.md

Zenodo webhook status: never enabled; the deposit went through the
depositor API (`msaf/zenodo_deposit.py`). Enabling the webhook later (see
`docs/ZENODO_ACTIVATE.md`) only affects FUTURE releases.

## Machine metadata

```yaml
tag: v1.40.0-alpha-final-certified-delivery
tag_object: 9fb68ff15406144bcbe20bf0cd9dff00fadd21a0
target_commit: a37b50b7dbdd7035cbeedc016e0a4070550557d1
previous_tag: v1.40.0-alpha   # d60b8ace916931f467ad59de5928eb8f7dabd6c0, unchanged
ci_push_run: 38854261266      # success
ci_tag_run: 38854493402       # success
suite: 311 passed
artifacts:
  reports/gw_diagnostic_v3.html:
    sha256: 89C7D5F948626BD51DE06F37534BDC4941D3793353DCB80B8557E10E2BED7322
  exports/research_paper.tex:
    sha256: 1840D07AC7445F63EEAFD015C0AF78EF45AE942342269E784640A7460B5315F8
```

## Summary

Consolidation delivery of the sealed Guinand-Weil three-resolution campaign
(dim 201 / 301 / 401):

- `exports/research_paper.tex` -- publication-grade consolidation of the
  sealed Main Spectral Results: the rigid three-point matrix (including the
  "0.0000 ; 0.0180" cell), the 18-cell S2 grid with 17/18 cells at the
  2000-surrogate floor, the double-ensemble extremity narration at
  sigma_u = 0.3, and the process-defect register transcribed from
  `reports/THREE_TASKS_2026-10-15.md` section 4.4. Transcription of sealed
  artifacts only; every number machine cross-checked cell-by-cell against
  the canonical logs (18/18 exact string matches).
- `reports/gw_diagnostic_v3.html` -- standalone offline dashboard; byte
  replay verified: rerunning `msaf/gw_dashboard_v3.py --write` returns the
  identical 23,493-byte file (17x "0.0000" + 1x "0.0180"; deterministic
  18-cell log10 heat scale).
- README section 6 map and HANDOFF seal rows updated for this delivery.

## Artifact hashes (exact)

Both sha256 values below are over the file content AS STORED IN THE TAGGED
COMMIT (git blob bytes). Verified additionally that they equal the
working-tree bytes on the sealing machine (Windows, core.autocrlf=true),
because the dashboard generator writes raw UTF-8 bytes with explicit LF
(`OUT.write_bytes(html.encode("utf-8"))`, `msaf/gw_dashboard_v3.py` line
516) and the manuscript source is LF/ASCII-only. GitHub and Zenodo source
archives distribute exactly the blob bytes, so these hashes describe the
released artifacts, not a local checkout variant.

| Artifact | SHA-256 |
|---|---|
| `reports/gw_diagnostic_v3.html` | `89C7D5F948626BD51DE06F37534BDC4941D3793353DCB80B8557E10E2BED7322` |
| `exports/research_paper.tex` | `1840D07AC7445F63EEAFD015C0AF78EF45AE942342269E784640A7460B5315F8` |

## Provenance chain

- campaign seal: `da93d19` (measurement close + dashboard lock)
- series close + CI record: `6a69de4`; README section 6: `28de2b8`;
  HANDOFF consolidation: `86b161f`
- this delivery: `a37b50b` (annotated tag object `9fb68ff1...`)
- CI: `38854261266` (commit push), `38854493402` (tag ref)
- baseline note: commits `6a69de4` / `14a1588` are ANCESTORS of the delivery
  commit (intermediate milestones on 2026-10-16), not the sealed head.

## Scope (read before citing)

Statistics of one finite deterministic constructed matrix per resolution.
NOT Montgomery's theorem, NOT evidence for the Riemann Hypothesis, NOT
Weil positivity, NOT prime counting, NOT factorisation. Open question kept
open: structural signature of the lattice versus a finite-size effect.

## Verify locally

    python msaf/gw_resolution_delta.py --write   # section-5 generator consistency
    python msaf/gw_dashboard_v3.py --write       # byte-replay of the dashboard
    python -m pytest msaf -q                     # 311 passed
