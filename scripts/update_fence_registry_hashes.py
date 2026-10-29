# scripts/update_fence_registry_hashes.py
import re, hashlib, os

REGISTRY = 'reports/FENCE_REGISTRY.md'

def sha256lf(path):
    # read file, normalize line endings to LF
    with open(path, 'rb') as f:
        data = f.read().replace(b'\r\n', b'\n')
    h = hashlib.sha256(data).hexdigest()
    return h

line_re = re.compile(r'(sha256LF)\s+([0-9a-fA-F]+)\s+(\S+)')

new_lines = []
with open(REGISTRY, 'r', encoding='utf-8') as f:
    for line in f:
        m = line_re.search(line)
        if m:
            prefix, oldhash, relpath = m.groups()
            # resolve path relative to repo root
            abspath = os.path.normpath(os.path.join(os.path.dirname(REGISTRY), '..', relpath))
            if os.path.isfile(abspath):
                newhash = sha256lf(abspath)
                line = f"{prefix} {newhash} {relpath}\n"
        new_lines.append(line)

with open(REGISTRY, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('FENCE_REGISTRY.md updated')
