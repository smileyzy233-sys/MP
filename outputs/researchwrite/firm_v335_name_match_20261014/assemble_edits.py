from pathlib import Path
import json,re

B=Path(__file__).resolve().parent
src={r['p']:r['text'] for r in json.loads((B/'sources/actual_paragraphs.json').read_text(encoding='utf-8'))}
edits=[]
for name in ['name_match_front.json','name_match_back.json']:
    edits.extend(json.loads((B/'reviews'/name).read_text(encoding='utf-8')))
rows={r['p']:r for r in edits}
assert len(rows)==len(edits)
flow=['2010年或更早的行业代码','↓','确认分类版本 → 取得类别名称','↓','LLM比较类别名称与目录条款活动','↓','记录匹配条款及前后准入要求','↓','判断本轮放宽，确定固定Treat']
rows[7]['new']=''.join(flow)
rows[65]['new']='匹配条款中的股比上限、合资合作形式和禁止进入等要求分别记录，鼓励资格单独保存。同一条款涉及多种活动或不同要求时，逐项对应原文中的活动与要求，保留限定语及子项位置，并结合相关有效规定核对其效力和生效时间。改革前后要求用明确文字保存，同时记录股比上限等具有直接含义的数值。'
rows[68]['new']=rows[68]['new'].replace('LLM依据','大语言模型（LLM）依据')
rows[73]['new']='匹配与法律比较'
rows[79]['new']='确认本轮未放宽'
# The preceding paragraph already establishes the exposure basis of the target.
del rows[154]
for p,r in rows.items():
    assert r['old']==src[p],p
    assert re.findall(r'\{\{M\d+\}\}',r['old'])==re.findall(r'\{\{M\d+\}\}',r['new']),p
    assert '\n' not in r['new'],p
(B/'approved_edits.json').write_text(json.dumps(sorted(rows.values(),key=lambda r:r['p']),ensure_ascii=False,indent=2),encoding='utf-8')
(B/'flow_lines.json').write_text(json.dumps({'7':flow},ensure_ascii=False,indent=2),encoding='utf-8')
if not (B/'layout_breaks.json').exists():(B/'layout_breaks.json').write_text('[]',encoding='utf-8')
print(len(rows),'approved paragraph edits')
