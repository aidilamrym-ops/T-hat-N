# GW — Resolusi ke-4 (dim 501): OUTCOME non-PD di ladder — statistik titik berakhir

Tanggal: 2026-10-17 (waktu lokal mesin). Status: **SELESAI — OUTCOME.**
Pra-registrasi: `reports/RESOLUTION4_DIM501_PREREG_2026-10-17.md`
(commit `ea2ed77`, dipush + CI hijau `39020789629` SEBELUM launch;
launcher start 17:24:00; ordering PASS).

Ringkas: Stage L dijalankan; ladder Route S 6000 bit (c=100, N=250 →
dim 501) mencetak `UNDETERMINED at pivot 446` — **bukan** CERTIFIED
POSITIVE DEFINITE. Pra-registrasi §4 (verbatim): "A G-M0 FAIL or a
non-PD ladder is NOT an infrastructure failure: it is the outcome,
reported as-is, and it ends the statistics of this point." Maka titik
keempat BERAKHIR di ladder: Stage C dan Stage M tidak dijalankan; tidak
ada angka S1/S2 untuk dim 501; tidak ada blok GW-DELTA keempat. Tidak
ada parameter yang diubah dan **tidak ada rerun** — aturan rerun §4
hanya untuk kegagalan infrastruktur terenumerasi, dan tidak satu pun
dari ketiganya terjadi (§3).

## 1. Angka (diekstrak mesin; verbatim)

Dari `reports/gw_route_s_ladder_c100_n250.log` (baris tabel hasil,
ringkasan, dan baris penutup; baris pemisah `----` 92 karakter tidak
dikutip di sini tetapi utuh di log):

```text
250  501   6000     446    0      True      1612.96  177.07   UNDETERMINED at pivot 446
1 run(s); 0 certified, 1 not certified
written: D:\Opencode AI Agent\reports\gw_route_s_ladder_c100_n250.json
```

Field JSON (`reports/gw_route_s_ladder_c100_n250.json`): `n_pos = 446`;
`n_neg = 0`; `undetermined_pivot = 446`; `pivots_recorded = 446`;
`entries_finite = true`; `verdict = "UNDETERMINED at pivot 446"`;
`build_s = 1612.96`; `ldlt_s = 177.07`; `total_s = 1790.13`.

Baca tool (`msaf/gw_route_s_ladder.py`, sha256 raw=lf
`cc09ed5a35ac90b581cf2ef5660f3db903704843909b8a80b7fb21bf036a5b20`,
tidak diubah): verdict `UNDETERMINED` = pivot tak-terputuskan pertama
dilaporkan di indeks 446; tidak ada pivot negatif yang ditemukan. Ini
pernyataan tentang SERTIFIKAT tanda interval pada satu matriks finit
pada presisi 6000 bit — bukan tentang spektrum sebenarnya, bukan tren.

## 2. Timeline (verbatim, utuh 5 baris, dari `reports/res4_dim501_launch_2026-10-17.log`; file berawalan BOM UTF-8)

```text
[2026-10-17T17:24:00] orchestrator start; sequential stages L -> C -> M (one heavy stage at a time); prereg commit ea2ed77 pushed; env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8; GW_DIR default C:/Users/usER/oracle-toe/GUINAND_WEIL
[2026-10-17T17:24:00] HEAD check OK: ea2ed77fe8886c56cebd9c4c667a8df09d422ae0 (res4-dim501: pre-register the fourth resolution point (dim 501) + series runner)
[2026-10-17T17:24:00] stage L launched: python msaf\gw_route_s_ladder.py --c 100 --ladder 250 --prec 6000 --out reports\gw_route_s_ladder_c100_n250.json; stdout->reports\gw_route_s_ladder_c100_n250.log; stderr->reports\gw_route_s_ladder_c100_n250.err.log
[2026-10-17T17:53:51] stage L finished exit= elapsed=1791s
[2026-10-17T17:53:51] ABORT: stage L nonzero exit -> infrastructure failure per prereg section 4; stopping for review (identical rerun allowed only after the issue is fixed and logged).
```

## 3. Klasifikasi (hasil review; bagian ini yang mengikat)

Review dilakukan setelah stop (2026-10-17). Temuan, berurutan:

