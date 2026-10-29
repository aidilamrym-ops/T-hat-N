# Pra-Registrasi â€” Konsolidasi MCP T2N ke `t2n_core` + `t2n_viz` â€” 2026-10-27

**Status:** PREREG. Dokumen ini dikunci sebelum kode ditulis. Amendemen harus
bertanggal and no menulis ulang kontrak which already disetujui.

**Ruang lingkup:** `mcp/t2n_illumina` (perbaikan), `mcp/t2n_core.py` (baru),
`mcp/t2n_viz.py` (baru), `opencode.jsonc` workspace, and test handshake.
Tidak menyentuh `shp_asymmetric_wager`, `shp_bridge`, `msaf/*` selain test
baru, `reports/FENCE_REGISTRY.md` entri lama, or artefak ber-`sha256LF`.

## 1. Masalah which dikunci

1. `mcp/t2n/illumina.py` gagal diimpor: `NameError: name
   'render_html_dashboard' is not defined`. Definisi fungsi hilang; badannya
   tertinggal in dalam `render_materials_dashboard` setelah `return`.
2. `mcp/t2n_combined.py` hanya menggabungkan `illumina` + `materials`, bukan
   lima role server (`repokeeper`, `archivist`, `science`, `scribe`,
   `watchtower`).
3. Workspace `opencode.jsonc` mendaftarkan 6 server t2n terpisah; daemon
   `opencode serve` menumpuk 2 batch t2n + 3 batch shp (16 proses) karena sesi
   lama no dibersihkan.

## 2. Keputusan pemilik 2026-10-27

- Arsitektur final: **`t2n_core` + `t2n_viz`**. Dua server shp no disentuh,
  sehingga total 4 server aktif.
- Proses: hanya batch t2n 02:01:48 which dimatikan; batch aktif dibiarkan.

## 3. Kontrak terukur (acceptance criteria)

Semua kriteria diuji oleh `msaf/tests/test_mcp_servers.py` which menjalankan
server sebagai subprocess lewat stdio (newline-delimited JSON-RPC), bukan
with mengimpor modul secara langsung.

| # | Kriteria | Ambang |
|---|---|---|
| K1 | `t2n_core` menjawab `initialize` | `serverInfo.name == "t2n_core"`, protokol in `SUPPORTED_PROTOCOLS` |
| K2 | `t2n_core` `tools/list` | tepat **30** tool: 6 repokeeper + 6 archivist + 3 science + 8 scribe + 5 watchtower + `ping` + `self_check` |
| K3 | `t2n_core` tanpa duplikat nama tool | `len(names) == len(set(names))` |
| K4 | `t2n_viz` `tools/list` | tepat **7** tool: 3 SVG + `render_html_dashboard` + `mp_query` + `ping` + `self_check` |
| K5 | `render_html_dashboard` berjalan | menulis satu file `.html` in bawah `T2N_WRITE_ROOTS/illumina/`; isi memuat `<title>` and header seksi |
| K6 | `ping` kedua server | `isError` false and payload memuat `"status": "ok"` |
| K7 | `opencode.jsonc` | tepat 2 entri `mcp.servers` t2n: `t2n_core`, `t2n_viz` |
| K8 | Guard repo | `test_fence_registry` + `test_authority_manifest` lulus setelah dokumen diperbarui |

Kegagalan salah satu kriteria = pekerjaan belum selesai; jangan menyebut
"green" or "verified".

## 4. Batas and non-klaim

- Perbaikan ini **infrastruktur**, bukan result ilmiah. Tidak ada klaim baru
  tentang RH, abc, BSD, figure-eight, Lean, Coq, or fisika.
- `render_materials_dashboard` no diekspos sebagai tool; ia boleh tetap ada
  sebagai fungsi internal tetapi no boleh menjadi jalur wajib.
- Tidak ada tool baru, no ada perubahan skema input tool which already ada.
- `materials.mp_query` tetap memerlukan jaringan bila dipanggil; test no
  memanggilnya.
- `mcp/t2n_combined.py` dipertahankan sebagai shim kompatibilitas, bukan
  server which didaftarkan.
- Proses shp no dimatikan, no diubah, and no dikonfigurasi ulang.

## 5. Artefak which akan dihasilkan

1. `mcp/t2n/illumina.py` â€” definisi `render_html_dashboard` dipulihkan.
2. `mcp/t2n_core.py` â€” gabungan lima role server.
3. `mcp/t2n_viz.py` â€” gabungan illumina + materials.
4. `mcp/t2n_combined.py` â€” shim ke `t2n_viz`.
5. `msaf/tests/test_mcp_servers.py` â€” guard K1â€“K6.
6. `opencode.jsonc` â€” dua entri t2n (K7).
7. `reports/DECISION_LOG.md`, `brain.md` Â§10.3, `reports/AUTHORITY_MANIFEST.json`.

## 6. Verifikasi

```text
python -m pytest msaf/tests/test_mcp_servers.py -q
python -m pytest msaf/tests/test_fence_registry.py msaf/tests/test_authority_manifest.py -q
```

## 7. Non-goals

- Tidak menyatukan `shp_*` ke dalam `t2n_*`.
- Tidak menghapus `mcp/t2n/*.py`; modul source tetap sebagai rujukan.
- Tidak menyentuh `mcp/out/` which already ada.
- Tidak mengubah `T2N_WRITE_ROOTS` default in luar `mcp/out`.


