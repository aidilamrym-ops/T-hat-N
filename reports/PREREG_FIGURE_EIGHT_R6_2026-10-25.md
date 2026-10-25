# Pra-registrasi: Figure-eight T2-r6 — validasi orbit reduced 8x8 dengan K6 diskriminatif

**Status:** PRA-REGISTRASI, ditulis dan dikunci sebelum implementasi r6.
Trek baru, bukan revisi r5. Target orbit periodik figure-eight T0 eksak, gauge q1y=1/5, I_xy=0.

## Perbaikan dari r5:
1. Mutasi M3 (gauge): nilai C=1/3 harus memindahkan koordinat sehingga I_xy != 0 benar-benar terdeteksi (uji residual K1/K3 gagal).
2. Mutasi M8 (kondisi Gauss): batas GAUSS_COND_MAX diketatkan ke 20.000 (di bawah nilai riil ≈29.649) agar cond_ok=False terdeteksi secara diskriminatif.

## Parameter Terkunci:
- Base campaign: hasil K1-K5 dari figure_eight_r3 tetap diverifikasi.
- Matriks K6 M1-M10 diperbarui agar 100% diskriminatif.
- Registry target: A-2026-0047 (jika ALL PASS).
- Batas klaim: lokal dalam box B, eksistensi dan keunikan lokal; tidak ada klaim stabilitas, chaos, KAM, atau fisika.
