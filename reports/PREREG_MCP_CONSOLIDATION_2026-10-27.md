# Pra-Registrasi — Konsolidasi MCP T2N ke `t2n_core` + `t2n_viz` — 2026-10-27

**Status:** PREREG. Dokumen ini dikunci sebelum kode ditulis. Amendemen harus
bertanggal dan tidak menulis ulang kontrak yang sudah disetujui.

**Ruang lingkup:** `mcp/t2n_illumina` (perbaikan), `mcp/t2n_core.py` (baru),
`mcp/t2n_viz.py` (baru), `opencode.jsonc` workspace, dan test handshake.
Tidak menyentuh `shp_asymmetric_wager`, `shp_bridge`, `msaf/*` selain test
baru, `reports/FENCE_REGISTRY.md` entri lama, atau artefak ber-`sha256LF`.

## 1. Masalah yang dikunci

1. `mcp/t2n/illumina.py` gagal diimpor: `NameError: name
   'render_html_dashboard' is not defined`. Definisi fungsi hilang; badannya
   tertinggal di dalam `render_materials_dashboard` setelah `return`.
2. `mcp/t2n_combined.py` hanya menggabungkan `illumina` + `materials`, bukan
   lima role server (`repokeeper`, `archivist`, `science`, `scribe`,
   `watchtower`).
3. Workspace `opencode.jsonc` mendaftarkan 6 server t2n terpisah; daemon
   `opencode serve` menumpuk 2 batch t2n + 3 batch shp (16 proses) karena sesi
   lama tidak dibersihkan.

## 2. Keputusan pemilik 2026-10-27

- Arsitektur final: **`t2n_core` + `t2n_viz`**. Dua server shp tidak disentuh,
  sehingga total 4 server aktif.
- Proses: hanya batch t2n 02:01:48 yang dimatikan; batch aktif dibiarkan.

## 3. Kontrak terukur (acceptance criteria)

Semua kriteria diuji oleh `msaf/tests/test_mcp_servers.py` yang menjalankan
server sebagai subprocess lewat stdio (newline-delimited JSON-RPC), bukan
dengan mengimpor modul secara langsung.

| # | Kriteria | Ambang |
|---|---|---|
| K1 | `t2n_core` menjawab `initialize` | `serverInfo.name == "t2n_core"`, protokol di `SUPPORTED_PROTOCOLS` |
| K2 | `t2n_core` `tools/list` | tepat **30** tool: 6 repokeeper + 6 archivist + 3 science + 8 scribe + 5 watchtower + `ping` + `self_check` |
| K3 | `t2n_core` tanpa duplikat nama tool | `len(names) == len(set(names))` |
| K4 | `t2n_viz` `tools/list` | tepat **7** tool: 3 SVG + `render_html_dashboard` + `mp_query` + `ping` + `self_check` |
| K5 | `render_html_dashboard` berjalan | menulis satu file `.html` di bawah `T2N_WRITE_ROOTS/illumina/`; isi memuat `<title>` dan header seksi |
| K6 | `ping` kedua server | `isError` false dan payload memuat `"status": "ok"` |
| K7 | `opencode.jsonc` | tepat 2 entri `mcp.servers` t2n: `t2n_core`, `t2n_viz` |
| K8 | Guard repo | `test_fence_registry` + `test_authority_manifest` lulus setelah dokumen diperbarui |

Kegagalan salah satu kriteria = pekerjaan belum selesai; jangan menyebut
"green" atau "verified".

## 4. Batas dan non-klaim

- Perbaikan ini **infrastruktur**, bukan hasil ilmiah. Tidak ada klaim baru
  tentang RH, abc, BSD, figure-eight, Lean, Coq, atau fisika.
- `render_materials_dashboard` tidak diekspos sebagai tool; ia boleh tetap ada
  sebagai fungsi internal tetapi tidak boleh menjadi jalur wajib.
- Tidak ada tool baru, tidak ada perubahan skema input tool yang sudah ada.
- `materials.mp_query` tetap memerlukan jaringan bila dipanggil; test tidak
  memanggilnya.
- `mcp/t2n_combined.py` dipertahankan sebagai shim kompatibilitas, bukan
  server yang didaftarkan.
- Proses shp tidak dimatikan, tidak diubah, dan tidak dikonfigurasi ulang.

## 5. Artefak yang akan dihasilkan

1. `mcp/t2n/illumina.py` — definisi `render_html_dashboard` dipulihkan.
2. `mcp/t2n_core.py` — gabungan lima role server.
3. `mcp/t2n_viz.py` — gabungan illumina + materials.
4. `mcp/t2n_combined.py` — shim ke `t2n_viz`.
5. `msaf/tests/test_mcp_servers.py` — guard K1–K6.
6. `opencode.jsonc` — dua entri t2n (K7).
7. `reports/DECISION_LOG.md`, `brain.md` §10.3, `reports/AUTHORITY_MANIFEST.json`.

## 6. Verifikasi

```text
python -m pytest msaf/tests/test_mcp_servers.py -q
python -m pytest msaf/tests/test_fence_registry.py msaf/tests/test_authority_manifest.py -q
```

## 7. Non-goals

- Tidak menyatukan `shp_*` ke dalam `t2n_*`.
- Tidak menghapus `mcp/t2n/*.py`; modul sumber tetap sebagai rujukan.
- Tidak menyentuh `mcp/out/` yang sudah ada.
- Tidak mengubah `T2N_WRITE_ROOTS` default di luar `mcp/out`.
