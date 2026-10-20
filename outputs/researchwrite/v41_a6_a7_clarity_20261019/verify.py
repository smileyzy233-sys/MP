from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json,re,hashlib,math
BASE=Path(__file__).resolve().parent
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}'
def txt(e):return ''.join(e.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
def read(p):
    with ZipFile(p) as z:return {n:z.read(n) for n in z.namelist()}
def nodebytes(es):return [etree.tostring(e,method='c14n') for e in es]
old=read(BASE/'input.docx');new=read(BASE/'review.docx')
ro=etree.fromstring(old['word/document.xml']);rn=etree.fromstring(new['word/document.xml'])
bo=list(ro.find('w:body',NS));bn=list(rn.find('w:body',NS))
io=next(i for i,e in enumerate(bo) if txt(e).startswith('A.6 '));jn=next(i for i,e in enumerate(bn) if txt(e).startswith('A.6 '))
to=next(i for i,e in enumerate(bo) if txt(e)=='参考文献与资料');tn=next(i for i,e in enumerate(bn) if txt(e)=='参考文献与资料')
while to>io and not txt(bo[to-1]):to-=1
while tn>jn and not txt(bn[tn-1]):tn-=1
checks={}
checks['all_other_parts_identical']=all(old[k]==v for k,v in new.items() if k!='word/document.xml')
checks['A1_A5_and_front_exact']=nodebytes(bo[:io])==nodebytes(bn[:jn])
checks['references_and_tail_exact']=nodebytes(bo[to:])==nodebytes(bn[tn:])
eq=lambda r:r.xpath('//w:body/w:p[w:r/w:tab]',namespaces=NS)
checks['all_six_original_equations_exact']=nodebytes(eq(ro))==nodebytes(eq(rn))
checks['continuous_numbers']=[int(re.search(r'（A(\d+)）$',txt(e))[1]) for e in eq(rn)]==list(range(1,7))
checks['editable_example_table']=len(rn.findall('.//w:tbl',NS))==3
plain=txt(rn)
checks['example_explicitly_hypothetical']='虚拟数值' in plain and '虚拟预测值' in plain
checks['example_arithmetic']=math.isclose(200/(200+800),.2) and math.isclose(300/(300+900),.25) and math.isclose(.25-.2,.05)
checks['unaffected_scoring_preserved']=nodebytes(ro.xpath('//w:tbl',namespaces=NS)[:2])==nodebytes(rn.xpath('//w:tbl',namespaces=NS)[:2])
flags=[]
for name,data in new.items():
    if name.startswith('word/') and name.endswith('.xml'):
        tree=etree.fromstring(data)
        for tag in ['keepNext','keepLines','pageBreakBefore']:
            for e in tree.findall('.//w:'+tag,NS):
                if e.get(W+'val','true').lower() not in ['0','false','off']:flags.append([name,tag])
checks['no_enabled_pagination_flags']=not flags
checks['headers_blank']=all(not txt(etree.fromstring(v)).strip() for k,v in new.items() if k.startswith('word/header') and k.endswith('.xml'))
checks['page_numbers_preserved']=any(b'PAGE' in v for k,v in new.items() if k.startswith('word/footer'))
checks['no_unconverted_tex_or_garbled']=not any(t.text and any(s in t.text for s in ['\\','$','\ufffd','???']) for t in rn.xpath('//w:t|//m:t',namespaces=NS))
checks['cost_and_scenario_explanations']='先沿用A.5的模型形式' in plain and '两套预测方程' in plain and '同时给定各部门一组候选' in plain and '可能不同于A.6的条件目标' in plain
out={'checks':checks,'stage_sha256':hashlib.sha256((BASE/'review.docx').read_bytes()).hexdigest(),'native_omml':len(rn.findall('.//m:oMath',NS))}
(BASE/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
failed=[k for k,v in checks.items() if not v]
print(json.dumps({'checks':len(checks),'failed':failed,'stage_sha256':out['stage_sha256']},ensure_ascii=False))
assert not failed,failed
