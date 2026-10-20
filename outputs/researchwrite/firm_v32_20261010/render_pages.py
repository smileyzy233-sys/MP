from pathlib import Path
import pypdfium2 as pdfium,pdfplumber,json,sys
from PIL import Image,ImageOps,ImageDraw
folder=Path(sys.argv[1]);pdf=pdfium.PdfDocument(folder/'document.pdf');parsed=pdfplumber.open(folder/'document.pdf');meta=[]
for i,page in enumerate(pdf):
    page.render(scale=1.6).to_pil().save(folder/f'page-{i+1}.png')
    text=parsed.pages[i].extract_text() or '';(folder/f'page-{i+1}.txt').write_text(text,encoding='utf-8')
    spans=parsed.pages[i].chars
    meta.append({'page':i+1,'chars':len(text),'min_x':min(s['x0'] for s in spans),'max_x':max(s['x1'] for s in spans),'min_y':min(s['top'] for s in spans),'max_y':max(s['bottom'] for s in spans),'last_text':text[-140:]})
(folder/'page_metrics.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
thumbs=[]
for i in range(len(pdf)):
    im=Image.open(folder/f'page-{i+1}.png').convert('RGB');im.thumbnail((306,396));tile=Image.new('RGB',(326,424),'#d7d7d7');tile.paste(im,((326-im.width)//2,7));ImageDraw.Draw(tile).text((10,404),f'Page {i+1}',fill='black');thumbs.append(tile)
for start in range(0,len(thumbs),9):
    rows=(len(thumbs[start:start+9])+2)//3;sheet=Image.new('RGB',(978,424*rows),'#c8c8c8')
    for j,im in enumerate(thumbs[start:start+9]):sheet.paste(im,((j%3)*326,(j//3)*424))
    sheet.save(folder/f'contact-{start//9+1}.png')
print(json.dumps({'pages':len(pdf),'metrics':meta},ensure_ascii=False))
