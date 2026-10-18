# -*- coding: utf-8 -*-
"""Contract guards for the in-place metadata edit path of the Zenodo
depositor (`msaf/zenodo_deposit.py --edit-record`).

An edit may re-title a published record and rewrite its opening
paragraphs, but it must never silently retarget what the archive holds
(same commit, same tarball sha256), and the fixed SCOPE paragraph plus a
LICENSE line must survive verbatim. These tests pin that contract with no
network access."""

from __future__ import annotations

import pytest

from msaf import zenodo_deposit as zd

TITLE = "Rigorous Ball Arithmetic for Zeta, L-Function, and Weil Spectra"
COMMIT = "a" * 40
SHA = "b" * 64
LICENSE_LINE = ("LICENSE: mit-license, as stated by the LICENSE file in "
                "the archived repository.")


DISCLOSURE = ("Provenance and AI-tooling disclosure. The OpenCode agentic "
              "coding environment drafts under human direction.")


def _description(title=TITLE, commit=COMMIT, sha=SHA, scope=zd.SCOPE_NOTE,
                 disclosure=DISCLOSURE, license_line=LICENSE_LINE):
    return ("%s\n\nA new opening paragraph.\n\n"
            "Source: https://github.com/OWNER/REPO at commit %s "
            "(archived tarball sha256 %s).\n"
            "Continuous integration for that exact commit: GREEN "
            "(GitHub Actions).\n\n%s\n\n%s\n\n%s"
            % (title, commit, sha, scope, disclosure, license_line))


def test_valid_edit_description_passes() -> None:
    problems = zd.validate_edit_description(_description(), TITLE, COMMIT,
                                            SHA)
    assert problems == []


def test_description_must_start_with_the_new_title() -> None:
    text = _description().replace(TITLE, "An Older Title", 1)
    problems = zd.validate_edit_description(text, TITLE, COMMIT, SHA)
    assert any("start with the new title" in p for p in problems)


def test_archived_commit_cannot_change() -> None:
    problems = zd.validate_edit_description(_description(commit="c" * 40),
                                            TITLE, COMMIT, SHA)
    assert any("archived commit" in p for p in problems)


def test_archived_tarball_sha256_cannot_change() -> None:
    problems = zd.validate_edit_description(_description(sha="d" * 64),
                                            TITLE, COMMIT, SHA)
    assert any("sha256" in p for p in problems)


def test_scope_paragraph_is_fixed() -> None:
    text = _description(scope=zd.SCOPE_NOTE.replace("NOT", "not"))
    problems = zd.validate_edit_description(text, TITLE, COMMIT, SHA)
    assert any("SCOPE" in p for p in problems)


def test_license_line_is_required() -> None:
    problems = zd.validate_edit_description(
        _description(license_line="All rights reserved."), TITLE, COMMIT,
        SHA)
    assert any("LICENSE" in p for p in problems)


def test_ai_tooling_disclosure_is_pinned() -> None:
    problems = zd.validate_edit_description(_description(disclosure=""),
                                            TITLE, COMMIT, SHA)
    assert any("AI-tooling disclosure" in p for p in problems)


def test_claims_extraction_reads_commit_and_sha() -> None:
    commit, sha = zd.extract_archive_claims(_description())
    assert commit == COMMIT
    assert sha == SHA


def test_claims_extraction_refuses_unparsable_text() -> None:
    with pytest.raises(SystemExit):
        zd.extract_archive_claims("no claim pair in this text")
