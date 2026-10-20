from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import hashlib,json,re,sys
import pdfplumber

ROOT=Path(__file__).resolve().parent
meta=json.loads((ROOT/'edit_meta.json').read_text(encoding='utf-8'))
SOURCE=Path(meta['source']);TARGET=Path(meta['output'])
render=ROOT/'render'/sys.argv[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
checks={}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def nodes(tree,path):return [etree.tostring(n,method='c14n') for n in tree.xpath(path,namespaces=NS)]
checks['source_unchanged']=digest(SOURCE)==meta['source_sha256']
checks['output_matches_edit']=digest(TARGET)==meta['sha256']
with ZipFile(SOURCE) as s,ZipFile(TARGET) as d:
    checks['zip_integrity']=d.testzip() is None
    checks['same_package_parts']=s.namelist()==d.namelist()
    changed=[n for n in s.namelist() if s.read(n)!=d.read(n)]
    checks['only_document_and_footnotes_changed']=set(changed)=={'word/document.xml','word/footnotes.xml'}
    sx=etree.fromstring(s.read('word/document.xml'));dx=etree.fromstring(d.read('word/document.xml'))
    for key,path in [('math','//m:oMath'),('paragraph_properties','//w:pPr'),('table_properties','//w:tblPr'),('cell_properties','//w:tcPr'),('sections','//w:sectPr'),('hyperlinks','//w:hyperlink'),('footnote_markers','//w:footnoteReference')]:
        checks[key+'_preserved']=nodes(sx,path)==nodes(dx,path)
    ps=sx.xpath('//w:p',namespaces=NS);pd=dx.xpath('//w:p',namespaces=NS)
    checks['paragraph_count_preserved']=len(ps)==len(pd)
    checks['headings_preserved']=nodes(sx,'//w:p[w:pPr/w:pStyle[@w:val="1" or @w:val="21" or @w:val="aa"]]')==nodes(dx,'//w:p[w:pPr/w:pStyle[@w:val="1" or @w:val="21" or @w:val="aa"]]')
    checks['numbered_equations_preserved']=nodes(sx,'//w:p[w:pPr/w:pStyle[@w:val="Equation"]]')==nodes(dx,'//w:p[w:pPr/w:pStyle[@w:val="Equation"]]')
    text=''.join(dx.xpath('//w:t/text()|//m:t/text()',namespaces=NS))
    checks['requested_sentence_replaced']='企业分析考察原有企业的反应，完整行业统计补充' not in text and '企业层面的基准分析考察改革前已有企业' in text
    checks['no_placeholders']=not any(t in text for t in ['{{','}}','\ufffd','[[FLOWCHART]]'])
    checks['math_count_116']=len(dx.xpath('//m:oMath',namespaces=NS))==116
    checks['table_count_4']=len(dx.xpath('//w:tbl',namespaces=NS))==4
    checks['no_images_added']=len(dx.xpath('//w:drawing|//w:pict',namespaces=NS))==0
    sf=etree.fromstring(s.read('word/footnotes.xml'));df=etree.fromstring(d.read('word/footnotes.xml'))
    checks['footnote_hyperlinks_preserved']=nodes(sf,'//w:hyperlink')==nodes(df,'//w:hyperlink')
    checks['footnote_properties_preserved']=nodes(sf,'//w:pPr')==nodes(df,'//w:pPr')
    eqs=re.findall(r'\((A\d+)\)',text)
    checks['equation_numbers']=eqs==['A'+str(i) for i in range(1,18)]
    checks['equation_references_resolve']=set(re.findall(r'（(A\d+)）',text)).issubset(eqs)
    headtext=[''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in dx.xpath('//w:p[w:pPr/w:pStyle[@w:val="1" or @w:val="21"]]',namespaces=NS)]
    headids={x.split(' ')[0] for x in headtext}
    checks['section_references_resolve']=set(re.findall(r'A\.\d+(?:\.\d+)?',text)).issubset(headids)
    chars={'before':len(''.join(sx.xpath('//w:t/text()',namespaces=NS))),'after':len(''.join(dx.xpath('//w:t/text()',namespaces=NS)))}
with pdfplumber.open(render/'document.pdf') as pdf:
    texts=[p.extract_text() or '' for p in pdf.pages]
    checks['all_pages_searchable']=all(len(t)>100 for t in texts)
    checks['no_render_replacement_glyph']=all('\ufffd' not in t for t in texts)
    checks['all_equations_rendered']=all(re.search(r'\(\s*A'+str(i)+r'\s*\)','\n'.join(texts)) for i in range(1,18))
    pages=len(pdf.pages)
result={'checks':checks,'all_passed':all(checks.values()),'pages':pages,'text_characters':chars,'source_sha256':digest(SOURCE),'output_sha256':digest(TARGET),'render':str(render),'method_scope':'Language edits; no data estimation or model changes.'}
(ROOT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(0 if result['all_passed'] else 1)