1. **Komputasi Stage L tidak gagal.** Proses selesai normal: log lengkap
   (termasuk baris `written:`), JSON lengkap dan konsisten
   (`total_s = 1790.13` ≈ elapsed launcher 1791 s), `err.log` 0 byte.
   Tool `gw_route_s_ladder.py` juga **selalu exit 0** — semua outcome
   (UNDETERMINED / NOT PD / ERROR per baris) tercatat di JSON, bukan di
   exit code (dibaca dari sumber: `sys.exit(main())`; `main()` selalu
   `return 0`).
2. **`exit=` kosong di log launcher adalah cacat penangkapan wrapper,
   bukan bukti exit nonzero.** Root cause direproduksi di mesin ini
   (PowerShell 5.1.19041.6456): `Start-Process -PassThru` +
   `-RedirectStandardOutput/-RedirectStandardError` + `.WaitForExit()`
   → `$p.ExitCode` = null (kosong) meskipun `HasExited` = True;
   `-WindowStyle Hidden` bukan penyebabnya. Dengan flag `-Wait`, atau
   `cmd /c` + `$LASTEXITCODE`, exit code tertangkap benar. Probe
   `ps_exitprobe.py` (exit 7 dan exit 0): launcher-style → `ExitCode=[]`;
   `-Wait` → `ExitCode=[7]`; `cmd /c` → `$LASTEXITCODE=7`.
3. **Konsekuensi: launcher salah-branch.** Karena `$rcL` kosong,
   launcher menempuh cabang "nonzero exit → infrastructure failure"
   (baris 35–38 skrip, `exit 2`) alih-alih gerbang verdict. Alur yang
   benar, sesuai skrip baris 39–44, adalah: baris log
   `stage L verdict (N=250, dim 501): UNDETERMINED at pivot 446` lalu
   (verbatim baris 43): "STOP: non-PD / undetermined ladder is an
   OUTCOME, not infrastructure; per prereg section 4 the statistics of
   this point end here; stage C NOT launched." **End-state identik**
   (Stage C/M tidak jalan), tetapi label di log salah. Log launcher
   TIDAK diedit (arsip); klasifikasi resmi adalah bagian ini.

**Klasifikasi final:** ini cabang **OUTCOME** per pra-registrasi §4
(non-PD ladder), bukan infrastruktur: (a) exit sebenarnya 0 (butir 1–2,
err.log kosong); (b) artefak lengkap; (c) kriteria "missing 36
captures" N/A karena Stage M memang tidak dijalankan oleh outcome.
Aturan rerun §4 karena itu TIDAK berlaku: **tidak ada rerun**, tidak
ada perubahan parameter. Tidak ada angka dari "percobaan gagal" yang
dipakai — karena tidak ada percobaan yang gagal; yang dilaporkan adalah
output komputasi yang selesai (verdict + counts). Perbaikan untuk
orkestrasi masa depan (dokumentasi, bukan tindakan di titik ini):
tangkap exit code dengan `-Wait` atau `cmd`+`$LASTEXITCODE`. Skrip
launcher (temp, tidak dikomit): sha256
`bec67db055d64fdaf76f35798f047b8663f448f5eec81c1ec50761d60a491d30`.

## 4. Yang TIDAK ada (karena outcome)

Stage C dan Stage M tidak dijalankan. Artefak yang tidak dibuat:
`reports/gw_capture_100_250.log`, `reports/gw_spectrum_100_250.json`,
`reports/mont_run_100_250.txt`, `reports/res4_dim501_m_stdout.log`,
`reports/res4_dim501_m_stderr.log`. Tidak ada angka S1/S2 untuk dim
501; tidak ada pembahasan tren (tidak ada yang bisa dibahas).

## 5. Artefak + hash + segel (semua dihitung di mesin ini)

