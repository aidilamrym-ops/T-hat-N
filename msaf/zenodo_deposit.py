# Zenodo deposit helper for the audited public repositories.
"""
Not a general-purpose tool: it is the exact procedure used for the
route-C deposits (only repositories whose gates are machine-verified and
whose CI is green at the archived commit), written down so the action is
reproducible and auditable instead of a sequence of ad-hoc curls.

What it refuses to do, on purpose
---------------------------------
* It never invents a license. `--license` must be passed explicitly; if
  the repository has no LICENSE file the caller passes nothing and the
  description states that no license is granted.
* It never claims a resolution of an open problem. The scope paragraph
  below is fixed text, not a parameter, because the failure mode being
  guarded against is a metadata field quietly implying more than the
  code proves.
* It prints the exact sha256 of the uploaded archive and the commit it
  came from, so the DOI resolves to a byte-verifiable object.
* In edit mode (`--edit-record`) it refuses to retarget what the archive
  holds: the new description must keep the same commit, the same tarball
  sha256, the fixed SCOPE paragraph, the AI-tooling disclosure paragraph
  and a LICENSE line, or nothing is written. Re-titling and rewriting the
  opening paragraph are allowed; changing the archived object is not.
* In new-version mode (`--new-version-of`) it mints a new version of a
  published record: the snapshot is replaced BY DESIGN and the new
  version gets its own DOI, but the description written there must
  satisfy the same contract -- SCOPE, disclosure and the claim pair are
  composed in, never parameters, and are checked before any write.
  Passing --deposition-id together with --new-version-of RESUMES the
  named new-version draft instead of calling actions/newversion again:
  Zenodo answers that call with HTTP 400 ("files.enabled: Please remove
  all files first") once the open draft holds files, so a fill-then-
  publish flow must resume by draft id.

Usage:
    C:\\Python314\\python.exe zenodo_deposit.py --repo OWNER/NAME --sha <full sha>
        [--license mit-license] [--draft-only] [--title "..."]
        [--date YYYY-MM-DD] [--version "..."] [--deposition-id ID]
        [--publish]

    python zenodo_deposit.py --new-version-of ID --repo OWNER/NAME
        --sha <full sha> [--license mit-license] [--title "..."]
        [--date YYYY-MM-DD] [--version "..."] [--keywords "a, b"]
        [--extra-note-file PATH] [--publish]

    python zenodo_deposit.py --new-version-of ID --deposition-id DRAFT
        --repo OWNER/NAME --sha <full sha> [...] [--publish]
        # resume a filled new-version draft (skip actions/newversion)

    python zenodo_deposit.py --edit-record ID --title "..."
        --description-file PATH [--keywords "a, b"] [--dry-run] [--publish]

The token is read from the ZENODO_TOKEN environment variable and is never
written to disk by this script.
"""

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://zenodo.org/api/deposit"

CREATORS = [{
    "name": "Amry, Muhammad Aidil",
    "affiliation": "Independent Researcher",
    "orcid": "0009-0002-9718-9710",
}]

SCOPE_NOTE = (
    "SCOPE -- WHAT THIS ARCHIVE IS NOT. This deposit archives the "
    "executable state of a software repository at one commit, with its "
    "verification harness and its test suite. It is NOT a claim that any "
    "open problem in mathematics or physics has been solved. No Riemann "
    "Hypothesis proof, no P versus NP resolution, no Hodge/Picard "
    "resolution, no Navier-Stokes regularity proof and no BSD/Elliott-"
    "Halberstam resolution is asserted here or anywhere in the archived "
    "tree; where the repository discusses such questions it does so as "
    "formalisation, skeleton, reformulation or bounded numerical "
    "evidence, and its own documents are the authority on which is which. "
    "The verifiable content of this deposit is the code, the manifests, "
    "the machine-checked conditions and the CI run at the commit named "
    "above -- nothing beyond that."
)

