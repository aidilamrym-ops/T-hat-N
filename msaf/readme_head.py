"""Print the first N lines of a repo README via the GitHub API."""
import base64
import json
import sys
import urllib.request

repo, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 25
req = urllib.request.Request(
    "https://api.github.com/repos/aidilamrym-ops/%s/readme" % repo,
    headers={"Accept": "application/vnd.github.raw"})
try:
    with urllib.request.urlopen(req) as r:
        text = r.read().decode("utf-8", "replace")
except Exception as exc:  # 404 when there is no README
    print("no README: %s" % exc)
    raise SystemExit(1)
print("\n".join(text.splitlines()[:n]))


