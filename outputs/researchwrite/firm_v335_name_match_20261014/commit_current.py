from pathlib import Path
import hashlib
import json
import os
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
TARGET = ROOT / '企业微观层面_v3.35.docx'
CANDIDATE = BASE / 'v335_candidate.docx'
EXPECTED = '39f6b40002448751512418e9ee807ea5e2cc2ee58e5f0f46c23022ffb5d65dae'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert sha(TARGET) == EXPECTED, 'Current document changed since preflight'
verification = json.loads((BASE / 'qa/verification_candidate.json').read_text(encoding='utf-8'))
assert verification['all_passed'] and verification['sha256'] == sha(CANDIDATE)
assert sha(BASE / 'sources/current_before.docx') == EXPECTED
fd, name = tempfile.mkstemp(prefix='.v335-edit-', suffix='.docx', dir=ROOT)
with os.fdopen(fd, 'wb') as out:
    out.write(CANDIDATE.read_bytes())
os.replace(name, TARGET)
assert sha(TARGET) == sha(CANDIDATE)
print(json.dumps({'target': str(TARGET), 'sha256': sha(TARGET)}, ensure_ascii=False))