DISCLOSURE_MARKER = "AI-tooling disclosure"

DISCLOSURE_NOTE = (
    "Provenance and AI-tooling disclosure. This repository is developed "
    "with substantive AI assistance: the OpenCode agentic coding "
    "environment drafts and edits code, tests and documentation under the "
    "author's direct instruction, review and sign-off. The research "
    "programme, the mathematical content, the sealed artefacts and every "
    "claim are the author's; the AI is a tool, not a source, and never an "
    "author. Nothing in the verification chain depends on who or what "
    "typed a line: every claim is bound to deterministic code, "
    "machine-checked gates and replayable runs; the author takes "
    "responsibility for all content."
)


def post(url, token, payload=None, raw=None, content_type=None):
    data = None
    headers = {"Content-Type": content_type} if content_type else {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif raw is not None:
        data = raw
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise SystemExit("HTTP %s on %s\n%s" % (exc.code, url, body[:2000]))


def get(url, token):
    req = urllib.request.Request(url)
    req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def put(url, token, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="PUT",
        headers={"Content-Type": "application/json"})
    req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise SystemExit("HTTP %s on %s\n%s"
                         % (exc.code, url,
                            exc.read().decode("utf-8", "replace")[:2000]))


def delete(url, token):
    req = urllib.request.Request(url, method="DELETE")
    req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        raise SystemExit("HTTP %s on %s\n%s"
                         % (exc.code, url,
                            exc.read().decode("utf-8", "replace")[:2000]))


def post_multipart(url, token, field, filename, blob):
    """Zenodo's file endpoint takes multipart/form-data, field name `file`.

    Sending the bytes as a raw octet-stream body (the obvious first
    attempt) is accepted by neither side: Zenodo closes the connection
    mid-upload and Python reports WinError 10054, which looks like a
    network fault rather than a malformed request. 31 MB was enough to
    trigger it on the first repository deposited."""
    boundary = "----zenodo-deposit-boundary-8f3c1a"
    head = (
        "--%s\r\n"
        'Content-Disposition: form-data; name="%s"; filename="%s"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n" % (boundary, field,
                                                             filename)
    ).encode("utf-8")
    tail = ("\r\n--%s--\r\n" % boundary).encode("utf-8")
    body = head + blob + tail
    # A single-shot POST of a ~32 MB body is refused at random: Zenodo
    # closed the connection mid-upload twice out of three attempts on
    # different repositories, with no error body to explain it. The
    # refusal is not correlated with size (31 MB succeeded) nor with the
    # draft. Retrying with backoff is the honest response to a flaky
    # endpoint; each attempt re-reads nothing because the body is already
    # in memory, and a deposit that already holds the file is detected by
    # the caller before this is reached.
    last = None
    for attempt in range(1, 5):
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Content-Type":
                     "multipart/form-data; boundary=%s" % boundary})
        req.add_header("Authorization", "Bearer " + token)
        try:
            with urllib.request.urlopen(req, timeout=1800) as resp:
                out = json.loads(resp.read().decode("utf-8"))
            if attempt > 1:
                print("upload succeeded on attempt %d" % attempt)
            return out
        except urllib.error.HTTPError as exc:
            raise SystemExit("HTTP %s on %s\n%s"
                             % (exc.code, url,
                                exc.read().decode("utf-8", "replace")[:2000]))
        except Exception as exc:  # URLError, reset, timeout
            last = exc
            print("upload attempt %d failed: %r -- retrying in %ds"
                  % (attempt, exc, 15 * attempt))
            time.sleep(15 * attempt)
    raise SystemExit("upload failed after 4 attempts: %r" % (last,))


def extract_archive_claims(description):
    """Pull the frozen claims (archived commit, tarball sha256) out of an
    existing record description, so an in-place edit cannot silently
    retarget what the archive holds."""
    m_commit = re.search(r"at commit ([0-9a-f]{40})", description)
    m_sha = re.search(r"sha256 ([0-9a-f]{64})", description)
    if not m_commit or not m_sha:
        raise SystemExit("the current description carries no commit/sha256 "
                         "claim pair; refusing to edit it blind")
    return m_commit.group(1), m_sha.group(1)


