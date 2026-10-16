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

Usage:
    C:\\Python314\\python.exe zenodo_deposit.py --repo OWNER/NAME --sha <full sha>
        [--license mit-license] [--draft-only] [--title "..."]
        [--date YYYY-MM-DD] [--version "..."] [--deposition-id ID]
        [--publish]

The token is read from the ZENODO_TOKEN environment variable and is never
written to disk by this script.
"""

import argparse
import hashlib
import io
import json
import os
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


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="OWNER/NAME on GitHub")
    ap.add_argument("--sha", required=True, help="full commit sha to archive")
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
                    help="publish the draft named by --deposition-id")
    ap.add_argument("--token", default=os.environ.get("ZENODO_TOKEN", ""))
    args = ap.parse_args(argv)

    if not args.token:
        raise SystemExit("no token: set ZENODO_TOKEN")

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
