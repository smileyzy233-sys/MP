from pathlib import Path
import sys, json, hashlib
import win32com.client
import pymupdf
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
path=Path(sys.argv[1]);folder=BASE/sys.argv[2];folder.mkdir(parents=True,exist_ok=True)
before=hashlib.sha256(path.read_bytes()).hexdigest()
app=win32com.client.DispatchEx('Word.Application');app.Visible=False;app.DisplayAlerts=0
try:
    doc=app.Documents.Open(str(path),False,True,False)
    doc.Fields.Update()
    for section in doc.Sections:
        for footer in section.Footers:footer.Range.Fields.Update()
    doc.Repaginate()
    record={'opened':str(path),'read_only':bool(doc.ReadOnly),'pages':doc.ComputeStatistics(2),'math_objects':doc.OMaths.Count,'tables':doc.Tables.Count,'footnotes':doc.Footnotes.Count,'endnotes':doc.Endnotes.Count,'fields':doc.Fields.Count}
    heads=[]
    for p in doc.Paragraphs:
        t=p.Range.Text.strip()
        if t.startswith('A.') or t.startswith('表A') or t.startswith('图A') or t=='参考文献与资料说明':
            heads.append({'text':t,'page':p.Range.Information(3),'y':p.Range.Information(6)})
    record['headings']=heads
    doc.ExportAsFixedFormat(str(folder/'qa.pdf'),17)
    doc.Close(False)
finally:app.Quit()
assert hashlib.sha256(path.read_bytes()).hexdigest()==before,'Read-only Word open modified file'
pdf=pymupdf.open(folder/'qa.pdf')
texts=[]
for i,p in enumerate(pdf):
    p.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6)).save(folder/f'page-{i+1:02}.png')
    texts.append({'page':i+1,'text':p.get_text(),'blocks':[{'bbox':list(b[:4]),'text':b[4]} for b in p.get_text('blocks') if b[6]==0]})
record['render_pages']=len(pdf);record['sha256']=before
(folder/'word_open.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
(folder/'page_text.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['pages','math_objects','tables','footnotes','sha256']},ensure_ascii=False))
