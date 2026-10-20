from pathlib import Path
import json
import pandas as pd
import pymupdf

ROOT=Path(r'A:\桌面\study\税收调查数据')
OUT=Path(r'A:\桌面\study\outputs\researchwrite\firm_v336_20261014')
report={}
for year in range(2007,2021):
    path=ROOT/f'{year}sd.dta'
    with pd.read_stata(path,iterator=True,convert_categoricals=False) as reader:
        labels=reader.variable_labels()
        cols=[k for k,v in labels.items() if k in ['industry','industry1','industry2','hylb','hydm','hy_dm','行业代码']]
        frame=reader.read(nrows=5000,columns=cols)
        report[str(year)]={
            'path':str(path),'file_size':path.stat().st_size,
            'data_label':reader._data_label,'format':reader._format_version,
            'saved_timestamp':reader._time_stamp,
            'variable_labels':labels,
            'industry_first5000_nonrandom':{k:{'dtype':str(frame[k].dtype),'nonmissing':int(frame[k].notna().sum()),'unique':[str(x) for x in frame[k].unique()][:100]} for k in cols},
        }
with pd.read_stata(ROOT/'税调基本信息07_20.dta',iterator=True) as reader:
    report['basic_info']={'variable_labels':reader.variable_labels(),'data_label':reader._data_label}
(OUT/'tax_metadata_readonly.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for yr in report:
    if yr=='basic_info': continue
    data=report[yr]
    labels=data['variable_labels']
    match={k:v for k,v in labels.items() if (any(x in (k+' '+v) for x in ['行业','industry','hylb','hydm','hy_dm','总产值','营业收入','主营业务收入','实收资本','股本','固定资产','职工','外商资本','港澳台资本','控制','成立','开业','调查方式','权重']) or k in ['qt_zcz','m310'])}
    print(yr, 'vars',len(labels), 'industry:',data['industry_first5000_nonrandom'])
    if int(yr)>=2017: print(match)

