# V1 sources — audit_ecdsa/captures/ (frozen 2026-10-19)

Comparison values for every row are extracted ONLY from the captured files
below (by `audit_ecdsa/build_manifest.py`); the claim's printed strings are a
cross-check only. Fetch: 2026-10-19 01:24–01:30 UTC (curl 8.13.0, Windows).
Derivation: `pdftotext` (poppler) 26.01.0 for PDF -> txt; `audit_ecdsa/tool_claim_text.py`
for the claim html -> txt (byte-reproducible; verified with `cmp` during freeze
prep). "sha256 raw" = as-fetched bytes; "sha256LF" = registry convention
(CRLF -> LF). They differ only for the PDFs (which contain CRLF byte pairs;
PDFs are pinned `binary` in .gitattributes and committed unconverted).

| file | role | origin | bytes | sha256 raw | sha256LF |
|---|---|---|---|---|---|
| captures/claim_anthropic_ecdsa_curve_origins.html | claim (verbatim) | https://www.anthropic.com/research/ecdsa-curve-origins | 171170 | 266554ce62f84b3c597193b76f7046655004601e39539e2f7619b6231898781d | = raw |
| captures/claim_anthropic_ecdsa_curve_origins.txt | claim text (derived) | tool_claim_text.py over the .html | 18734 | 35dfbdd84db918e2b678aa0371191f621c7fcac1f1ef28252cf8c43844ad77be | = raw |
| captures/fips186-4.pdf | standards copy | https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf | 941581 | 081dcccbcd8a1ffe4b5cca7b30dcedb739910e65b39e6182a3cdbae3e5f61689 | 34222f3b6a9442a3491b6ace810c64da0a4e43b779737ad53a287656e7fc5f6b |
| captures/fips186-4.txt | extraction (derived) | pdftotext -layout | 268348 | 5da836de5eb14ae8bb4df2fdddaa7cf25df3ba1ad404fb8cf5050a9af1898ab9 | = raw |
| captures/fips186-2-change1.pdf | standards copy | https://csrc.nist.gov/CSRC/media/Publications/fips/186/2/archive/2001-10-05/documents/FIPS186-2-change1.pdf | 506186 | bad948fd373d7b4112e52b86d0b8f17ca969fb328315d93f19d02782ccc68356 | 0c411bcd9c806f2dccd86ea4f663e86cc864148ce5de342ed3c13a4e46bbb38b |
| captures/fips186-2-change1.txt | extraction (derived) | pdftotext -layout | 91834 | e85f5165cc8381bf61963c95af4ca7cebe37789486d92c8693200284116ed798 | = raw |
| captures/sec2-v2.pdf | standards copy | https://www.secg.org/sec2-v2.pdf | 306784 | 87b8f3703364ed5b21ba8582e411cc0cbf477bcaa3f4f45e0d6580d1c00d9952 | b52e0a56a18bef949c4342a891b78174c0977a516e2e494247bfb9159c9ea8e2 |
| captures/sec2-v2.txt | extraction (derived) | pdftotext -layout | 74669 | 93d6a91157c802de1226c08fcf36ecd78d292ac814d12bb4deb54e77362f3300 | = raw |
| captures/x962-1998-draft.pdf | standards copy (ANSI X9.62-1998 draft, 1998-09-20; archival mirror of grouper.ieee.org) | https://safecurves.cr.yp.to/grouper.ieee.org/groups/1363/private/x9-62-09-20-98.pdf | 761099 | 6cb44495bf816008afc11cc6cf65124b484654b2d260559dab6dde55e2609da7 | 03230cade876901515088c170048660ce1955dd090c1c7ef875f46bcbcc45852 |
| captures/x962-1998-draft.txt | extraction (derived) | pdftotext -layout | 424451 | da957ea6ccd36df852f3ceb81f301cae3d57c19c25fbc014c1a6bdfa1ee7a299 | = raw |
| captures/bc_SECNamedCurves.java | independent implementation (Bouncy Castle) | https://raw.githubusercontent.com/bcgit/bc-java/main/core/src/main/java/org/bouncycastle/asn1/sec/SECNamedCurves.java | 46877 | 486aa8e242427ea36492f4775a626fafbfe1b90071800fbef8d243707dd0fa55 | = raw |
| captures/neuromancer_prime192v2.html | independent database | https://neuromancer.sk/std/x962/prime192v2/ | 252529 | ef018c91553ccde243cb6c47405c14c68cf595bf07cfe1fdbaef27beef7baa2c | = raw |
| captures/neuromancer_prime192v3.html | independent database | https://neuromancer.sk/std/x962/prime192v3/ | 252529 | bfc658dc5687d3b149108f7ea708de943bd918efea4d6fc54dd53e1d52df75cb | = raw |
| captures/neuromancer_prime239v1.html | independent database | https://neuromancer.sk/std/x962/prime239v1/ | 253573 | d40e415d883418b9263608bb922e6c12b9a60b4356e723499447d07b3b83300b | = raw |
| captures/neuromancer_prime239v2.html | independent database | https://neuromancer.sk/std/x962/prime239v2/ | 253569 | 89848baf1e2451b523a247f77f975e345754380d8c72b6504c99bbc32ce0d3ff | = raw |
| captures/neuromancer_prime239v3.html | independent database | https://neuromancer.sk/std/x962/prime239v3/ | 252435 | 8a8f2bb06df9e72e58c93c0fd8f03df0364db5ecba94d18dc6b04602e822d7a0 | = raw |
| captures/saweis_nist_curve_seed_origins.html | context ONLY (not a comparison source; stated derived from the neuromancer database) | https://saweis.net/posts/nist-curve-seed-origins.html | 25781 | 8218c3c2f16435884691767b6d0259bf41e25819bca91a92d688cd41d8fb4ede | = raw |

