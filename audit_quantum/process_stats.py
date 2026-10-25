import pathlib, hashlib, json
root = pathlib.Path('D:/Opencode AI Agent/audit_quantum/exec_2026-10-19')
stats = {}
for p in sorted(root.glob('*.bin')):
    data = p.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    stats[p.name] = {'sha256': sha, 'size': len(data)}
md_path = pathlib.Path('D:/Opencode AI Agent/reports/audit_quantum_2026-10-19.md')
with md_path.open('w', encoding='utf-8') as f:
    f.write('# Quantum audit 2026‑10‑19\n\n')
    f.write('## Binary stats summary\n\n')
    f.write('| File | Size (bytes) | SHA‑256 |\n')
    f.write('|------|--------------|---------|\n')
    for name,info in stats.items():
        f.write(f'| {name} | {info["size"]} | {info["sha256"]} |\n')
    f.write('\n')
    f.write('**Receipt**\n\n')
    receipt = {'name':'Quantum audit 2026‑10‑19','files':stats}
    f.write('```json\n')
    f.write(json.dumps(receipt, indent=2))
    f.write('\n```\n')
print('markdown written')
