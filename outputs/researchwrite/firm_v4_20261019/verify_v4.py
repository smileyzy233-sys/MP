from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import hashlib, json, re, math

ROOT=Path(r'A:\桌面\study'); BASE=Path(__file__).resolve().parent
SOURCE=ROOT/'企业微观层面_v3.37.docx'; OUT=ROOT/'企业微观层面_v4.docx'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def txt(e):return ''.join(e.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
checks={}
with ZipFile(OUT) as z:
    checks['zip_integrity']=z.testzip() is None
    parts={n:etree.fromstring(z.read(n)) for n in z.namelist() if n.startswith('word/') and n.endswith('.xml')}
    r=parts['word/document.xml'];body=r.find('w:body',NS);plain=txt(body)
    checks['native_omml_count']=len(r.findall('.//m:oMath',NS))
    equations=r.xpath('//w:body/w:p[w:r/w:tab]',namespaces=NS)
    labels=[int(re.search(r'（A(\d+)）$',txt(e))[1]) for e in equations]
    checks['equation_sequence_A1_A18']=labels==list(range(1,19))
    refs=[int(x) for x in re.findall(r'式（A(\d+)）',plain)]
    checks['references_in_range']=all(1<=n<=18 for n in refs)
    targets={n:txt(e) for n,e in zip(labels,equations)}
    checks['equation_topics']=(all(t in targets[2] for t in ['Intensity','UNKNOWN']) and 'Intensity' in targets[3] and 'Intensity' in targets[4] and 'Intensity' in targets[5] and 'covered' in targets[10] and 'μ' in targets[11] and 'ξ' in targets[12] and 'δ' in targets[14] and 'Ω' in targets[17])
    enabled=[]
    for name,tree in parts.items():
        for tag in ['keepNext','keepLines','pageBreakBefore']:
            for e in tree.findall('.//w:'+tag,NS):
                if e.get(W+'val','true').lower() not in ['0','false','off']:enabled.append([name,tag])
    checks['no_enabled_pagination_flags_in_any_part']=not enabled
    checks['all_headers_empty']=all(not txt(tree).strip() and not tree.xpath('.//w:drawing|.//w:pict|.//w:instrText',namespaces=NS) for n,tree in parts.items() if n.startswith('word/header'))
    checks['page_field_preserved']=any('PAGE' in ''.join(tree.xpath('.//w:instrText/text()',namespaces=NS)) for n,tree in parts.items() if n.startswith('word/footer'))
    checks['editable_three_tables']=len(body.findall('w:tbl',NS))==3
    checks['no_raster_figure']=not r.xpath('.//w:drawing|.//w:pict',namespaces=NS)
    checks['all_seven_sections']=all(any(txt(e).startswith(f'A.{i} ') for e in body) for i in range(1,8))
    checks['auxiliary_restrict_only']=sum(1 for t in r.xpath('//m:t',namespaces=NS) if t.text=='Restrict')==2
    checks['no_legacy_design']=not any(s in plain for s in ['Treat','Post','DID','2010年为参照','2014年动态结果'])
    checks['no_unconverted_tex']=not any(t.text and ('\\' in t.text or '$' in t.text) for t in r.xpath('//m:t|//w:t',namespaces=NS))
    checks['no_garbled_replacement']=not any(s in plain for s in ['\ufffd','???','待填写','TODO'])
    checks['reference_17_and_source_pages']='[17]' in plain and '第3—4页' in plain and '第5—7页' in plain
    checks['source_unchanged']=sha(SOURCE)=='f7792b617b2237c50d42f25ac76a2fe0e25aa641ddc2e9e4532e45384554d271'
    checks['unknown_coverage']='包括调查外、强度未知和其他无法预测的生产' in plain
    checks['explicit_fixed_denominator']='再以固定权重' in plain and '不补0或减少分母' in plain and bool(r.xpath('//m:f[m:num//m:t="1"][m:den//m:t="4"]',namespaces=NS))
    checks['scoring_table_maxima']=all(str(i) in txt(body.findall('w:tbl',NS)[2]) for i in range(1,5))

# Test only the proposed arithmetic and boundary cases; no policy/data processing.
def cap(p):
    if p is None:return None
    if p==0:return 'BAN'
    if p==100:return 0
    if 0<p<25:return 3
    if 25<=p<=50:return 2
    if 50<p<100:return 1
    raise ValueError('Out of range')
def intensity(b,s):
    if b==1:return 1.
    if b!=0 or any(v is None for v in s):return None
    return sum(v/m for v,m in zip(s,[3,1,1,1]))/4
checks['cap_thresholds']=[cap(v) for v in [0,1,24.9,25,49,50,50.1,70,99.9,100,None]]==['BAN',3,3,2,2,2,1,1,1,0,None]
checks['example_49_percent']=math.isclose(intensity(0,[cap(49),1,0,0]),5/12)
checks['example_70_percent']=math.isclose(intensity(0,[cap(70),1,0,0]),1/3)
checks['ban_and_unknown']=intensity(1,[None]*4)==1 and intensity(0,[1,None,0,0]) is None and intensity(None,[0]*4) is None
checks['nonban_top_and_zero']=intensity(0,[3,1,1,1])==1 and intensity(0,[0,0,0,0])==0
checks['monotone_in_known_dimension_scores']=all(intensity(0,[c,o,g,e])<=intensity(0,[cc,oo,gg,ee]) for c in range(4) for o in range(2) for g in range(2) for e in range(2) for cc in range(c,4) for oo in range(o,2) for gg in range(g,2) for ee in range(e,2))
record={'output_sha256':sha(OUT),'checks':checks,'enabled_flags':enabled,'equation_labels':labels,'formula_references':refs}
(BASE/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
fails=[k for k,v in checks.items() if v is False]
print(json.dumps({'checks':len(checks),'failed':fails,'math_objects':checks['native_omml_count'],'output_sha256':record['output_sha256']},ensure_ascii=False))
assert not fails,fails
