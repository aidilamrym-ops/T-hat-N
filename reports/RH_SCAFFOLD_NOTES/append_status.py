import pathlib
import json

base = pathlib.Path('D:/Opencode AI Agent/reports/RH_SCAFFOLD_NOTES')
files = {
    'Stage_2_Derivation_Analytic_Tail_Bound.md': ('Stage 2', 'Stage_2_Derivation_Analytic_Tail_Bound_receipt.json'),
    'Stage_3_Eigenvalue_Locking_Dimension_Induction.md': ('Stage 3', 'Stage_3_Eigenvalue_Locking_Dimension_Induction_receipt.json'),
    'Stage_4_Containment_Proof.md': ('Stage 4', 'Stage_4_Containment_Proof_receipt.json'),
}
for md_name, (label, receipt_name) in files.items():
    path = base / md_name
    text = path.read_text(encoding='utf-8')
    if '## STATUS' in text:
        continue
    receipt = json.loads((base / receipt_name).read_text(encoding='utf-8'))
    text += '\n\n## STATUS\n\n'
    text += f'- **{label}** completed.\n'
    text += f'- Lean file: `{pathlib.Path(receipt["path"]).name}`\n'
    text += f'- SHA-256: `{receipt["sha256"]}`\n'
    text += '\n---\n'
    path.write_text(text, encoding='utf-8')
    print('updated', md_name)
