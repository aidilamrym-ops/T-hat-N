# Captured sources (frozen snapshots)

These files are byte-frozen read-only snapshots collected for the P2 audit
(`reports/AUDIT_COLLATZ_PREREG_2026-10-19.md`). They are reference captures,
not audit results; the audit re-fetches and compares at execution time
(items S1/S2 and the H1 claims).

All files were fetched over HTTPS. sha256 values are of the raw bytes as saved.
These files are LF-only, so sha256LF equals raw sha256 for every file.

| file | source URL | fetched (local, UTC+8) | bytes | sha256 |
|---|---|---|---|---|
| site_path_records.html | https://pcbarina.fit.vutbr.cz/path-records.htm | 2026-10-19 01:53 | 15462 | c4cc03a16ab4c642c9b1fff65fcd82b3c156cbc6ad6074d07c712d406dba468b |
| site_news.html | https://pcbarina.fit.vutbr.cz/news.htm | 2026-10-19 01:53 | 2595 | 642dcfb92326b05eb623fa933cce7cfac77817d3416b6cb31bb7423386395ea3 |
| site_main.html | https://pcbarina.fit.vutbr.cz/ | 2026-10-19 02:06 | 3379 | c31f4bbbdbcbe58778b75bb5c2ec4386ad57216f3c74a0ff53682bf24a48798e |
| oeis_A006884.txt | https://oeis.org/A006884/b006884.txt | 2026-10-19 01:53 | 1456 | 657ec2fbc0ade279ce052005ae11234ea795c47b0fdaf9add6fff5d4f214de86 |
| oeis_A006885.txt | https://oeis.org/A006885/b006885.txt | 2026-10-19 02:03 | 2516 | 7007b273e50fc2d51afba6e740b201ae61e3ae4f8b5898e3880bb6c5156bf053 |
| oeis_A006877.txt | https://oeis.org/A006877/b006877.txt | 2026-10-19 01:53 | 2254 | 4bdd9c264ffb33f6252adad6716f8f0ad55c84687d4300a9bfbe646a1a81327f |
| oeis_A006878.txt | https://oeis.org/A006878/b006878.txt | 2026-10-19 02:03 | 1237 | 1aebb537ac7cbb0290e8614b8e58e879efa24843277c0c437a72672f965233ac |

Stability notes (freeze-time checks on 2026-10-19; reference only, not audit
evidence; the formal re-fetch and comparison is item S1/S2 at execution):

- All seven URLs were re-fetched once with `curl.exe` 8.13.0 and compared
  byte-for-byte: six files matched their freeze copies exactly. `site_main.html`
  differed from an earlier capture (`ebdf4f29...`) only in the single
  `Generated: ...` line; the frozen copy here is the later fetch
  (`c31f4bbb...`), and the audit normalizes exactly that line before comparing.
- The pcbarina pages belong to a live project; these freeze copies are the
  reference of record for the audit.
- OEIS b-files are plain term lists, reproduced here solely as frozen
  verification references for the audit. Source: The On-Line Encyclopedia of
  Integer Sequences (https://oeis.org); the b-file headers contain the original
  attribution lines (see the files themselves).
- Context-only captures not committed here: `ericr.nl` delay-records page
  (HTTPS endpoint failed certificate verification at recon; not part of the
  frozen set) and one scratch HTML variant used during freeze-time checking.