## Row coverage and extraction anchors

Anchors are as recorded in `seeds_manifest.json` ("ref" per source; line
numbers are 1-based, `\n`-based, of the frozen `.txt`).

- R01 prime239v1: x962-1998-draft.txt line 6146,6752 + neuromancer_prime239v1.html
- R02 prime239v2: x962-1998-draft.txt line 6769 + neuromancer_prime239v2.html
- R03 prime239v3: x962-1998-draft.txt line 6786 + neuromancer_prime239v3.html
- R04 P-192: fips186-4.txt line 3541 + fips186-2-change1.txt line 1102 + sec2-v2.txt line 342 + bc_SECNamedCurves.java line 323
- R05 prime192v3: x962-1998-draft.txt line 6725 + neuromancer_prime192v3.html
- R06 prime192v2: x962-1998-draft.txt line 6712 + neuromancer_prime192v2.html
- R07 P-521: fips186-4.txt line 3606 + fips186-2-change1.txt line 1192 + sec2-v2.txt line 577 + bc_SECNamedCurves.java line 526
- R08 P-256: fips186-4.txt line 3571 + fips186-2-change1.txt line 1142 + sec2-v2.txt line 483 + bc_SECNamedCurves.java line 467
- R09 P-384: fips186-4.txt line 3587 + fips186-2-change1.txt line 1164 + sec2-v2.txt line 528 + bc_SECNamedCurves.java line 496
- R10 P-224: fips186-4.txt line 3553 + fips186-2-change1.txt line 1122 + sec2-v2.txt line 408 + bc_SECNamedCurves.java line 395
- R11 B-233: fips186-4.txt line 3740 + fips186-2-change1.txt line 1329 + sec2-v2.txt line 917 + bc_SECNamedCurves.java line 867
- R12 B-283: fips186-4.txt line 3790 + fips186-2-change1.txt line 1379 + sec2-v2.txt line 1030 + bc_SECNamedCurves.java line 962
- R13 B-409: fips186-4.txt line 3857 + fips186-2-change1.txt line 1437 + sec2-v2.txt line 1114 + bc_SECNamedCurves.java line 1024
- R14 B-571: fips186-4.txt line 3927 + fips186-2-change1.txt line 1515 + sec2-v2.txt line 1204 + bc_SECNamedCurves.java line 1090
- R15 B-163 (seed-only; no (t,n) pair published): fips186-4.txt line 3689 + fips186-2-change1.txt line 1280 + sec2-v2.txt line 844 + bc_SECNamedCurves.java line 747

Extraction rules (implemented in `build_manifest.py`; ALL occurrences of a
value in a file must agree, else the build aborts):

- fips186-4.txt: `SEED = <5 x 8 hex>` following a `D.x Curve <name>` heading.
- fips186-2-change1.txt: `s= <5 x 8 hex>` following a `Curve <name>` heading.
- sec2-v2.txt: `S = <5 x 8 hex>` following `Recommended Parameters <sec-name>`.
- bc_SECNamedCurves.java: `byte[] S = Hex.decodeStrict("<40 hex>");` within the
  curve's holder block.
- x962-1998-draft.txt: explicit frozen line anchors (above). NOTE: that file
  also contains example/test seeds for other constructs; only the anchored lines
  are read (e.g., line 6769 is printed as `SEED= E8B40116 ...` — no space
  before `=`).
- neuromancer pages: JSON `"seed": "<40 hex>"` (all occurrences must agree).

## Independence notes

- Comparison-source origins (6): fips186-4 and fips186-2-change1 (NIST; same
  organization, separate documents/editions), sec2-v2 (SECG), bc-java
  (Bouncy Castle, independent implementation table), x962-1998-draft (the
  ANSI standard itself; archival mirror), neuromancer (independent curve
  database). Every row draws on at least two different origins; all rows have
  >=2 sources (v-curves: 2; NIST rows: 4).
- NOT counted as sources: the claim page (cross-check only), the saweis page
  (context only; derived from the neuromancer database per its own text).
- Cross-source agreement is machine-enforced at manifest build; zero
  disagreements occurred at freeze.

## Excluded during source survey (not in the package)

- OpenSSL `crypto/ec/ec_curve.c` (master, captured 2026-10-19): defines the
  X9.62 v-curves but stores no seed values -> cannot serve as a source.
- Crypto++ `eccrypto.cpp`: curve parameter tables carry no seed field -> cannot
  serve.
- sawes.net original post: unreachable at fetch time (curl error 28; an
  archive.org attempt was rate-limited); the author's relocated page
  (saweis.net, captured above) is context only.

Pins: `seeds_manifest.json` "captures" block (raw + LF + size per file);
prereg §2 pins this file and the manifest by sha256LF.
