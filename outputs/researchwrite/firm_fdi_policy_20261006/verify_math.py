from pathlib import Path
import importlib.util, json
from lxml import etree

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('planbuilder',ROOT/'build_docx.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
ns={'x':builder.MS}
tests={
 'sum_then_foreign_control':r'\sum_fD^F_{ft}Q_{furt}',
 'cost_sup_and_sub':r'd_{Cmj}^{MP,\mathrm{cf}}',
 'event_indicator':r'\sum_{h\ne-1}\beta^q_{e,h}T_{ur,e}\mathbf1(t-t_e=h)',
 'hat_derivative':r'\widehat\xi_{Cmj}=\exp(-\delta_{mj})',
 'cases':r'\begin{cases}\exp(-\widehat\delta_{mj}),&i=C,\\1,&\text{其他关系},\end{cases}',
}
records={}
for name,tex in tests.items():
    ml=builder.TexParser(tex,True).parse()
    om=builder.math(tex,True)
    records[name]={'mathml':etree.tostring(ml,encoding='unicode'),'native_text':''.join(om.xpath('.//m:t/text()',namespaces=builder.NS))}
    if name=='sum_then_foreign_control':
        under=ml.xpath('.//x:munder[x:mo="∑"]',namespaces=ns)
        assert len(under)==1
        assert ''.join(under[0][1].itertext())=='f'
        assert len(ml.xpath('.//x:msubsup[x:mi="D"]',namespaces=ns))==1
        assert len(ml.xpath('.//x:msub[x:mi="Q"]',namespaces=ns))==1
    if name=='cases':assert len(ml.xpath('.//x:mtr',namespaces=ns))==2
(ROOT/'qa_math.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('NATIVE_MATH_CHECKS_PASS',len(records))
