from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import sys
sys.stdout.reconfigure(encoding='utf-8')
p=Path(r'A:\桌面\study\企业微观层面_v4.1.docx')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(p) as z:
 r=E.fromstring(z.read('word/document.xml'))
 print('section',E.tostring(r.find('.//{'+ns['w']+'}sectPr'),encoding='unicode'))
 pars=r.xpath('//w:body//w:p',namespaces=ns)
 for i,p in enumerate(pars):
  if p.xpath('.//w:br[@w:type="page"]',namespaces=ns) or i in [0,1,11,12,40,41,43,58,77,83,88]:
   print(i,E.tostring(p,encoding='unicode')[:1800])
 for part in ['word/styles.xml','word/document.xml']:
  root=E.fromstring(z.read(part))
  print(part,{k:len(root.xpath('//w:'+k,namespaces=ns)) for k in ['keepNext','keepLines','pageBreakBefore']})
