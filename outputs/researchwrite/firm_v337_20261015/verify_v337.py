from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import re,json,hashlib
ROOT=Path(r'A:\桌面\study');BASE=Path(__file__).resolve().parent
SRC=ROOT/'企业微观层面_v3.36.docx';OUT=ROOT/'企业微观层面_v3.37.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';M='http://schemas.openxmlformats.org/officeDocument/2006/math';NS={'w':W,'m':M}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def texts(e):return ''.join(e.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
with ZipFile(SRC) as z:source={n:z.read(n) for n in z.namelist()}
with ZipFile(OUT) as z:
    assert z.testzip() is None
    blobs={n:z.read(n) for n in z.namelist()}
x=etree.fromstring(blobs['word/document.xml']);sx=etree.fromstring(source['word/document.xml']);body=x.find('w:body',NS)
text='\n'.join(texts(p) for p in body)
checks={}
checks['source_unchanged']=sha(SRC)=='2819289f94e1cb07c84985832e95b0787dda4eb81762285288fd3ff669719744'
bad_phrases=['主估计窗口依据','后续根据资料确定','条件成立后开展','核实后再判断','仍待确定','尚待','最终安排','优先核验阶段','m310','qt_zcz','f437','5,000','1329/1322','锁定模型版本后']
checks['removed_generic_progress_and_audit_details']=not any(p in text for p in bad_phrases)
checks['annual_panel_preserved']=all(p in text for p in ['2007—2020','Restrict','企业固定效应','条件关联','转行业','未知','生产情景'])
checks['no_retired_design']=not any(p in text for p in ['Treat','Post','DID','2014年模型部门目标','统一事件年'])
displays=[p for p in body if p.tag=='{'+W+'}p' and p.xpath('./w:r/w:tab',namespaces=NS)]
source_displays=[p for p in sx.find('w:body',NS) if p.tag=='{'+W+'}p' and p.xpath('./w:r/w:tab',namespaces=NS)]
numbers=[re.search(r'（A(\d+)）$',''.join(p.xpath('.//w:t/text()',namespaces=NS))).group(1) for p in displays]
checks['equation_numbers']=numbers==[str(i) for i in range(1,17)]
def canonical_math(ps):return [etree.tostring(p.find('m:oMath',NS),method='c14n',exclusive=True) for p in ps]
checks['all_16_numbered_equations_native_and_unchanged']=len(displays)==16 and canonical_math(displays)==canonical_math(source_displays)
checks['no_tex_or_corruption']=not any(s in text for s in ['$','\\mathrm','\\beta','�','{{M','[TODO]'])
checks['editable_figure_and_tables']=len(x.findall('.//w:tbl',NS))==3 and not x.xpath('//w:drawing|//w:pict',namespaces=NS)
checks['blank_header']=not x.findall('.//w:headerReference',NS)
checks['page_field_and_footer_preserved']=all(blobs[n]==b for n,b in source.items() if re.fullmatch(r'word/footer\d+.xml',n)) and any(b'PAGE' in b for n,b in blobs.items() if n.startswith('word/footer'))
checks['section_geometry_preserved']=etree.tostring(x.find('.//w:sectPr',NS))==etree.tostring(sx.find('.//w:sectPr',NS))
bad=[]
for n,b in blobs.items():
    if n.startswith('word/') and n.endswith('.xml'):
        tree=etree.fromstring(b)
        for tag in ['keepNext','keepLines','pageBreakBefore']:
            bad.extend((n,tag) for e in tree.findall('.//w:'+tag,NS) if e.get('{'+W+'}val','true') not in ['0','false','off'])
checks['all_paragraph_parts_and_styles_disable_prohibited_controls']=not bad
refs=[int(re.match(r'^\[(\d+)\]',t).group(1)) for p in body if re.match(r'^\[\d+\]',t:=texts(p))]
checks['all_16_references_preserved']=refs==list(range(1,17))
rr=etree.fromstring(blobs['word/_rels/document.xml.rels']);ids={r.get('Id') for r in rr}
checks['hyperlinks_valid']=all(h.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id') in ids for h in x.findall('.//w:hyperlink',NS))
headings=[texts(p) for p in body if re.match(r'^A\.[1-7] ',texts(p))]
checks['a1_to_a7_framework_preserved']=len(headings)==7
source_chars=len(''.join(texts(p) for p in sx.find('w:body',NS)))
final_chars=len(''.join(texts(p) for p in body))
record={'checks':checks,'all_pass':all(checks.values()),'output_sha256':sha(OUT),'source_characters':source_chars,'final_characters':final_chars,'text_reduction_pct':round((1-final_chars/source_chars)*100,1),'numbered_equations':16,'native_math_objects':len(x.findall('.//m:oMath',NS)),'ordinary_breaks':len(x.xpath('//w:br[@w:type="page"]',namespaces=NS)),'bad_controls':bad}
(BASE/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2));assert record['all_pass']
