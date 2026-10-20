from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json,hashlib,re,sys
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
SOURCE=B/'sources/current_before.docx'
TARGET=Path(sys.argv[1]) if len(sys.argv)>1 else B/'v335_candidate.docx'
N={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'};W='{'+N['w']+'}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,val):
 checks.append({'check':name,'passed':bool(val)})
 assert val,name
with ZipFile(SOURCE) as z:old={n:z.read(n) for n in z.namelist()}
with ZipFile(TARGET) as z:
 check('ZIP intact',z.testzip() is None)
 new={n:z.read(n) for n in z.namelist()}
x0=etree.fromstring(old['word/document.xml']);x1=etree.fromstring(new['word/document.xml'])
p0=x0.xpath('//w:body//w:p',namespaces=N);p1=x1.xpath('//w:body//w:p',namespaces=N)
origin=json.loads((B/'qa/origin_map.json').read_text(encoding='utf-8'))
patches=json.loads((B/'approved_edits.json').read_text(encoding='utf-8'));edited={r['p'] for r in patches}
layout=json.loads((B/'layout_breaks.json').read_text(encoding='utf-8')) if (B/'layout_breaks.json').exists() else []
removed_breaks=json.loads((B/'remove_breaks.json').read_text(encoding='utf-8'))
check('Untargeted original paragraphs unchanged',all(etree.tostring(p0[int(k)])==etree.tostring(p1[v]) for k,v in origin.items() if int(k) not in edited|{i-1 for i in layout}|set(removed_breaks)))
check('69 native mathematical objects unchanged',[etree.tostring(e) for e in x0.findall('.//m:oMath',N)]==[etree.tostring(e) for e in x1.findall('.//m:oMath',N)] and len(x1.findall('.//m:oMath',N))==69)
check('All original hyperlink objects unchanged',[etree.tostring(e) for e in x0.findall('.//w:hyperlink',N)]==[etree.tostring(e) for e in x1.findall('.//w:hyperlink',N)])
check('Footer bytes unchanged',all(new.get(n)==v for n,v in old.items() if re.match(r'word/footer\d+\.xml$',n)))
check('Header empty',not x1.findall('.//w:headerReference',N) and not any(re.match(r'word/header\d+\.xml$',n) for n in new))
check('Styles unchanged',all(old[n]==new[n] for n in ['word/styles.xml','word/stylesWithEffects.xml']))
tables=x1.findall('.//w:tbl',N)
check('3 editable tables retained',len(tables)==3)
table=json.loads((B/'table_a2.json').read_text(encoding='utf-8'))
values=[[''.join(c.xpath('.//w:t/text()',namespaces=N)) for c in row.findall('w:tc',N)] for row in tables[2].findall('w:tr',N)]
check('Table A2 four-column content exact',values==table['rows'])
for n,v in new.items():
 if n.startswith('word/') and n.endswith('.xml'):
  t=etree.fromstring(v)
  for tag in ['keepNext','keepLines','pageBreakBefore']:
   check(n+': '+tag+' disabled',all(e.get(W+'val','true') in ['0','false','off'] for e in t.findall('.//w:'+tag,N)))
plain=''.join(x1.xpath('.//w:t/text()',namespaces=N))
for s in ['GB小类名称','确认未命中','限制状态','未受限','其中2011草案反映拟议要求','鼓励资格另行记录','H6361','煤炭及制品批发','AMNE部门','模型部门']:
 check('Required content: '+s,s in plain)
check('No leaked placeholders','{{M' not in plain and '\ufffd' not in plain)
check('Sixteen numbered equations retained',all(f'（A{i}）' in plain for i in range(1,17)))
check('Idea internal snapshot unchanged',sha(B/'sources/idea_readonly.docx')=='7c05568616604b00fae2829bad64938ff509ea5a2b87d8b00a71b2f548d152e9')
result={'target':str(TARGET),'sha256':sha(TARGET),'all_passed':True,'checks':checks,'changed_paragraphs':len(patches),'paragraphs':len(p1)}
(B/'qa'/('verification_current.json' if TARGET.name=='企业微观层面_v3.35.docx' else 'verification_candidate.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'all_passed':True,'checks':len(checks),'sha256':sha(TARGET)},ensure_ascii=False))
