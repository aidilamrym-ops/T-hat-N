import hashlib
import json
import pathlib

base = pathlib.Path('D:/Opencode AI Agent/reports/RH_SCAFFOLD_NOTES')
stages = [
    ('Stage_2_Derivation_Analytic_Tail_Bound.lean', 'Stage 2 Analytic Tail Bound'),
    ('Stage_3_Eigenvalue_Locking_Dimension_Induction.lean', 'Stage 3 Eigenvalue Locking'),
    ('Stage_4_Containment_Proof.lean', 'Stage 4 Containment Proof'),
]
for filename, label in stages:
    p = base / filename
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    receipt = {
        'name': label,
        'sha256': sha,
        'path': str(p.relative_to('D:/Opencode AI Agent')),
    }
    out = base / (filename.replace('.lean', '_receipt.json'))
    out.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(f'{filename}: {sha}')
