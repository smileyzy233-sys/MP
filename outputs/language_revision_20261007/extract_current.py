from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json, hashlib, shutil, re

ROOT=Path(__file__).resolve().parent
SOURCE=Path(r'A:\桌面\study\企业微观层面_新方案.docx')
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
records=[]
style_names={}
def record(p,key):
    style=p.find('w:pPr/w:pStyle',NS)
    style=style.get('{'+NS['w']+'}val') if style is not None else 'Normal'
    pieces=[];protected=[]
    for child in p:
        tag=etree.QName(child).localname
        if tag=='pPr':continue
        if tag=='oMath':
            token=f'⟦M{len(protected)+1:03d}⟧'
            protected.append({'token':token,'kind':'math','text':''.join(child.xpath('.//m:t/text()',namespaces=NS))})
            pieces.append(token)
        elif tag=='r':
            text=''.join(child.xpath('.//w:t/text()',namespaces=NS))
            fonts=child.find('w:rPr/w:rFonts',NS)
            mono=fonts is not None and 'Consolas' in list(fonts.attrib.values())
            if mono and text:
                token=f'⟦K{len(protected)+1:03d}⟧'
                protected.append({'token':token,'kind':'formatted_identifier','text':text})
                pieces.append(token)
            else:pieces.append(text)
        else:raise RuntimeError('Unexpected paragraph element '+tag)
    text=''.join(pieces)
    plain=''.join(p.xpath('.//w:t/text() | .//m:t/text()',namespaces=NS))
    name=style_names.get(style,style).lower()
    kind='equation' if style=='Equation' else 'heading' if name.startswith('heading') or name=='title' else 'caption' if name=='caption' else 'reference' if style=='Reference' else 'body'
    if key.startswith('T'):kind='table'
    records.append({'id':key,'style':style,'kind':kind,'text':text,'plain':plain,'protected':protected})

with ZipFile(SOURCE) as z:
    styles=etree.fromstring(z.read('word/styles.xml'))
    for e in styles.findall('w:style',NS):
        name=e.find('w:name',NS)
        if name is not None:style_names[e.get('{'+NS['w']+'}styleId')]=name.get('{'+NS['w']+'}val')
    root=etree.fromstring(z.read('word/document.xml'))
    for i,e in enumerate(root.find('w:body',NS),1):
        tag=etree.QName(e).localname
        if tag=='p':record(e,f'P{i:03d}')
        elif tag=='tbl':
            for ri,row in enumerate(e.findall('w:tr',NS)):
                for ci,cell in enumerate(row.findall('w:tc',NS)):
                    for pi,p in enumerate(cell.findall('w:p',NS)):record(p,f'T{i:03d}R{ri:02d}C{ci:02d}P{pi:02d}')
    math_hashes=[hashlib.sha256(etree.tostring(e,method='c14n')).hexdigest() for e in root.xpath('//m:oMath',namespaces=NS)]
    package_hashes={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n!='word/document.xml'}
meta={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'body_blocks':len(root.find('w:body',NS)),'native_math_count':len(math_hashes),'math_hashes':math_hashes,'unchanged_package_hashes':package_hashes,'source_bytes':SOURCE.stat().st_size}
(ROOT/'current_paragraphs.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'source_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
snapshot=ROOT/'source_before.docx'
if snapshot.exists():
    assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==meta['sha256'],'Preserve changed snapshot'
else:shutil.copyfile(SOURCE,snapshot)
ledger='''# 术语与修改边界\n\n本轮为中文研究方案全文语言修订，保留当前Word的标题、章节、公式、表格结构、变量和研究设计。以当前Word为唯一权威来源，不从旧Markdown重建。\n\n保留经济活动、政策暴露、外资生产份额、条件均值、PPML、ITT、成本楔子、等价成本、局部均衡PE、一般均衡GE等术语；对难理解的连续名词改用说明其实际含义的完整句子，不以换同义词为润色。等价成本仍指在模型中产生对应生产变化的成本调整，不能改成直接观测的真实制度成本。\n\n原生数学和格式化字段用保护标记，修改前后顺序及内容必须一致。不得增加数据事实、删去识别假设或把条件结论升级为因果结论。文献不变。表格文字可润色，数值与CF设定不变。\n'''
(ROOT/'terminology_and_scope.md').write_text(ledger,encoding='utf-8')
print(json.dumps({'source_sha256':meta['sha256'],'records':len(records),'math':len(math_hashes),'body':[x['id'] for x in records if x['kind']=='body' and x['text']],'styles':sorted(set(x['style'] for x in records))},ensure_ascii=False))
