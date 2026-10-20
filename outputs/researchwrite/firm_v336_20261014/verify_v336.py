from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import re,json,hashlib
ROOT=Path(r'A:\桌面\study');BASE=Path(__file__).resolve().parent
SRC=ROOT/'企业微观层面_v3.35.docx';OUT=ROOT/'企业微观层面_v3.36.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';M='http://schemas.openxmlformats.org/officeDocument/2006/math';NS={'w':W,'m':M}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
with ZipFile(SRC) as z:source={n:z.read(n) for n in z.namelist()}
with ZipFile(OUT) as z:
    assert z.testzip() is None
    blobs={n:z.read(n) for n in z.namelist()}
x=etree.fromstring(blobs['word/document.xml']);body=x.find('w:body',NS)
text='\n'.join(''.join(p.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS)) for p in body)
checks['source_sha256_unchanged']=sha(SRC)=='580f238eb7513b83edac094d2c3438617815d84d5815abf2fc4958993dd751e6'
checks['no_retired_design']=not any(k in text for k in ['Treat','Post','DID','双重差分','固定处理','2014年模型部门目标','以2010年为参照','h=t','本轮改革','改革前所属','2010年末已经'])
checks['no_unconverted_math']=not any(k in text for k in ['$','\\mathrm','\\beta','{{M','[TODO]','�'])
displays=[p for p in body if p.tag=='{'+W+'}p' and p.xpath('./w:r/w:tab',namespaces=NS)]
numbers=[re.search(r'（A(\d+)）$',''.join(p.xpath('.//w:t/text()',namespaces=NS))).group(1) for p in displays]
checks['equation_labels_contiguous']=numbers==[str(i) for i in range(1,17)]
checks['all_display_math_native']=len(displays)==16 and all(p.find('m:oMath',NS) is not None for p in displays)
checks['editable_tables']=len(x.findall('.//w:tbl',NS))==3 and not x.xpath('//w:drawing|//w:pict',namespaces=NS)
checks['empty_header']=not x.findall('.//w:headerReference',NS)
checks['footer_preserved']=all(blobs[n]==b for n,b in source.items() if re.fullmatch(r'word/footer\d+.xml',n))
checks['page_number_field']=any(b'PAGE' in b for n,b in blobs.items() if n.startswith('word/footer'))
checks['section_geometry_preserved']=etree.tostring(x.find('.//w:sectPr',NS))==etree.tostring(etree.fromstring(source['word/document.xml']).find('.//w:sectPr',NS))
bad=[]
for n,b in blobs.items():
    if n.startswith('word/') and n.endswith('.xml'):
        r=etree.fromstring(b)
        for tag in ['keepNext','keepLines','pageBreakBefore']:
            bad.extend((n,tag) for e in r.findall('.//w:'+tag,NS) if e.get('{'+W+'}val','true') not in ['0','false','off'])
checks['pagination_controls_disabled_in_all_parts_and_styles']=not bad
refs=[int(re.match(r'^\[(\d+)\]',t).group(1)) for p in body if (t:=''.join(p.xpath('.//w:t/text()',namespaces=NS))).startswith('[') and re.match(r'^\[\d+\]',t)]
checks['bibliography_contiguous']=refs==list(range(1,17))
allrefs=set()
for m in re.finditer(r'\[(\d+(?:[,—,]\d+)*)\]',text):
    st=m.group(1)
    if '—' in st:
        lo,hi=map(int,st.split('—'));allrefs.update(range(lo,hi+1))
    else:allrefs.update(map(int,st.split(',')))
checks['citations_resolve']=allrefs<=set(refs)
rels=etree.fromstring(blobs['word/_rels/document.xml.rels']);ids={e.get('Id') for e in rels}
checks['hyperlink_relationships_resolve']=all(e.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id') in ids for e in x.findall('.//w:hyperlink',NS))
record={'checks':checks,'all_pass':all(checks.values()),'native_math_objects':len(x.findall('.//m:oMath',NS)),'ordinary_page_breaks':len(x.xpath('//w:br[@w:type="page"]',namespaces=NS)),'output_sha256':sha(OUT),'bad_pagination_controls':bad,'bibliography_numbers':refs,'equation_numbers':numbers}
(BASE/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2))
assert all(checks.values()),checks