def validate_edit_description(text, title, commit_sha, archive_sha256):
    """Return the list of contract violations for a description about to
    be frozen for writing (an in-place edit or a new version).

    An edit may re-title the record and rewrite its opening paragraphs; it
    may not change what the archive holds, and it may not drop the
    disclosure of how the work was made. The commit, the tarball sha256,
    the fixed SCOPE paragraph, the AI-tooling disclosure paragraph and a
    LICENSE line must survive verbatim, or the write is refused before it
    happens."""
    problems = []
    if not text.startswith(title):
        problems.append("description must start with the new title line")
    if ("at commit %s" % commit_sha) not in text:
        problems.append("archived commit claim dropped or altered")
    if ("sha256 %s" % archive_sha256) not in text:
        problems.append("archived tarball sha256 claim dropped or altered")
    if SCOPE_NOTE not in text:
        problems.append("the fixed SCOPE paragraph is missing")
    if DISCLOSURE_MARKER not in text:
        problems.append("the AI-tooling disclosure paragraph is missing")
    if "LICENSE:" not in text:
        problems.append("the LICENSE line is missing")
    return problems


def compose_description(title, owner_repo, sha, digest, extra_note="",
                        license_id=None):
    """Compose the description a deposit or a new version will carry.

    The fixed blocks are not parameters: the SCOPE paragraph and the
    AI-tooling disclosure paragraph are part of the frozen text, exactly
    like the claim pair, so no caller can drop them by omission. Order:
    title, source claims, SCOPE, the caller's note, disclosure, LICENSE."""
    desc = (
        "%s\n\n"
        "Source: https://github.com/%s at commit %s "
        "(archived tarball sha256 %s).\n"
        "Continuous integration for that exact commit: GREEN "
        "(GitHub Actions).\n\n%s"
        % (title, owner_repo, sha, digest, SCOPE_NOTE)
    )
    if extra_note:
        desc += "\n\n" + extra_note.strip()
    desc += "\n\n" + DISCLOSURE_NOTE
    if license_id:
        desc += ("\n\nLICENSE: %s, as stated by the LICENSE file in the "
                 "archived repository." % license_id)
    else:
        desc += ("\n\nLICENSE: none. The repository contains no LICENSE "
                 "file and this deposit grants no rights; all rights are "
                 "reserved by the author.")
    return desc


def compose_metadata(title, owner_repo, description, date=None, version=None,
                     license_id=None, keywords=()):
    """Build the deposition metadata shared by the deposit and new-version
    modes; only the description and the version string change per call."""
    metadata = {
        "upload_type": "software",
        "title": title,
        "description": description,
        "creators": CREATORS,
        "publication_date": date or time.strftime("%Y-%m-%d"),
        "access_right": "open",
        "related_identifiers": [{
            "identifier": "https://github.com/%s" % owner_repo,
            "relation": "isSupplementTo",
            "scheme": "url",
        }],
        "keywords": list(keywords),
    }
    if license_id:
        metadata["license"] = license_id
    if version:
        metadata["version"] = version
    return metadata


def resolve_latest_draft_id(payload):
    """The newversion action answers with the ORIGINAL resource; the new
    draft id lives in links.latest_draft. Refuse to guess when absent."""
    latest = (payload.get("links") or {}).get("latest_draft")
    if not latest or "/" not in latest:
        raise SystemExit("newversion response carries no usable "
                         "latest_draft link; inspect the record")
    return latest.rstrip("/").rsplit("/", 1)[-1]


def same_concept(draft, source):
    """A new-version draft must share the source record's concept id;
    compare as strings so the API's int/str forms both pass."""
    return str(draft.get("conceptrecid")) == str(source.get("conceptrecid"))


