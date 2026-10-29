# Audit P1 â€” L1 sweep penuh (opsi pra-reg Â§8): rilis review-01787854-v3 â€” LULUS PENUH

Tanggal: 2026-10-18. Status: **SELESAI â€” semua step exit 0**
(`RESULT PASS: fresh sweep matches every canonical line and all 3149013
sealed rows N=690988..3840000`; `RESULT: FULL SWEEP REPLAY AND METADATA
PASS`; `RESULT: L1-SWEEP COMPLETE`). Ini addendum for entri registry
`A-2026-0001`; report L4 `reports/AUDIT_DBN_L4REPORT_2026-10-17.md` tetap
beku (frasa "L1 not-run" / "sweep no dijalankan" in sana and in note
L1 pra-sweep = snapshot saat itu).

## 1. Urutan pra-registrasi (terkunci SEBELUM eksekusi)

- Header log + runner + watchdog (`reports/audit_p1_l1_sweep_2026-10-18.log`,
  `audit_p1/l1_sweep.sh`, `audit_p1/l1_sweep_watchdog.sh`) dipush in commit
  `295e7163999a5518c6af1ecf65530149bcef1d75` **sebelum perintah sweep
  pertama**; blok mesin in bawah header merekam `repo_commit: 295e716â€¦` +
  sha256 runner (`911f63b8be290581f773c3114cb3ebca7597f167556dfe08ff86bf32fe1cdfff`,
  salinan engine) saat run start â†’ urutan commit < perintah terekam mesin.
- Keputusan owner (menjalankan opsi Â§8) tercatat **sebelum** result; no
  ada parameter, toleransi, seleksi, or cap which diubah setelah result
  terlihat.
- Cap pra-registrasi: **6 jam** dinding dari `started_utc`, dikawal mekanis
  oleh `l1_sweep_watchdog.sh` (menulis stop-record ke log bila tercapai).
  Aktual: jauh in bawah cap (Â§3), watchdog **no memutus**.

## 2. Input ter-pin & delta lingkungan (direkam pra-eksekusi)

- OCI archive sha256
  `87a4695e86b535eac48b0a39e1999028e8a18249eb1c95cc9715e4a91afb83c6`
  (172.810.240 B; pin prereg, no berubah); image (podman digest)
  `sha256:6e29bc53adc5a4337802da2b5a219720e3da9dcc1b87c546b96b6126d8b9975d`;
  image `.Id` (config digest)
  `5ccd9e3f7f8fdde6ee6a35c2542efc17b6a7247d615ad03c1db5bd47e3c8f42d` =
  `EXPECTED_IMAGE_ID` ter-pin â†’ **VERDICT: image id matches the pinned
  value**.
- Tree rilis: checkout `2e9976c4becbf97e31c56fe75fce07cdff5dd4ea`; tree
  `7f15ecf8c3dbc73d547a2d4a3f2287bd87802f44`; `status --porcelain` kosong.
- Label identitas image: `org.opencontainers.image.dbn.platform =
  linux/amd64`; base digest `sha256:52df9b1eâ€¦`; ubuntu-snapshot
  `20260723T000000Z`; source
  `github.com/judegomila/dbn-lambda-01787854-candidate-audit`.
- Delta lingkungan (direkam sebelum eksekusi, no diadaptasi setelahnya):
  CLI `docker` no ada in distro audit â†’ shim `/usr/local/bin/docker`
  (`exec podman "$@"`; sha256
  `3b0d64869d5e8d4c065e742c79a9482313c56b02c559ff47fabec5a60b0b404c`) â†’
  podman 5.7.0; permukaan container sama with replay L1 which already lulus
  (verify.sh + container review).
- Skrip rilis apa adanya: `scripts/run_full_sweep.sh`; `IMAGE` +
  `EXPECTED_IMAGE_ID` ter-pin; tanpa env override (`ALLOW_DIRTY_REPO`,
  `ALLOW_UNPINNED_IMAGE` no diset); guard rilis jalan: `replay_guard`
  require/prepare (fresh path `/root/l1/replay-out/sweep`), penolakan repo
  kotor, cek identitas image + label reviewed-build, probe bind-mount.

## 3. Timeline & budgeting

- Blok lingkungan pertama `2026-10-18T11:09:52+0800` (03:09:52Z); cek
  tree/image/fresh-path `11:09:53â€“56+0800`, semua exit 0.
- `started_utc = 2026-10-18T03:10:00Z` â†’ `finished_utc =
  2026-10-18T05:31:18Z` â†’ **â‰ˆ 2 j 21 m 18 s** dinding.
- Batas cap 6 j = 09:10:00Z â†’ no tersentuh (margin â‰ˆ 3 j 39 m); no
  ada stop-record watchdog in log.
