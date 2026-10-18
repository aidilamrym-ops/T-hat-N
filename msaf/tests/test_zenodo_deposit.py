# -*- coding: utf-8 -*-
"""Contract guards for the Zenodo depositor (`msaf/zenodo_deposit.py`).

An edit may re-title a published record and rewrite its opening
paragraphs, but it must never silently retarget what the archive holds
(same commit, same tarball sha256), and the fixed SCOPE paragraph, the
AI-tooling disclosure paragraph and a LICENSE line must survive verbatim.
The same frozen text is composed into every deposit and new version, and
the newversion action's `latest_draft` resolution refuses to guess. These
tests pin all of that with no network access."""

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


def test_compose_description_satisfies_the_frozen_contract() -> None:
    desc = zd.compose_description(TITLE, "OWNER/REPO", COMMIT, SHA,
                                  extra_note="Note.",
                                  license_id="mit-license")
    assert zd.DISCLOSURE_MARKER in desc
    assert zd.SCOPE_NOTE in desc
    assert zd.validate_edit_description(desc, TITLE, COMMIT, SHA) == []


def test_compose_description_without_license_states_none() -> None:
    desc = zd.compose_description(TITLE, "OWNER/REPO", COMMIT, SHA)
    assert "LICENSE: none." in desc


def test_compose_metadata_core_fields() -> None:
    md = zd.compose_metadata(TITLE, "OWNER/REPO", "the description",
                             date="2026-10-18", keywords=["a", "b"])
    assert md["upload_type"] == "software"
    assert md["title"] == TITLE
    assert md["description"] == "the description"
    assert md["publication_date"] == "2026-10-18"
    assert md["access_right"] == "open"
    assert md["related_identifiers"] == [{
        "identifier": "https://github.com/OWNER/REPO",
        "relation": "isSupplementTo",
        "scheme": "url",
    }]
    assert md["keywords"] == ["a", "b"]
    assert md["creators"][0]["orcid"] == "0009-0002-9718-9710"
    assert "version" not in md
    assert "license" not in md


def test_compose_metadata_version_and_license_only_when_passed() -> None:
    md = zd.compose_metadata(TITLE, "OWNER/REPO", "d",
                             version="v1.41.0-alpha",
                             license_id="mit-license")
    assert md["version"] == "v1.41.0-alpha"
    assert md["license"] == "mit-license"


def test_latest_draft_resolution_reads_the_link() -> None:
    payload = {"links": {"latest_draft":
                         "https://zenodo.org/api/deposit/depositions/"
                         "23410999/"}}
    assert zd.resolve_latest_draft_id(payload) == "23410999"


def test_latest_draft_resolution_refuses_without_link() -> None:
    with pytest.raises(SystemExit):
        zd.resolve_latest_draft_id({"links": {}})
