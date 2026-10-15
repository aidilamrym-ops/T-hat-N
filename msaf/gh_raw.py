"""Fetch raw file bytes from a GitHub repo and write them to disk verbatim."""
import sys
import urllib.request

repo, path, dest = sys.argv[1], sys.argv[2], sys.argv[3]
req = urllib.request.Request(
    "https://api.github.com/repos/aidilamrym-ops/%s/contents/%s" % (repo, path),
    headers={"Accept": "application/vnd.github.raw"})
with urllib.request.urlopen(req) as r:
    blob = r.read()
open(dest, "wb").write(blob)
print("%s: %d bytes, CRLF=%d, LF=%d"
      % (dest, len(blob), blob.count(b"\r\n"), blob.count(b"\n")))