| File | Byte | sha256 (raw) | sha256 (lf) |
|---|---|---|---|
| `reports/gw_route_s_ladder_c100_n250.json` | 343 | `319e50d7d54e61330e50d6a922297ca8cb6c662771c37f96b2ce82e504cb5772` | `3d2104901af41e48397f03108f1d98a788f25c3eecac3bf98ee6cb74a9506153` |
| `reports/gw_route_s_ladder_c100_n250.log` | 921 | `c6e4851010e48e510ecd208df0083929f8f551d5541b7df0d3e43dfcba548ee2` | `3d89637784b2cd82827a06edfd7c544fd62ee56a47e1e25ddf0786e8cf42a001` |
| `reports/gw_route_s_ladder_c100_n250.err.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (kosong) | sama |
| `reports/res4_dim501_launch_2026-10-17.log` | 921 | `d4225ac05181ef055886c840273567be7ca0915b07844da0713a572d780cd846` | `48074b5d8b54b831d4721a5cf8002e945fbf58d4302ca68b6d4fad0234771e67` |

Rumus: raw = byte apa adanya; lf = `\r\n` → `\n` lalu sha256.

**Cek ulang segel pra-registrasi §5 (raw byte, PASS semua):**

| File tersegel | sha256 raw (= nilai pra-registrasi) |
|---|---|
| `reports/gw_spectrum_100_100.json` | `c645c590e54717cf793a31ecd941640adbbca162caf15108f56dde1da993f75d` |
| `reports/gw_spectrum_100_150.json` | `8fded8394f0ab4e8ed83f537609d313d0d50eef42f09214c30d1cfcd994d161d` |
| `reports/gw_route_s_ladder_c100.json` | `674a50d3057aa19ce51e28841bef6dcde93fff91ec3adbb945611a9059574558` |
| `reports/gw_capture_100_100.log` | `0908b3dfc124431ca553ee516f12c9a05eeaa262d3c2e2a980ac48ee7f69f6dd` |
| `reports/gw_capture_100_150.log` | `f2e2ffa2cbcc2554139743481ab7cf52351d0124f6577a35a45b1345528a1e26` |
| `reports/mont_run_100_100.txt` | `811a9dcc055acc1d649ebce1d8fec45b56c4fc26b81060de2f90746e058dfe4d` |
| `reports/mont_run_100_150.txt` | `faecc52318b729be13c624b589e9d1ed4a332f5da8b2af316957b67f0bf7f017` |
| `msaf/mont_run.txt` | `eb072757c3b1b18e502ab25dc1bff329d115b7d6c2c74baec89e279340b54b10` |

Item sha256_lf pra-registrasi §5 (PASS): `reports/gw_h1_floor_refine.json`
`4777d94f9ec533712b14cc097b9240e5c961790b3d9025f452b7c21aade6148f`,
`reports/AMENDMENT_FLOOR_SPEC.md`
`3c9958bee3021385b242b84b2ecda136e15f35d5682c16ff690713830efbb917`,
`msaf/gw_h1_floor_refine.py`
`c70a76973e8e4e756642f310af4f7a721c6bbde485c7d8dcb5ab20961e4a5cf2`.
Dashboard v3/v4/v5 dan blok mesin README §7 tidak disentuh oleh run ini
(tidak ada penulisan ke file apa pun di luar daftar New files §5);
segelnya hidup di dokumen masing-masing.

Verifikasi kutipan: setiap string angka/hash di laporan ini dicek mesin
terhadap artefaknya (skrip verifikasi sesi; semua PASS).

## 6. Publikasi (append-only)

- Laporan ini (kewajiban pra-registrasi §5).
- `reports/HANDOFF.md`: paragraf update di kepala, baris tabel §1 baru,
  §2.0e baru; "seri keempat tersisa" dihapus (statistik berakhir).
- `README.md` §6.7 item 2: outcome wider-N dicatat.
- `reports/THREE_TASKS_2026-10-15.md`: blok BARU (notice outcome, bukan
  blok terukur) ditambahkan di akhir; GW-DELTA dan GW-DELTA-3
  byte-identik (tidak disentuh; syarat pra-registrasi §5).
- Artefak dikomit pada commit publikasi yang membawa file ini.

## 7. Batas (beku)

Outcome dari satu matriks finit pada satu presisi (6000 bit). Bukan
teorema Montgomery, bukan bukti RH, bukan Weil-positivity, bukan
pernyataan tentang spektrum sebenarnya, bukan prime counting, bukan
faktorisasi, bukan tren. Yang bisa dikatakan: ladder 6000 bit untuk dim
501 TIDAK memberikan sertifikat PD; titik keempat seri tidak
menghasilkan statistik.

Ditulis oleh sesi analisis, 2026-10-17.
