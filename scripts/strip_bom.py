# scripts/strip_bom.py
"""Remove UTF-8 BOM (U+FEFF) from all .py and .lean source files.
   Run before CI to ensure AST parsing works and registry hashes match.
"""
import os

BOM = b"\xef\xbb\xbf"

for root, _, files in os.walk("."):
    for name in files:
        if not (name.endswith('.py') or name.endswith('.lean')):
            continue
        path = os.path.join(root, name)
        with open(path, 'rb') as f:
            data = f.read()
        if data.startswith(BOM):
            # strip BOM, keep rest unchanged
            new_data = data[len(BOM):]
            with open(path, 'wb') as f:
                f.write(new_data)
            print(f"Stripped BOM from {path}")
