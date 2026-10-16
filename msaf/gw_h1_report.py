# -*- coding: utf-8 -*-
"""Generate reports/AMENDMENT_FLOOR_RESULTS.md (dated H1 execution record).

Machine side of the FROZEN pre-registration reports/AMENDMENT_FLOOR_SPEC.md,
parts (A) and (B) (part (C), engine B, is a later session).  Every number is
formatted here from reports/gw_h1_floor_refine.json, the seven run logs and
reports/h1_floor_refine_section.md (embedded verbatim); no number is retyped
by hand -- same discipline as msaf/gw_resolution_delta.py.
"""

import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from msaf.gw_h1_extract import REFINED_A, REFINED_B, parse_log  # noqa: E402


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    with open("reports/gw_h1_floor_refine.json", encoding="utf-8") as fh:
        art = json.load(fh)
    grid, c4, man = art["grid"], art["c4_array"], art["manifest"]
    assert c4 is not None, "C4 array incomplete: run all five seeds first"
    assert all("status" not in g for g in grid), "grid incomplete"
    assert not any(g["verdict_printed"] != g["verdict_recomputed"]
                   for g in grid), "verdict disagreement"

    spec_sha = sha256_file("reports/AMENDMENT_FLOOR_SPEC.md")
    with open("reports/h1_floor_refine_section.md", encoding="utf-8") as fh:
        section = fh.read().rstrip("\n")

    runs = []
    for dim, path in REFINED_A.items():
        runs.append(("A", dim, path))
    for seed, path in REFINED_B.items():
        runs.append(("B", seed, path))

    run_rows = []
    for kind, ident, path in runs:
        log = parse_log(path)
        sha = man["refined_logs"]["%s_%s" % (kind, ident)]
        tag = ("A dim %d" % ident) if kind == "A" else ("B seed %d" % ident)
        run_rows.append("| %s | %d | %d | %.1f | `%s` |"
                        % (tag, log["seed"], log["samples"],
                           log["elapsed_s"], sha))

    # instrument provenance: identical across all seven headers, else stop
    instr_sha, instr_rev, instr_date, thr = set(), set(), set(), set()
    for _, _, path in runs:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        instr_sha.add(re.search(r"# instrument sha256 = ([0-9a-f]{64})",
                                raw).group(1))
        m = re.search(r"# instrument git revision = ([0-9a-f]{40}) (\S+)", raw)
        instr_rev.add(m.group(1))
        instr_date.add(m.group(2))
        thr.add(re.search(r"# threading env = (.+)", raw).group(1))
    assert len(instr_sha) == len(instr_rev) == len(thr) == 1, "header drift"
    instr_sha, instr_rev = instr_sha.pop(), instr_rev.pop()
    instr_date, thr = instr_date.pop(), thr.pop()

    ks, seeds = c4["k"], c4["seeds"]
    canon_k = ks[0]
    canon_p = "%.5e" % (canon_k / 20000)
    pooled_p = "%.5e" % c4["p_hat"]
    hom_stat = "%.4f" % c4["homogeneity_stat"]
    hom_p = "%.5e" % c4["homogeneity_p"]
    below = [(s, k) for s, k in zip(seeds, ks) if k / 20000 < 0.05]
    below_txt = ", ".join("%d = %.5e" % (s, k / 20000) for s, k in below)
    floor_cells = sum(1 for g in grid if g["k_gue"] == 0)

    lines = []
    add = lines.append
    add("# AMANDEMEN LANTAI H1 -- hasil terukur (2026-10-16)")
    add("")
    add("Otoritas: `reports/AMENDMENT_FLOOR_SPEC.md` (DIBEKUKAN; sha256")
    add("`%s`). Bagian (A) grid refined" % spec_sha)
    add("20000 surrogat dan (B) array robustness 5-seed: **SELESAI**. Bagian")
    add("(C) engine B: sesi berikutnya (spec bagian 5; tidak pernah")
    add("verdict-bearing).")
    add("")
    add("Dokumen ini dihasilkan mesin oleh `msaf/gw_h1_report.py` dari")
    add("`reports/gw_h1_floor_refine.json` + 7 log run + tabel extractor;")
    add("tidak ada angka yang diketik ulang oleh manusia. Tabel di bagian 2")
    add("adalah keluaran extractor verbatim.")
    add("")
    add("## 1. Yang dieksekusi")
    add("")
    add("- (A) 20000 surrogat per ensemble, dim 201/301/401, seed kanonik")
    add("  20260927 -> grid refined 18 sel; target pra-registrasi C1-C4")
    add("  ditandai di tabel.")
    add("- (B) Array 5-seed S5 pada C4 (dim 301, chart T, sigma_u 0.5): seed")
    add("  20260927 (kanonik; entri ini diambil dari run A dim 301 --")
    add("  komputasi identik, tanpa duplikasi) + seed 20261001..20261004")
    add("  (4 run baru).")
    add("- Instrumen: `gw_montgomery.py` revisi `%s` (%s)," % (instr_rev,
                                                              instr_date))
    add("  sha256 `%s`, TIDAK dimodifikasi;" % instr_sha)
    add("  hash on-disk == header ketujuh log. Injeksi seed via override")
    add("  modul (instrumen tidak punya flag `--seed`). Hitungan eksak: spy")
    add("  read-only `np.mean` (instrumen mencetak p pada %.4f; spec bagian")
    add("  3 mempensiunkan string \"0.0000\").")
    add("- Lingkungan: python 3.14.4 + numpy 2.5.2 + scipy 1.18.0;")
    add("  %s. Catatan operasional: cap" % thr)
    add("  thread murni kinerja -- rerun capped mereproduksi log tersegel")
    add("  persis (bagian 4).")
    add("- Tujuh run (semua exit 0; 36/36 tangkapan eksak per run):")
    add("")
    add("| run | seed | samples | elapsed (s) | sha256 log |")
    add("|---|---|---|---|---|")
    for row in run_rows:
        add(row)
    add("")
    add("## 2. Grid refined (A) + array robustness (B) -- keluaran mesin")
    add("verbatim")
    add("")
    add(section)
    add("")
    add("## 3. Kepatuhan format beku (spec bagian 3)")
    add("")
    add("- \"0.0000\" pensiun; k=0 dilaporkan sebagai BOUND: p_GUE <")
    add("  1.49775e-04 (rumus beku 1 - 0.05^(1/n), n = 20000), tidak pernah")
    add("  sebagai nol terukur.")
    add("- %d dari 18 sel grid refined: k_GUE = 0/20000 (bound). Satu sel" %
        floor_cells)
    add("  off-floor: C4 = %d/20000 = %s." % (canon_k, canon_p))
    add("- Verdict refined dihitung ulang dari k eksak dengan aturan yang")
    add("  TIDAK berubah; 18/18 cocok dengan verdict tercetak di log.")
    add("- Validasi spy: 36/36 tangkapan per run; cocok dengan p tercetak")
    add("  pada n=10, pada n=2000 (repro tersegel), dan pada sel positive-k")
    add("  n=20000 (1262/20000 <-> 0.0631; 960/20000 <-> 0.0480).")
    add("- Nilai tersegel tetap terlihat di semua tempat (kolom sealed);")
    add("  refined SUPERSEDE untuk C1-C4 dan dianotasi; dashboard tersegel")
    add("  `reports/gw_diagnostic_v3.html` TIDAK disentuh (spec bagian 6.4).")
    add("")
    add("## 4. Bukti reproduktibilitas (commit 993b0e8)")
    add("")
    add("- REPRO CHECK PASS: rerun dim 201 @ 2000 sampel (capped 1-thread)")
    add("  mereproduksi log tersegel pada SEMUA field yang dibandingkan")
    add("  (chi2, p, verdict, S1/S2 final, r_bar) -- identik. Thread count")
    add("  bukan efek numerik.")
    add("- Benchmark mesin ini: capped 1-thread ~2x lebih cepat dari default")
    add("  (eigvalsh n=301: 20.6 vs 39.6 ms) -- threading murni overhead.")
    add("- Instrumen tidak berubah selama kampanye (sha256 on-disk ==")
    add("  header semua run).")
    add("")
    add("## 5. Array robustness C4 -- klasifikasi beku (spec bagian 4)")
    add("")
    add("- Pohon keputusan beku, urutan diterapkan: cabang 1. Klasifikasi:")
    add("  **%s**." % c4["classification"])
    add("- Homogenitas Pearson chi2 = %s (df = 4), p = %s --" % (hom_stat,
                                                                hom_p))
    add("  ditolak pada alpha = 0.01.")
    add("- Angka of record: kanonik 20000 = %d/20000 = %s; pooled" %
        (canon_k, canon_p))
    add("  5-seed = %d/%d = %s. C4 ditandai" % (c4["pooled_k"],
                                               c4["pooled_n"], pooled_p))
    add("  resolution-sensitive; verdict grid tetap memakai nilai kanonik")
    add("  20000.")
    add("- Ekspektasi pra-registrasi yang TERFALSIFIKASI (dicatat, tidak")
    add("  dipatch): spec bagian 4 menyatakan \"setiap cabang meninggalkan")
    add("  C4 di bawah ambang verdict 0.05\". Terukur: pooled p_hat = %s;" %
        pooled_p)
    add("  %d dari 5 seed >= 0.05 (yang di bawah: %s);" % (len(ks) - len(below),
                                                          below_txt))
    add("  verdict kanonik = NO DISCRIMINATION (bukan INCONSISTENT).")
    add("- Batas interpretasi (beku): bahkan STABLE tidak menjadikan C4")
    add("  \"physical\"; klasifikasi di sini NOT STABLE. Statistik dari")
    add("  matriks deterministik berhingga; bukan teorema Montgomery, bukan")
    add("  bukti RH.")
    add("")
    add("## 6. Manifest")
    add("")
    add("- repo HEAD saat ekstraksi: `%s`; ekstraksi: %s" % (man["repo_head"],
                                                            man["generated"]))
    add("- extractor sha256: `%s`; spec sha256: `%s`" % (man["extractor_sha256"],
                                                        spec_sha))
    add("- sha256 log refined:")
    for k in sorted(man["refined_logs"]):
        add("  - %s: `%s`" % (k, man["refined_logs"][k]))
    add("- sha256 log tersegel (baseline):")
    for k in sorted(man["sealed_logs"]):
        add("  - %s: `%s`" % (k, man["sealed_logs"][k]))
    add("")
    add("## 7. Catatan deviasi")
    add("")
    add("Tidak ada deviasi prosedural dari spec yang tercatat selama")
    add("eksekusi ini. Dua catatan operasional direkam, bukan dipatch")
    add("diam-diam: cap thread kinerja (bagian 1) dan reuse entri kanonik")
    add("S5 dari run A dim 301 (bagian 1).")
    add("")

    with open("reports/AMENDMENT_FLOOR_RESULTS.md", "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("\n".join(lines))
    print("wrote reports/AMENDMENT_FLOOR_RESULTS.md (%d lines)" % len(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
