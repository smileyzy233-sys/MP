from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json,re,hashlib,math
ROOT=Path(r'A:\桌面\study');BASE=Path(__file__).resolve().parent
OUT=ROOT/'企业微观层面_v4.1.docx';SRC=ROOT/'企业微观层面_v4.docx'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def txt(e):return ''.join(e.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
checks={}
with ZipFile(OUT) as z:
    checks['zip_integrity']=z.testzip() is None
    parts={n:etree.fromstring(z.read(n)) for n in z.namelist() if n.startswith('word/') and n.endswith('.xml')}
    r=parts['word/document.xml'];b=r.find('w:body',NS);plain=txt(b)
    formulas=r.xpath('//w:body/w:p[w:r/w:tab]',namespaces=NS)
    labels=[int(re.search(r'（A(\d+)）$',txt(e))[1]) for e in formulas]
    checks['six_formulas_continuous']=labels==list(range(1,7))
    checks['core_formulas']=all(s in txt(e) for s,e in zip(['max','Intensity','Intensity','μ','ξ','δ'],formulas))
    checks['references_current']=all(1<=int(x)<=6 for x in re.findall(r'式（A(\d+)）',plain))
    flags=[]
    for n,tree in parts.items():
        for tag in ['keepNext','keepLines','pageBreakBefore']:
            for q in tree.findall('.//w:'+tag,NS):
                if q.get(W+'val','true').lower() not in ['0','false','off']:flags.append([n,tag])
    checks['no_enabled_pagination_flags']=not flags
    checks['blank_headers']=all(not txt(tree).strip() and not tree.xpath('.//w:drawing|.//w:pict|.//w:instrText',namespaces=NS) for n,tree in parts.items() if n.startswith('word/header'))
    checks['page_number_field']=any('PAGE' in ''.join(tree.xpath('.//w:instrText/text()',namespaces=NS)) for n,tree in parts.items() if n.startswith('word/footer'))
    checks['two_editable_tables']=len(b.findall('w:tbl',NS))==2
    checks['no_rasterized_flowchart']=not r.xpath('.//w:drawing|.//w:pict',namespaces=NS)
    checks['all_seven_sections']=all(any(txt(e).startswith(f'A.{i} ') for e in b) for i in range(1,8))
    checks['no_third_level_headings']=not any(re.match(r'A\.\d\.\d',txt(e)) for e in b)
    checks['approved_routine_explanations_removed']=all(s not in plain for s in ['面板允许企业间的观察年数不同','首次被调查不等同于实际设立','更名改号','年初人数','折旧','4190','argmin','EQUITY_CAP','NONE / UNKNOWN'])
    checks['no_legacy_design']=all(s not in plain for s in ['Treat','Post','DID','2014年动态'])
    checks['no_tex_or_garbled_text']=not any(t.text and any(s in t.text for s in ['\\','$','\ufffd','???']) for t in r.xpath('//w:t|//m:t',namespaces=NS))
    checks['no_obsolete_table_refs']='表A2' not in plain
    checks['unknown_and_fixed_denominator']='未知不补零、不缩小分母' in plain
    checks['conditional_prediction_and_causal_boundary']='基准系数描述条件关联' in plain and '该情景沿用关联模型的条件解释' in plain
    checks['prediction_scope_and_other_assumption']='假定其不随限制变化而反应' in plain
    checks['scenario_direction']='情景0采用旧规则、情景1采用后续规则' in plain and '反向恢复旧规则情景0' in plain
    checks['no_forced_new_pe_sequence']='先在局部均衡' not in plain and '采用局部均衡拟合时' in plain
    checks['source_unchanged']=sha(SRC)=='26c16648f50072f6125625bf443163d0ed9291e925d30131b2349ba0b38513ef'
    refs=[x for x in b if re.match(r'^\[\d+\]',txt(x))]
    checks['ten_numbered_references']=[int(re.match(r'^\[(\d+)\]',txt(x))[1]) for x in refs]==list(range(1,11))
    # Boundary arithmetic is a validation of the proposed scoring, not policy/data work.
    def cap(p):return 3 if 0<p<25 else 2 if 25<=p<=50 else 1 if 50<p<100 else 0 if p==100 else None
    checks['cap_thresholds']=[cap(p) for p in [1,24.9,25,49,50,50.1,70,100]]==[3,3,2,2,2,1,1,0]
    checks['scoring_examples']=math.isclose((cap(49)/3+1)/4,5/12) and math.isclose((cap(70)/3+1)/4,1/3)
record={'checks':checks,'output_sha256':sha(OUT),'formula_labels':labels,'native_omml':len(r.findall('.//m:oMath',NS)),'flags':flags}
(BASE/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
fails=[k for k,v in checks.items() if not v]
print(json.dumps({'checks':len(checks),'failed':fails,'sha256':record['output_sha256']},ensure_ascii=False))
assert not fails,fails
