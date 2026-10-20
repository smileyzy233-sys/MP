from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
import json, hashlib, re, copy, sys

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r'A:\桌面\study\企业微观层面_v3.docx')
TARGET = SOURCE.with_name('企业微观层面_v3_语言润色版.docx')
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main', 'm':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W = '{'+NS['w']+'}'
def sha(b): return hashlib.sha256(b).hexdigest()
def template(p):
    text = ''; objects = []
    for child in p:
        if child.tag == W+'pPr': continue
        if child.tag == W+'r' and all(c.tag in (W+'rPr', W+'t') for c in child):
            text += ''.join(child.xpath('./w:t/text()',namespaces=NS))
        else:
            text += '{{'+str(len(objects))+'}}'
            objects.append(child)
    return text, objects

data = SOURCE.read_bytes()
with ZipFile(SOURCE) as z:
    parts = {i.filename: z.read(i.filename) for i in z.infolist()}
trees = {n: etree.fromstring(parts[n]) for n in ['word/document.xml','word/footnotes.xml']}
records = []; lookup = {}
for part, tree in trees.items():
    prefix = 'p' if part == 'word/document.xml' else 'f'
    for i,p in enumerate(tree.xpath('//w:p',namespaces=NS)):
        text,objs = template(p); key = prefix+str(i).zfill(3)
        record = {'id':key, 'style':p.xpath('./w:pPr/w:pStyle/@w:val',namespaces=NS), 'text':text,
                  'objects':[''.join(o.xpath('.//m:t/text()|.//w:t/text()',namespaces=NS)) or etree.QName(o).localname for o in objs]}
        records.append(record);lookup[key]=(part,p,text,objs)

if len(sys.argv)==1 or sys.argv[1]=='inspect':
    (ROOT/'source_snapshot.json').write_text(json.dumps({'source':str(SOURCE),'sha256':sha(data),'records':records},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(records,ensure_ascii=False,indent=2));sys.exit()

snapshot=json.loads((ROOT/'source_snapshot.json').read_text(encoding='utf-8'))
assert sha(data)==snapshot['sha256'],'Source changed since inspection'
edits=json.loads((ROOT/'replacements.json').read_text(encoding='utf-8'))
changes=[];changed_parts=set()
for key,new in edits.items():
    part,p,old,objects=lookup[key]
    assert new!=old,key+' unchanged edit'
    assert re.findall(r'\{\{\d+\}\}',old)==re.findall(r'\{\{\d+\}\}',new),key+' object sequence changed'
    fmt=None
    for r in p.findall(W+'r'):
        if r.find(W+'t') is not None:
            rp=r.find(W+'rPr');fmt=copy.deepcopy(rp) if rp is not None else None;break
    for c in list(p):
        if c.tag!=W+'pPr':p.remove(c)
    for token in re.split(r'(\{\{\d+\}\})',new):
        if not token:continue
        if re.fullmatch(r'\{\{\d+\}\}',token):p.append(copy.deepcopy(objects[int(token[2:-2])]))
        else:
            r=etree.SubElement(p,W+'r')
            if fmt is not None:r.append(copy.deepcopy(fmt))
            t=etree.SubElement(r,W+'t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=token
    changes.append({'id':key,'before':old,'after':new});changed_parts.add(part)

flow_edits={
    '固定企业改革前业务，逐版判断政策待遇':'固定企业改革前业务，逐版判断适用规则',
    '包含新设企业的完整行业生产':'全行业生产，包括新设企业产出',
    '核实原有企业产出在部门中的覆盖范围':'明确原有企业样本覆盖哪些部门产出',
    '核对生产覆盖、部门归属及模型比较范围':'核查产出覆盖范围、部门归属及模型比较口径',
    '有完整生产依据或明确补充假设时，形成部门目标':'掌握完整部门产出或说明补充假设后，构造部门目标'
}
for before,after in flow_edits.items():
    nodes=trees['word/document.xml'].xpath('//w:t[text()=$txt]',namespaces=NS,txt=before)
    assert len(nodes)==1,before
    nodes[0].text=after

for part in changed_parts:parts[part]=etree.tostring(trees[part],xml_declaration=True,encoding='UTF-8',standalone=True)
old_meta=ROOT/'edit_meta.json'
if TARGET.exists():
    assert old_meta.exists() and sha(TARGET.read_bytes())==json.loads(old_meta.read_text(encoding='utf-8'))['sha256'],'Output changed externally'
with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
    for name,body in parts.items():z.writestr(name,body)
meta={'source':str(SOURCE),'source_sha256':sha(data),'output':str(TARGET),'sha256':sha(TARGET.read_bytes()),'changed_paragraphs':len(changes),'flow_text_edits':flow_edits,'changed_parts':sorted(changed_parts),'changes':changes}
old_meta.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in meta.items() if k!='changes'},ensure_ascii=False,indent=2))
