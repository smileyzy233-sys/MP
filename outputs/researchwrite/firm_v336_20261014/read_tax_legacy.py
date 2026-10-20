from pathlib import Path
import json
import win32com.client
import pymupdf
import pandas as pd

ROOT=Path(r'A:\桌面\study\税收调查数据')
OUT=Path(r'A:\桌面\study\outputs\researchwrite\firm_v336_20261014')
word=win32com.client.DispatchEx('Word.Application')
word.Visible=False
word.DisplayAlerts=0
try:
    for path in sorted((ROOT/'税调变量说明07-16').glob('*.doc')):
        doc=word.Documents.Open(str(path),ReadOnly=True,AddToRecentFiles=False)
        try: (OUT/(path.stem+'.txt')).write_text(doc.Content.Text,encoding='utf-8')
        finally: doc.Close(SaveChanges=0)
finally:
    word.Quit(SaveChanges=0)
for filename,pages,prefix in [
    ('2007年度全国企业税收调查表填报说明.pdf',[1,2,47,50],'tax2007'),
    ('2011年度全国税收调查表填表说明.pdf',[0,12],'tax2011')]:
    doc=pymupdf.open(ROOT/'税调变量说明07-16'/filename)
    for i in pages: doc[i].get_pixmap(matrix=pymupdf.Matrix(1,1)).save(OUT/f'{prefix}p{i+1}.png')
expected={2012:['f437','f311','f312','f370','f388','f389','f435','f436'],2013:['f440','f314','f315','f373','f391','f392','f438','f439'],2014:['f393','f269','f270','f328','f346','f347','f391','f392'],2015:['f393','f269','f270','f328','f346','f347','f391','f392'],2016:['f403','f272','f273','f331','f349','f350','f399','f400']}
for yr,cols in expected.items():
    with pd.read_stata(ROOT/f'{yr}sd.dta',iterator=True) as r:
        labels=r.variable_labels()
        print(yr,{k:labels.get(k,'NOT PRESENT') for k in cols})
print('done')