def file_matches_local(stored_checksum, blob):
    """True when a draft file's stored checksum (md5, possibly prefixed
    like "md5:...") equals the md5 of the local bytes to be claimed. An
    absent checksum fails closed: publish only what can be verified."""
    stored = (stored_checksum or "").split(":")[-1].strip().lower()
    return bool(stored) and stored == hashlib.md5(blob).hexdigest()


def public_get(url, tries=6, wait=5):
    """Retry-wrapped anonymous GET (the public record may lag an edit)."""
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 503) and attempt < tries:
                time.sleep(wait)
                continue
            raise
    return None


def edit_record_metadata(args):
    """In-place metadata edit of an already-published deposition.

    Legacy flow: unlock (actions/edit), PUT the merged metadata, then
    republish when --publish is passed. The DOI, the concept DOI and the
    archived files never change. Without --publish the edit stays
    unpublished, which is the safe checkpoint between the two halves."""
    dep_url = "%s/depositions/%s" % (API, args.edit_record)
    cur = get(dep_url, args.token)
    if not cur.get("submitted"):
        raise SystemExit("record %s is not published; refusing to edit"
                         % args.edit_record)
    old_md = cur.get("metadata", {})
    old_desc = old_md.get("description", "")
    commit_sha, archive_sha256 = extract_archive_claims(old_desc)
    with open(args.description_file, "r", encoding="utf-8") as fh:
        new_desc = fh.read().replace("\r\n", "\n").strip()
    problems = validate_edit_description(new_desc, args.title, commit_sha,
                                         archive_sha256)
    if problems:
        for p in problems:
            print("REFUSED: %s" % p)
        raise SystemExit("description failed the edit contract")
    new_keywords = [k.strip() for k in args.keywords.split(",")
                    if k.strip()]
    if not new_keywords:
        new_keywords = list(old_md.get("keywords", []))
        print("keywords not passed -- keeping the current %d"
              % len(new_keywords))

    print("record:      %s" % args.edit_record)
    print("doi:         %s" % cur.get("doi"))
    print("title old:   %s" % old_md.get("title"))
    print("title new:   %s" % args.title)
    print("desc bytes:  %d -> %d" % (len(old_desc), len(new_desc)))
    print("desc sha256: %s -> %s"
          % (hashlib.sha256(old_desc.encode("utf-8")).hexdigest(),
             hashlib.sha256(new_desc.encode("utf-8")).hexdigest()))
    print("keywords:    %d -> %d" % (len(old_md.get("keywords", [])),
                                    len(new_keywords)))
    if args.dry_run:
        print("DRY RUN -- nothing written. New description follows:")
        print("=" * 60)
        print(new_desc)
        print("=" * 60)
        return 0

    merged = {}
    for key in ("upload_type", "creators", "publication_date",
                "access_right", "related_identifiers", "license", "version"):
        if key in old_md:
            merged[key] = old_md[key]
    merged["title"] = args.title
    merged["description"] = new_desc
    merged["keywords"] = new_keywords

    post("%s/actions/edit" % dep_url, args.token)
    print("record unlocked for editing")
    try:
        out = put(dep_url, args.token, payload={"metadata": merged})
    except SystemExit:
        print("PUT failed -- discarding the edit so the record is left "
              "exactly as published")
        post("%s/actions/discard" % dep_url, args.token)
        raise
    got = out.get("metadata", {})
    got_desc = got.get("description", "")
    if (got.get("title") != args.title
            or hashlib.sha256(got_desc.encode("utf-8")).hexdigest()
            != hashlib.sha256(new_desc.encode("utf-8")).hexdigest()):
        raise SystemExit("PUT echo does not match what was sent; record "
                         "left unpublished -- inspect before retrying")
    print("edit applied: title/description/keywords updated in the draft")

    if not args.publish:
        print("NOT REPUBLISHED (safe checkpoint). Re-run with --publish to "
              "republish; the edit is idempotent.")
        return 0
    done = post("%s/actions/publish" % dep_url, args.token)
    print("REPUBLISHED")
    print("doi:        %s" % done.get("doi"))
    print("conceptdoi: %s" % done.get("conceptdoi"))
    print("url:        https://doi.org/%s" % done.get("doi"))
    try:
        pub = public_get("https://zenodo.org/api/records/%s"
                         % args.edit_record)
        pm = pub.get("metadata", {})
        print("public title now: %s" % pm.get("title"))
        print("public keywords:  %d items" % len(pm.get("keywords", [])))
        if pm.get("title") != args.title:
            print("note: public record still shows the old title; the "
                  "Zenodo cache may lag a moment -- re-check shortly")
    except urllib.error.HTTPError as exc:
        print("note: public re-check got HTTP %s; re-check manually"
              % exc.code)
    return 0


