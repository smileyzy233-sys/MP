from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
from collections import Counter
import json,re,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
SOURCE=Path(r'A:\桌面\study\企业微观层面_v4.1.docx')
TARGET=Path(r'A:\桌面\study\企业微观层面_v4.1_文字重写版.docx')
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}'
source_data=json.loads((BASE/'source.json').read_text(encoding='utf-8'))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_data['sha256']
with ZipFile(SOURCE) as z:parts={n:z.read(n) for n in z.namelist()}
root=E.fromstring(parts['word/document.xml'])
original=deepcopy(root)
pars=root.xpath('//w:body//w:p',namespaces=NS)
edits={}
for filename in ['edits_a1_a4.json','edits_main.json']:
 new=json.loads((BASE/filename).read_text(encoding='utf-8'))
 assert not(set(new)&set(edits)), 'overlapping edits'
 edits.update(new)

def format_run(p):
 for r in p.findall(W+'r'):
  if r.find(W+'t') is not None:
   rp=r.find(W+'rPr')
   return deepcopy(rp) if rp is not None else None

def add_text(p,text,rp):
 for n,chunk in enumerate(text.split('\n')):
  if n:
   r=E.SubElement(p,W+'r');E.SubElement(r,W+'br')
  if chunk:
   r=E.SubElement(p,W+'r')
   if rp is not None:r.append(deepcopy(rp))
   t=E.SubElement(r,W+'t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=chunk

for index,value in sorted(edits.items(),key=lambda item:int(item[0])):
 p=pars[int(index)]
 expected=[m['token'] for m in source_data['paragraphs'][int(index)]['math']]
 assert Counter(re.findall(r'\{\{M\d+\}\}',value))==Counter(expected),(index,'math tokens differ')
 math=[deepcopy(c) for c in p if c.tag.startswith('{'+NS['m']+'}')]
 rp=format_run(p);pp=deepcopy(p.find(W+'pPr'))
 segments=value.split('\n\n')
 previous=p
 for s,segment in enumerate(segments):
  dest=p if s==0 else E.Element(W+'p')
  for c in list(dest):dest.remove(c)
  if pp is not None:dest.append(deepcopy(pp))
  for chunk in re.split(r'(\{\{M\d+\}\})',segment):
   if re.fullmatch(r'\{\{M\d+\}\}',chunk):dest.append(deepcopy(math[int(chunk[3:-2])]))
   else:add_text(dest,chunk,rp)
  if s:
   previous.addnext(dest)
  previous=dest

# Keep the overview page and reference-page break; replace former layout-only breaks after rewriting.
for index in [20,58,83]:
 p=pars[index]
 if not ''.join(p.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS)).strip():
  p.getparent().remove(p)

# Ordinary page break places the A.6 heading with its text; pagination flags stay off.
pb=E.Element(W+'p')
pp=E.SubElement(pb,W+'pPr')
spacing=E.SubElement(pp,W+'spacing');spacing.set(W+'before','0');spacing.set(W+'after','0');spacing.set(W+'line','20');spacing.set(W+'lineRule','exact')
run=E.SubElement(pb,W+'r');rp=E.SubElement(run,W+'rPr');E.SubElement(rp,W+'sz').set(W+'val','2')
E.SubElement(run,W+'br').set(W+'type','page')
pars[53].addprevious(pb)

# Explicitly disable paragraph pagination flags in every relevant part and inherited style.
for n,content in list(parts.items()):
 if not n.startswith('word/') or not n.endswith('.xml'):continue
 tree=root if n=='word/document.xml' else E.fromstring(content)
 changed=n=='word/document.xml'
 for tag in ['keepNext','keepLines','pageBreakBefore']:
  for elem in tree.xpath('//w:'+tag,namespaces=NS):
   elem.set(W+'val','0');changed=True
 if changed:parts[n]=E.tostring(tree,encoding='UTF-8',xml_declaration=True,standalone=True)

def fingerprint(node):
 # Compare semantic OOXML structure without irrelevant namespace serialization differences.
 return (node.tag,tuple(sorted(node.attrib.items())),node.text,tuple(fingerprint(c) for c in node))
before_math=original.xpath('//m:oMath',namespaces=NS)
after_math=root.xpath('//m:oMath',namespaces=NS)
assert [fingerprint(m) for m in before_math]==[fingerprint(m) for m in after_math]
assert len(root.xpath('//w:tbl',namespaces=NS))==3
for t in [1,2]:
 assert fingerprint(original.xpath('//w:tbl',namespaces=NS)[t])==fingerprint(root.xpath('//w:tbl',namespaces=NS)[t])
assert fingerprint(pars[0])==fingerprint(original.xpath('//w:body//w:p',namespaces=NS)[0])
for p in root.xpath('//w:p',namespaces=NS):
 assert '{{M' not in ''.join(p.xpath('.//w:t/text()',namespaces=NS))
with ZipFile(TARGET,'w',ZIP_DEFLATED) as z:
 for n,content in parts.items():z.writestr(n,content)
newtext='\n'.join(''.join(p.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS)) for p in root.xpath('//w:body//w:p',namespaces=NS))
(BASE/'rewritten.txt').write_text(newtext,encoding='utf-8')
stats={'source':str(SOURCE),'source_sha256':source_data['sha256'],'output':str(TARGET),'output_sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'revised_paragraphs':len(edits),'math_objects':len(after_math),'numbered_formulas':6,'tables':3,'source_title_preserved':True,'score_table_and_example_unchanged':True,'non_document_parts_unchanged':[n for n in parts if n!='word/document.xml' and parts[n]==ZipFile(SOURCE).read(n)]}
(BASE/'build_meta.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in stats.items() if k!='non_document_parts_unchanged'},ensure_ascii=False,indent=2))
