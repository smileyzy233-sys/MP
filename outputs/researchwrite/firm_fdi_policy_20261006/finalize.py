from pathlib import Path
import json, hashlib, shutil

ROOT=Path(__file__).resolve().parent
meta=json.loads((ROOT/'build_meta.json').read_text(encoding='utf-8'))
out=Path(meta['output_path']);md=Path(meta['markdown_path'])
assert hashlib.sha256(out.read_bytes()).hexdigest()==meta['output_sha256']
verification=ROOT/'qa_logs/verification.json'
v=json.loads(verification.read_text(encoding='utf-8'))
v['visual_review_pending']=False
v['visual_review_passed']=True
v['content_review_passed']=True
v['reviewers']={'draft_empirical':'A3-A5 authoring','draft_structural':'A6-A7 authoring','review_new_plan':'full content audit and P1 closure','luna_visual':'latest pages 1-6 visual QA','root':'latest pages 7-13 visual QA and full integration'}
verification.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
exports=ROOT/'exports';exports.mkdir(exist_ok=True)
for source,dest in [(out,exports/'proposal_final.docx'),(md,exports/'proposal_final.md')]:
    if dest.exists():raise RuntimeError('Archive already exists; preserve it')
    shutil.copyfile(source,dest)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==hashlib.sha256(dest.read_bytes()).hexdigest()
state={'date':'2026-10-06','mode':'hybrid','status':'complete','scope':'research design document only; no empirical or structural computation performed','output':meta['output_path'],'markdown':meta['markdown_path'],'pages':v['pages'],'native_math':v['native_math'],'tables':v['tables'],'visual_qa':'passed all latest 13 pages','content_qa':'passed after legal scope, sample domain and department shock corrections','remaining_execution_conditions':['actual independent reform support','observation price convention and model calibration','PE/GE identification consistency','entry and within-sector extensions when required'],'source_hashes_unchanged':True}
(ROOT/'state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'sha256':meta['output_sha256'],'pages':v['pages'],'qa':'passed'},ensure_ascii=False))
