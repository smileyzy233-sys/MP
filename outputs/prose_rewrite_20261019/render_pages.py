from pathlib import Path
import sys,json
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')
folder=Path(sys.argv[1]);pdf=pymupdf.open(folder/'qa.pdf')
texts=[]
for i,p in enumerate(pdf):
 p.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6)).save(folder/f'page-{i+1:02}.png')
 texts.append({'page':i+1,'text':p.get_text(),'blocks':[{'bbox':list(b[:4]),'text':b[4]} for b in p.get_text('blocks') if b[6]==0]})
(folder/'page_text.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2),encoding='utf-8')
print('rendered pages',len(pdf))
