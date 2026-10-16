# ZENODO_ACTIVATE -- enabling the GitHub -> Zenodo webhook (T-hat-N)

Operational guideline. Owner action required: the switch can only be flipped
from a logged-in browser session at zenodo.org -- no API token bypasses it.
Context: `reports/HANDOFF.md` section 3. **Update 2026-10-16:** the
delivery was secured via the depositor API (`msaf/zenodo_deposit.py`) as
a NEW VERSION of the T-hat-N record -- version DOI
`10.5281/zenodo.23410894`, concept DOI `10.5281/zenodo.23338271`. The
webhook remains OFF; this guide now matters only for enabling AUTOMATIC
archiving of FUTURE releases (the API path stays valid regardless).

## 1. Preconditions (verify first, in this order)

1. Gate green: `python -m pytest msaf -q` -> `311 passed`.
2. CI green on the commit to be archived: delivery commit `a37b50b`
   (runs `38854261266` for the push, `38854493402` for the tag ref).
3. The delivery tag resolves:
   `git ls-remote --tags origin v1.40.0-alpha-final-certified-delivery`
4. Release notes template ready:
   `reports/RELEASE_v1.40.0-alpha-final-certified-delivery.md`.

## 2. Steps (browser, owner only)

1. Log in at https://zenodo.org with the owner account (the one linked to
   ORCID 0009-0002-9718-9710).
2. Open Settings -> GitHub -> "Connect" / "Enable" and authorize the Zenodo
   GitHub application for the account `aidilamrym-ops`.
3. In the repository list, flip the switch ON for `T-hat-N` ONLY. Sealed
   policy (HANDOFF section 3): deposit only repositories whose gate is green
   AND CI is green.
4. Publish the GitHub Release for the EXISTING tag. Status 2026-10-16: the
   delivery release was ALREADY published via `gh` (no browser needed; it
   is the current Latest release). For any FUTURE tag, publish with the
   prepared notes; do NOT create a new tag:
   `gh release create v1.40.0-alpha-final-certified-delivery --verify-tag --notes-file reports/RELEASE_v1.40.0-alpha-final-certified-delivery.md`
5. Zenodo archives the release automatically and mints two DOIs: a concept
   DOI (all versions) and a version DOI (this release).
6. Record the DOI: (a) README "Permanent archive" bullet, (b) HANDOFF
   section 1 new row, (c) the citation block. Follow the format of the four
   verified Zenodo records: the record description carries the commit sha
   and the sha256 of the deposited source archive; related_identifiers
   point back to the GitHub repository.

## 3. Verification checklist (after publishing)

- `https://doi.org/<DOI>` returns HTTP 200.
- The Zenodo record description contains commit `a37b50b...` and a sha256
  of the deposited archive.
- related_identifiers present and pointing at
  `https://github.com/aidilamrym-ops/T-hat-N`.

## 4. Fallback path (no browser, or webhook left disabled)

`python msaf/zenodo_deposit.py` (depositor API). Built-in policy: refuses
to invent licenses or claims, records the sha256 of every deposited file,
and retries interrupted uploads. This mints the DOI without the GitHub
integration, but it does NOT auto-archive future releases; every deposit
must be launched manually.

## 5. Important behaviors

- Drafts do NOT trigger the webhook; the switch must be ON before the
  release is PUBLISHED.
- Switching the repository ON does not retro-archive releases published
  earlier (the 2026-10-13 `v1.1.0` release predates any enablement and will
  not be picked up); the webhook catches NEW release events only.
- Avoid deleting and re-publishing the same release: every publication
  creates a new version DOI.
- The webhook does not run CI; it snapshots the tag content exactly as it
  stands at publication time.

## 6. Record when done

Update `reports/HANDOFF.md`: section 3 (canonical path status for T-hat-N)
and section 1 (new seal row: DOI + verification evidence).
