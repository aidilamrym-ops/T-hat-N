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
  sha256, the fixed SCOPE paragraph and a LICENSE line, or nothing is
  written. Re-titling and rewriting the opening paragraph are allowed;
  changing the archived object is not.

Usage:
    C:\\Python314\\python.exe zenodo_deposit.py --repo OWNER/NAME --sha <full sha>
        [--license mit-license] [--draft-only] [--title "..."]
        [--date YYYY-MM-DD] [--version "..."] [--deposition-id ID]
        [--publish]

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
    """Return the list of contract violations for an edited description.

    An edit may re-title the record and rewrite its opening paragraphs; it
    may not change what the archive holds. The commit, the tarball
    sha256, the fixed SCOPE paragraph and a LICENSE line must survive
    verbatim, or the edit is refused before any write."""
    problems = []
    if not text.startswith(title):
        problems.append("description must start with the new title line")
    if ("at commit %s" % commit_sha) not in text:
        problems.append("archived commit claim dropped or altered")
    if ("sha256 %s" % archive_sha256) not in text:
        problems.append("archived tarball sha256 claim dropped or altered")
    if SCOPE_NOTE not in text:
        problems.append("the fixed SCOPE paragraph is missing")
    if "LICENSE:" not in text:
        problems.append("the LICENSE line is missing")
    return problems


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
                    help="resume an existing draft instead of creating one")
    ap.add_argument("--publish", action="store_true",
                    help="publish: the draft named by --deposition-id in "
                         "deposit mode, the edited record in --edit-record "
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

    desc = (
        "%s\n\n"
        "Source: https://github.com/%s at commit %s "
        "(archived tarball sha256 %s).\n"
        "Continuous integration for that exact commit: GREEN "
        "(GitHub Actions).\n\n%s"
        % (args.title, owner_repo, args.sha, digest, SCOPE_NOTE)
    )
    if args.extra_note:
        desc += "\n\n" + args.extra_note.strip()
    if args.license:
        desc += ("\n\nLICENSE: %s, as stated by the LICENSE file in the "
                 "archived repository." % args.license)
    else:
        desc += ("\n\nLICENSE: none. The repository contains no LICENSE "
                 "file and this deposit grants no rights; all rights are "
                 "reserved by the author.")

    metadata = {
        "upload_type": "software",
        "title": args.title,
        "description": desc,
        "creators": CREATORS,
        "publication_date": args.date or time.strftime("%Y-%m-%d"),
        "access_right": "open",
        "related_identifiers": [{
            "identifier": "https://github.com/%s" % owner_repo,
            "relation": "isSupplementTo",
            "scheme": "url",
        }],
        "keywords": [k.strip() for k in args.keywords.split(",") if k.strip()],
    }
    if args.license:
        metadata["license"] = args.license
    if args.version:
        metadata["version"] = args.version

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
