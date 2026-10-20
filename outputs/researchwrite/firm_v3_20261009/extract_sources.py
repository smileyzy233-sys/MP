from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import hashlib, json
ROOT=Path(__file__).resolve().parent
REF=Path(r'A:\桌面\制度性开放\审稿意见\手动改和写')
paths={'current':Path(r'A:\桌面\study\企业微观层面_新方案_框架重写版.docx'),'old':Path(r'A:\桌面\study\旧版方案\企业微观层面.docx'),'reply_final':REF/'审稿人回复.docx','reply_original':REF/'对审稿报告一的回复(2)(1).docx','revision_instructions':REF/'修改意见.docx','flow_reference':REF/'流程图.pptx'}
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
manifest=[]
for label,path in paths.items():
    with ZipFile(path) as z:
        if path.suffix=='.docx':
            root=etree.fromstring(z.read('word/document.xml'))
            rows=[]
            for i,p in enumerate(root.xpath('//w:body//w:p',namespaces=NS)):
                text=''.join(p.xpath('.//w:t[not(ancestor::w:del)]/text()|.//m:t[not(ancestor::w:del)]/text()',namespaces=NS))
                if text.strip():rows.append(f'[{i:03d}] '+text)
            if 'word/comments.xml' in z.namelist():
                cr=etree.fromstring(z.read('word/comments.xml'))
                rows+=['\nCOMMENTS']+[''.join(c.xpath('.//w:t/text()',namespaces=NS)) for c in cr]
            metrics={'paragraphs':len(rows),'math':len(root.xpath('//m:oMath',namespaces=NS)),'tables':len(root.xpath('//w:tbl',namespaces=NS)),'sections':len(root.xpath('//w:sectPr',namespaces=NS))}
        else:
            rows=[]
            for part in sorted(z.namelist()):
                if part.startswith('ppt/slides/slide') and part.endswith('.xml'):
                    root=etree.fromstring(z.read(part));rows.append(part+'\n'+'\n'.join(root.xpath('//a:t/text()',namespaces=NS)))
            metrics={}
    (ROOT/'sources'/f'{label}.txt').write_text('\n'.join(rows),encoding='utf-8')
    manifest.append({'label':label,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,**metrics})
(ROOT/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
