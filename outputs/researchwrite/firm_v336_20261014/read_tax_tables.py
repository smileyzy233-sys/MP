from pathlib import Path
import json
import win32com.client
import pandas as pd

ROOT=Path(r'A:\桌面\study\税收调查数据')
OUT=Path(r'A:\桌面\study\outputs\researchwrite\firm_v336_20261014')
excel=win32com.client.DispatchEx('Excel.Application')
excel.Visible=False
excel.DisplayAlerts=False
result={}
try:
    for path in sorted((ROOT/'税调变量说明07-16').glob('*.xls')):
        book=excel.Workbooks.Open(str(path),UpdateLinks=0,ReadOnly=True)
        try:
            rows=[]
            for sheet in book.Worksheets:
                for i,row in enumerate(sheet.UsedRange.Value,1):
                    text=' | '.join('' if x is None else str(x) for x in row)
                    if any(x in text for x in ['总产值','营业收入','主营业务收入','实收资本','增加固定资产','职工人数','行业','国民经济','股本','外商资本','港澳台资本']):
                        rows.append({'sheet':sheet.Name,'excel_row':i,'text':text})
            result[path.name]=rows
        finally:
            book.Close(SaveChanges=False)
finally:
    excel.Quit()
(OUT/'tax_original_xls_rows.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
allf=[]
for year in range(2017,2021):
    with pd.read_stata(ROOT/f'{year}sd.dta',iterator=True) as reader:
        frame=reader.read(nrows=5000,columns=['year','行业代码','企业总产值','营业收入','纳税人登记注册类型代码'])
    allf.append(frame)
    print(year,'year values first5000',frame['year'].value_counts(dropna=False).to_dict(),'Q nonmissing',int(frame['企业总产值'].notna().sum()),'R nonmissing',int(frame['营业收入'].notna().sum()),'Q first5',frame['企业总产值'].head().tolist())
print('industry first5000 identical across files',all(allf[0]['行业代码'].equals(f['行业代码']) for f in allf[1:]))
print('Q first5000 identical across files',all(allf[0]['企业总产值'].equals(f['企业总产值']) for f in allf[1:]))

