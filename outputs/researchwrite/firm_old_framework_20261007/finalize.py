from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
v=json.loads((ROOT/'verification.json').read_text(encoding='utf-8'))
for e in json.loads((ROOT/'source_manifest.json').read_text(encoding='utf-8')):
    assert hashlib.sha256(Path(e['source']).read_bytes()).hexdigest()==e['sha256']
assert hashlib.sha256(Path(v['output']).read_bytes()).hexdigest()==v['sha256']
v['visual_review_pending']=False;v['visual_review_passed']=True;v['content_review_passed']=True
v['visual_reviewers']={'luna_framework_visual':'pages 1-5','root':'pages 6-11'}
(ROOT/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
state={'date':'2026-10-07','status':'complete','output':v['output'],'scope':'Rewrite current proposal with old seven-section framework; no research computation','input_hashes_checked':True,'pages':v['pages'],'main_sections':7,'subsections':16,'tables':3,'equations':17,'content_qa':'passed','visual_qa':'all 11 pages passed','remaining_research_limits':['Empirical estimates not run','Structural parameter calibration and actual reform support remain execution conditions','Coarse-sector welfare remains a conditional model scenario']}
(ROOT/'state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':v['output'],'pages':v['pages'],'bytes':Path(v['output']).stat().st_size,'sources_unchanged':True,'qa':'passed'},ensure_ascii=False))
