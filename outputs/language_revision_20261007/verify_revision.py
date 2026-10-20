from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from docx import Document
import json,hashlib,re
import pdfplumber

ROOT=Path(__file__).resolve().parent
meta=json.loads((ROOT/'result.json').read_text(encoding='utf-8'))
source=Path(meta['source']);output=Path(meta['output'])
manifest=json.loads((ROOT/'source_manifest.json').read_text(encoding='utf-8'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['sha256']
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
with ZipFile(source) as a, ZipFile(output) as b:
    assert b.testzip() is None
    r1=etree.fromstring(a.read('word/document.xml'));r2=etree.fromstring(b.read('word/document.xml'))
    for tag in ['oMath']:
        q='//m:'+tag
        assert [etree.tostring(x,method='c14n') for x in r1.xpath(q,namespaces=ns)]==[etree.tostring(x,method='c14n') for x in r2.xpath(q,namespaces=ns)]
    for tag in ['pPr','tblPr','tblGrid','trPr','tcPr','sectPr']:
        q='//w:'+tag
        assert [etree.tostring(x,method='c14n') for x in r1.xpath(q,namespaces=ns)]==[etree.tostring(x,method='c14n') for x in r2.xpath(q,namespaces=ns)],('Formatting changed',tag)
    for name,h in manifest['unchanged_package_hashes'].items():assert hashlib.sha256(b.read(name)).hexdigest()==h
    assert len(r1.xpath('//w:lastRenderedPageBreak',namespaces=ns))==len(r2.xpath('//w:lastRenderedPageBreak',namespaces=ns))
    prose=''.join(r2.xpath('//w:t/text()',namespaces=ns))
    assert '⟦' not in prose and '\ufffd' not in prose
    assert '不用于恢复完整的历史制度成本存量' not in prose
    assert len(r2.xpath('//w:tbl',namespaces=ns))==5
doc=Document(output)
assert len(doc.tables)==5
pages=[]
with pdfplumber.open(ROOT/'render_after/document.pdf') as pdf:
    for i,p in enumerate(pdf.pages,1):
        chars=[c for c in p.chars if c['text'].strip()]
        text=p.extract_text() or ''
        bad=[c for c in chars if c['x0']<35 or c['x1']>p.width-25 or c['top']<25 or c['bottom']>p.height-15]
        assert chars and not bad,(i,bad[:5])
        assert '\ufffd' not in text
        pages.append({'page':i,'chars':len(text),'min_x':min(c['x0'] for c in chars),'max_x':max(c['x1'] for c in chars),'min_y':min(c['top'] for c in chars),'max_y':max(c['bottom'] for c in chars),'text':text})
render=json.loads((ROOT/'render_after/render_meta.json').read_text(encoding='utf-8-sig'))
assert len(pages)==render['pages']
assert len(list((ROOT/'render_after').glob('page-*.png')))==len(pages)
assert hashlib.sha256(output.read_bytes()).hexdigest()==meta['output_sha256'],'Render changed Word'
summary={**meta,'pages':len(pages),'source_unchanged':True,'formula_bytes_unchanged':True,'paragraph_and_table_formatting_unchanged':True,'document_opens':True,'pdf_text_and_bounds_pass':True,'visual_review_pending':True}
(ROOT/'verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'page_metrics.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in ['source_sha256','output_sha256']},ensure_ascii=False,indent=2))
print('PAGE_SUMMARY',[(p['page'],p['chars']) for p in pages])