def new_version_deposit(args, blob, digest, fname, desc, metadata, tmp):
    """Mint a new version of a published record and fill the draft.

    Legacy flow: POST actions/newversion, resolve links.latest_draft,
    drop the inherited file copy of the previous version, upload the new
    tarball, PUT the composed metadata, and publish only when --publish
    is passed. A fill-then-publish sequence cannot call newversion twice
    (Zenodo refuses with "files.enabled: Please remove all files first"
    once the open draft holds files), so --deposition-id resumes the
    named draft directly. The original version, its DOI and its files
    never change; the new version gets its own DOI under the same concept
    DOI. The description already passed the frozen-claims contract in
    main() before this was called."""
    src_url = "%s/depositions/%s" % (API, args.new_version_of)
    cur = get(src_url, args.token)
    if not cur.get("submitted"):
        raise SystemExit("record %s is not published; refusing to mint a "
                         "new version" % args.new_version_of)
    if args.deposition_id:
        draft_id = args.deposition_id
        print("resuming the named new-version draft (no newversion call)")
    else:
        out = post("%s/actions/newversion" % src_url, args.token)
        draft_id = resolve_latest_draft_id(out)
    draft = get("%s/depositions/%s" % (API, draft_id), args.token)
    if draft.get("submitted"):
        raise SystemExit("draft %s is already published; nothing to fill"
                         % draft_id)
    if not same_concept(draft, cur):
        raise SystemExit("draft %s does not belong to the same concept as "
                         "record %s; refusing" % (draft_id,
                                                  args.new_version_of))
    print("record:      %s (concept %s)"
          % (args.new_version_of, cur.get("conceptrecid")))
    print("new draft:   %s (state %s)" % (draft_id, draft.get("state")))
    print("title:       %s" % args.title)
    print("desc bytes:  %d" % len(desc.encode("utf-8")))
    print("desc sha256: %s" % hashlib.sha256(desc.encode("utf-8")).hexdigest())
    have = {f.get("filename") for f in draft.get("files", [])}
    for f in draft.get("files", []):
        if f.get("filename") != fname:
            delete("%s/depositions/%s/files/%s"
                   % (API, draft_id, f.get("id")), args.token)
            print("inherited file dropped from draft: %s"
                  % f.get("filename"))
    if fname in have:
        stored = ""
        for f in draft.get("files", []):
            if f.get("filename") == fname:
                stored = f.get("checksum", "")
        if not file_matches_local(stored, blob):
            raise SystemExit("draft file %s is not the local bytes "
                             "(stored checksum %r); refusing to continue"
                             % (fname, stored))
        print("file already present in draft, checksum matches local "
              "bytes, upload skipped: %s" % fname)
    else:
        with open(tmp, "rb") as fh:
            payload = fh.read()
        post_multipart("%s/depositions/%s/files" % (API, draft_id),
                       args.token, "file", fname, payload)
        print("file uploaded: %s (%d bytes, sha256=%s)"
              % (fname, len(payload), digest))
    got = put("%s/depositions/%s" % (API, draft_id), args.token,
              payload={"metadata": metadata})
    gm = got.get("metadata", {})
    gd = gm.get("description", "")
    if (gm.get("title") != args.title
            or hashlib.sha256(gd.encode("utf-8")).hexdigest()
            != hashlib.sha256(desc.encode("utf-8")).hexdigest()):
        raise SystemExit("PUT echo does not match what was sent; the draft "
                         "is left unpublished -- inspect before retrying")
    print("draft metadata set; PUT echo matches verbatim")
    if not args.publish:
        print("NOT PUBLISHED (safe checkpoint). The draft is private and "
              "modifiable; re-run the same command with --publish to "
              "publish it. id=%s" % draft_id)
        return 0
    done = post("%s/depositions/%s/actions/publish" % (API, draft_id),
                args.token)
    print("PUBLISHED")
    print("doi:        %s" % done.get("doi"))
    print("conceptdoi: %s" % done.get("conceptdoi"))
    print("url:        https://doi.org/%s" % done.get("doi"))
    print("archive:    %d bytes  sha256=%s" % (len(blob), digest))
    try:
        os.remove(tmp)
    except OSError:
        pass
    try:
        pub = public_get("https://zenodo.org/api/records/%s" % draft_id)
        pm = pub.get("metadata", {})
        print("public title:   %s" % pm.get("title"))
        print("public version: %s" % pm.get("version"))
    except urllib.error.HTTPError as exc:
        print("note: public re-check got HTTP %s; re-check manually"
              % exc.code)
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=None, help="OWNER/NAME on GitHub")
    ap.add_argument("--sha", default=None, help="full commit sha to archive")
    ap.add_argument("--title", required=True)
    ap.add_argument("--license", default=None,
                    help="Zenodo license id, e.g. mit-license. Omit when "
                         "the repository grants none.")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--draft-only", action="store_true")
    ap.add_argument("--extra-note", default="",
                    help="appended verbatim to the description; use it to "
                         "state the repository's own verification story "
                         "rather than the generic CI line")
    ap.add_argument("--date", default=None,
                    help="publication date recorded in the metadata "
                         "(default: today, local time)")
    ap.add_argument("--version", default=None,
                    help="version string recorded in the metadata")
    ap.add_argument("--deposition-id", default=None,
                    help="resume an existing draft instead of creating one; "
                         "with --new-version-of it names the new-version "
                         "draft to resume")
    ap.add_argument("--new-version-of", default=None,
                    help="mint a NEW VERSION of this published record id; "
                         "the new draft replaces the archived snapshot with "
                         "--sha under the same concept DOI and must satisfy "
                         "the same frozen-claims contract as the edit mode")
    ap.add_argument("--extra-note-file", default=None,
                    help="read the extra-note text from this UTF-8 file "
                         "(for notes too long to quote on a command line)")
    ap.add_argument("--publish", action="store_true",
                    help="publish: the draft named by --deposition-id in "
                         "deposit mode, the edited record in --edit-record "
                         "mode, the filled new version in --new-version-of "
                         "mode")
    ap.add_argument("--edit-record", default=None,
                    help="in-place metadata edit of this published record "
                         "id (title/description/keywords only; DOI and "
                         "archived files stay untouched)")
    ap.add_argument("--description-file", default=None,
                    help="full replacement description for --edit-record; "
                         "the archived-object claims must survive verbatim")
    ap.add_argument("--dry-run", action="store_true",
                    help="with --edit-record: print the change, write "
                         "nothing")
    ap.add_argument("--token", default=os.environ.get("ZENODO_TOKEN", ""))
    args = ap.parse_args(argv)

    if not args.token:
        raise SystemExit("no token: set ZENODO_TOKEN")

    if args.edit_record:
        if not args.description_file:
            raise SystemExit("--edit-record requires --description-file")
        return edit_record_metadata(args)

    if args.dry_run:
        raise SystemExit("--dry-run only applies to --edit-record")

    if not args.repo or not args.sha:
        raise SystemExit("deposit mode needs --repo and --sha")

    owner_repo = args.repo
    archive_url = ("https://github.com/%s/archive/%s.tar.gz"
                   % (owner_repo, args.sha))
    print("fetching %s" % archive_url)
    with urllib.request.urlopen(archive_url) as resp:
        blob = resp.read()
    digest = hashlib.sha256(blob).hexdigest()
    fname = "%s-%s.tar.gz" % (owner_repo.split("/")[1], args.sha[:12])
    print("archive: %d bytes  sha256=%s" % (len(blob), digest))

    tmp = os.path.join(os.environ.get("TEMP", "."), fname)
    with open(tmp, "wb") as fh:
        fh.write(blob)

    extra_note = args.extra_note
    if args.extra_note_file:
        with open(args.extra_note_file, "r", encoding="utf-8") as fh:
            extra_note = fh.read().replace("\r\n", "\n").strip()

    desc = compose_description(args.title, owner_repo, args.sha, digest,
                               extra_note=extra_note,
                               license_id=args.license)
    problems = validate_edit_description(desc, args.title, args.sha, digest)
    if problems:
        for p in problems:
            print("REFUSED: %s" % p)
        raise SystemExit("composed description failed the frozen-claims "
                         "contract; nothing written")

    metadata = compose_metadata(
        args.title, owner_repo, desc, date=args.date, version=args.version,
        license_id=args.license,
        keywords=[k.strip() for k in args.keywords.split(",") if k.strip()])

    if args.new_version_of:
        return new_version_deposit(args, blob, digest, fname, desc, metadata,
                                   tmp)

    if args.publish:
        done = post("%s/depositions/%s/actions/publish"
                    % (API, args.deposition_id), args.token)
        print("PUBLISHED")
        print("doi:        %s" % done.get("doi"))
        print("conceptdoi: %s" % done.get("conceptdoi"))
        print("url:        https://doi.org/%s" % done.get("doi"))
        print("archive:    %d bytes  sha256=%s" % (len(blob), digest))
        return 0

    if args.deposition_id:
        dep_id = args.deposition_id
        print("resuming draft deposition %s" % dep_id)
        put("%s/depositions/%s" % (API, dep_id), args.token,
            payload={"metadata": metadata})
        print("draft metadata updated")
        # Idempotent resume: a re-upload of an identical filename is not
        # accepted and the connection is dropped mid-body, which reads as
        # a network fault. Ask what the draft already holds first.
        have = {f["filename"] for f in get("%s/depositions/%s"
                                           % (API, dep_id), args.token)
                .get("files", [])}
        print("files already in draft: %s" % (sorted(have) or "none"))
    else:
        dep = post(API + "/depositions", args.token,
                   payload={"metadata": metadata})
        dep_id = dep["id"]
        print("draft deposition %s" % dep_id)
        have = set()

    if fname in have:
        print("file already present, upload skipped: %s" % fname)
    else:
        with open(tmp, "rb") as fh:
            payload = fh.read()
        post_multipart("%s/depositions/%s/files" % (API, dep_id), args.token,
                       "file", fname, payload)
        print("file uploaded: %s (%d bytes, sha256=%s)"
              % (fname, len(payload), digest))

    if args.draft_only:
        print("DRAFT ONLY -- not published. id=%s" % dep_id)
        return 0

    done = post("%s/depositions/%s/actions/publish" % (API, dep_id), args.token)
    print("PUBLISHED")
    print("doi:        %s" % done.get("doi"))
    print("conceptdoi: %s" % done.get("conceptdoi"))
    print("url:        https://doi.org/%s" % done.get("doi"))
    print("archive:    %d bytes  sha256=%s" % (len(blob), digest))
    try:
        os.remove(tmp)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


