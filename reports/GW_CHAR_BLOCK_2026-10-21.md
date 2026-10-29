from pathlib import Path

path = Path(r"D:\Opencode AI Agent\reports\GW_CHAR_BLOCK_2026-10-21.md")
text = path.read_text(encoding="utf-8")

# Update status line
text = text.replace(
    "**Status:** eksekusi `PASS`, **sertifikasi `INCONCLUSIVE` / `NOT READY`**.",
    "**Status:** eksekusi `PASS`, **sertifikasi `INCONCLUSIVE` / `NOT READY`** (blok pole principal already diimplementasikan; validasi independen belum)."
)

# Update the two missing items
text = text.replace(
    "1. no ada validasi independen for pergeseran paritas `alpha = 3/4`\n"
    "   maupun konstanta konduktor `log q*`;\n"
    "2. blok pole for karakter **principal** belum diturunkan maupun diuji.",
    "1. no ada validasi independen for pergeseran paritas `alpha = 3/4`\n"
    "   maupun konstanta konduktor `log q*`;\n"
    "2. blok pole for karakter **principal** already diturunkan and diuji "
    "(residu Ï†(q)/q, blok W02 diskalakan)."
)

# Update the closing items
text = text.replace(
    "2. derivasi blok pole principal (source `psi_0` diskalakan residu\n"
    "   `phi(q)/q`) beserta uji fungsinya;",
    "2. validasi independen blok paritas/konduktor (mis. pencocokan\n"
    "   explicit formula terhadap jumlah nol numerik)."
)

# Update the "Langkah penutup C" section
text = text.replace(
    "1. validasi independen blok `alpha=3/4` and `log q*`, misalnya pencocokan\n"
    "   explicit formula on test vector terhadap jumlah nol `L(s,chi)` which\n"
    "   dihitung numerik, or implementasi kedua which independen;\n"
    "2. derivasi blok pole principal (source `psi_0` diskalakan residu\n"
    "   `phi(q)/q`) beserta uji fungsinya;\n"
    "3. baru setelah keduanya tertutup, tulis registry and boleh naik ke\n"
    "   `PASS`.",
    "1. validasi independen blok `alpha=3/4` and `log q*`, misalnya pencocokan\n"
    "   explicit formula on test vector terhadap jumlah nol `L(s,chi)` which\n"
    "   dihitung numerik, or implementasi kedua which independen.\n"
    "2. Blok pole principal already diimplementasikan (source `psi_0` diskalakan\n"
    "   residu `phi(q)/q`, blok W02 diskalakan)."
)

# Update the receipt sha256
import hashlib, pathlib as pl
receipt_hash = hashlib.sha256(pl.Path(r"D:\Opencode AI Agent\reports\gw_char_block_2026-10-21.json").read_bytes().replace(b'\r\n',b'\n')).hexdigest()
text = text.replace(
    "receipt sha256: faa06b697afa3dad812d9d12f17327521465445922e2b0599facb1987b202312",
    f"receipt sha256: {receipt_hash}"
)

# Update the file hash
report_hash = hashlib.sha256(pl.Path(r"D:\Opencode AI Agent\reports\GW_CHAR_BLOCK_2026-10-21.md").read_bytes().replace(b'\r\n',b'\n')).hexdigest()
# We'll update after writing

path.write_text(text, encoding="utf-8", newline="")
print("Report updated")
print("New receipt hash:", receipt_hash)

