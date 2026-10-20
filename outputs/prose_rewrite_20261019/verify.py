from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import json,re,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
B=Path(__file__).resolve().parent
meta=json.loads((B/'build_meta.json').read_text(encoding='utf-8'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
src=Path(meta['source']);out=Path(meta['output']);ref=Path(r'A:\桌面\制度性开放\审稿意见\手动改和写\审稿人回复.docx')
def fp(n):return (n.tag,tuple(sorted(n.attrib.items())),n.text,tuple(fp(c) for c in n))
with ZipFile(src) as s,ZipFile(out) as o:
 a=E.fromstring(s.read('word/document.xml'));b=E.fromstring(o.read('word/document.xml'))
 ap=a.xpath('//w:body//w:p',namespaces=ns);bp=b.xpath('//w:body//w:p',namespaces=ns)
 txt=lambda p:''.join(p.xpath('.//w:t/text()|.//m:t/text()',namespaces=ns))
 full='\n'.join(map(txt,bp));source_full='\n'.join(map(txt,ap))
 active=[]
 for n in o.namelist():
  if n.startswith('word/') and n.endswith('.xml'):
   root=E.fromstring(o.read(n))
   for x in root.xpath('//w:keepNext|//w:keepLines|//w:pageBreakBefore',namespaces=ns):
    if x.get('{'+ns['w']+'}val','1') not in ['0','false','off']:active.append((n,x.tag))
 checks={
 'source_unchanged':hashlib.sha256(src.read_bytes()).hexdigest()==meta['source_sha256'],
 'reference_unchanged':hashlib.sha256(ref.read_bytes()).hexdigest()==json.loads((B/'reference.json').read_text(encoding='utf-8'))['sha256'],
 'output_matches_build':hashlib.sha256(out.read_bytes()).hexdigest()==meta['output_sha256'],
 'word_render_matches_output':json.loads((B/'render_final/word_open.json').read_text(encoding='utf-8-sig'))['sha256'].lower()==meta['output_sha256'],
 'all_60_math_objects_preserved':[fp(x) for x in a.xpath('//m:oMath',namespaces=ns)]==[fp(x) for x in b.xpath('//m:oMath',namespaces=ns)] and len(b.xpath('//m:oMath',namespaces=ns))==60,
 '6_equation_numbers':re.findall('（A[1-6]）',full)==['（A'+str(i)+'）' for i in range(1,7)],
 'A1_A7_headings_preserved':[txt(p) for p in ap if re.match(r'^A\.[1-7] ',txt(p))]==[txt(p) for p in bp if re.match(r'^A\.[1-7] ',txt(p))],
 'all_3_editable_tables':len(b.xpath('//w:tbl',namespaces=ns))==3,
 'score_and_example_tables_unchanged':[fp(x) for x in a.xpath('//w:tbl',namespaces=ns)[1:]]==[fp(x) for x in b.xpath('//w:tbl',namespaces=ns)[1:]],
 'references_and_links_unchanged':[fp(p) for p in ap[90:]]==[fp(p) for p in bp[-10:]],
 'citations_preserved':re.findall(r'\[[0-9,]+\]',source_full)==re.findall(r'\[[0-9,]+\]',full),
 'pagination_flags_disabled':not active,
 'no_placeholder_or_replacement_char':'{{' not in full and '\ufffd' not in full,
 'other_package_parts_unchanged':all(o.read(n)==s.read(n) for n in s.namelist() if n!='word/document.xml'),
 'zip_valid':o.testzip() is None,
 'seven_page_images':len(list((B/'render_final').glob('page-*.png')))==7
 }
 assert all(checks.values()),checks
 record={'checks':checks,'passed':len(checks),'source_characters':len(source_full),'output_characters':len(full),'visual_review':'7 pages inspected; A.6 heading moved with ordinary page break; formulas, table captions, tables, flow diagram, references and page numbers readable; no clipping or isolated heading','skills':['nature-polishing','docx','documents'],'agents':['prose_a1_a4: draft A.1-A.4','style_audit: reference style and semantic comparison'],'remaining_scope':'Writing revision only; no empirical analysis or external policy re-verification performed.'}
 (B/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(record,ensure_ascii=False,indent=2))