- Inventaris sha256 + penanda akhir `13:31:19â€“20+0800` (05:31:19â€“20Z).

## 4. Hasil

Komparator akhir (skrip rilis) â€” baris verba in log:

```text
RESULT PASS: fresh sweep matches every canonical line and all 3149013 sealed rows N=690988..3840000
RESULT: FULL SWEEP REPLAY AND METADATA PASS
```

Penanda akhir runner: `RESULT: L1-SWEEP COMPLETE (all steps exit 0 as
recorded above)`.

15/15 lane `[PASS]` (verbatim per lane in log):

| lane | rows | N |
|---|---|---|
| p235711_690988_690995.log | 8 | 690988..690995 |
| p235711_690996_691500.log | 505 | 690996..691500 |
| p235711_691501_697000.log | 5.500 | 691501..697000 |
| p235711_697001_728999.log | 31.999 | 697001..728999 |
| p2357_729000_818999.log | 90.000 | 729000..818999 |
| p235_819000_1027999.log | 209.000 | 819000..1027999 |
| p23_1028000_1030000.log | 2.001 | 1028000..1030000 |
| p23_1030001_1050000.log | 20.000 | 1030001..1050000 |
| p23_1050001_1100000.log | 50.000 | 1050001..1100000 |
| p23_1100001_1300000.log | 200.000 | 1100001..1300000 |
| p23_1300001_1700000.log | 400.000 | 1300001..1700000 |
| p23_1700001_2200000.log | 500.000 | 1700001..2200000 |
| p23_2200001_2800000.log | 600.000 | 2200001..2800000 |
| p23_2800001_3300000.log | 500.000 | 2800001..3300000 |
| p23_3300001_3840000.log | 540.000 | 3300001..3840000 |

Total = **3.149.013 baris** â€” jumlah eksak which diharapkan pra-registrasi
(baris kanonik + semua baris tersegel cocok).

## 5. Bukti & hash

- `REPLAY_METADATA.txt` (verbatim in log): `purpose=complete finite
  Triangle replay`; `started_utc`/`finished_utc` seperti Â§3;
  `repository_commit=2e9976c4â€¦`; `repository_dirty=false`;
  `producer_sha256=580d0b51165da58d4ca22e16d80a8c3db603dd0d9246f26dd027b5f820bf0808`;
  `review_container_inputs_sha256=1dbed4db14784e2764190039aa5fca014f25fd6a9d63e9b7f3730a935942159d`;
  image `6e29bc53â€¦` / `.Id 5ccd9e3fâ€¦`; platform `linux/amd64`; gcc
  `13.3.0-6ubuntu2~24.04.1`; libflint `3.0.1-3.1build1`; libgmp
  `2:6.3.0+dfsg-2ubuntu6.1`; libmpfr `4.2.1-1build1.1`.
- `REPLAY_SHA256SUMS` (16 entri: 15 log lane + REPLAY_METADATA): sha256
  semua keluaran tercatat in-run; sha256 file sums itu sendiri
  `e035dfd1af259ca6504e3897cbc4fa9b4e6c3cd2bb44a74d5a84ef7289fceb19`;
  inventaris `find â€¦ -exec sha256sum` (17 file) dicatat in log.
- Backup in luar repo:
  `C:\Users\usER\AppData\Local\Temp\opencode\l1_sweep_2026-10-18.tar.gz`
  (24.581.749 B; sha256
  `11bad9123b8f0db2b4ed4ac2a3e4f42aeda7197ee91c78f30ec39f12a3c75509`);
  isi diekstrak ulang and diverifikasi vs `REPLAY_SHA256SUMS` â†’
  **16/16 OK**.

## 6. Yang TIDAK ditetapkan (limit)

- Label maksimum tetap replay-level: **"release replayed; numbers
  reproduced from the release's own tooling"** (pra-reg Â§3.5). Producer,
  lane, and komparator semuanya milik rilis; ini **bukan** verifikasi
  independen and no boleh dikutip lebih tinggi.
- Tidak ada klaim matematis universal; no menyatakan or menyangkal
  RH / Pâ‰ NP.
- Cakupan = rentang N=690988..3840000 sesuai pra-registrasi; in luar itu
  tetap NOT COVERED.

## 7. Artefak & jangkar

- Log transkrip penuh: `reports/audit_p1_l1_sweep_2026-10-18.log`.
- Runner + watchdog: `audit_p1/l1_sweep.sh`,
  `audit_p1/l1_sweep_watchdog.sh` (pra-registrasi `295e716`).
- Registry: `A-2026-0001` â€” note sweep baru + 4 baris sertifikat (log
  sweep, report ini, runner, watchdog).
- Urutan commit: `295e716` (pra-registrasi, sebelum perintah pertama) â†’
  commit which membawa report ini.


