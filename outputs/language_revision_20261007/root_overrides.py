from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
records={r['id']:r for r in json.loads((ROOT/'current_paragraphs.json').read_text(encoding='utf-8'))}
all_edits={e['id']:e for name in ['first_half_edits.json','second_half_edits.json'] for e in json.loads((ROOT/name).read_text(encoding='utf-8'))}
overrides=[]
def modify(key,old,new):
    after=all_edits[key]['after']
    assert old in after,(key,old)
    all_edits[key]['after']=after.replace(old,new)

all_edits['P003']['after']='本研究考察外资准入规则放松如何影响企业是否由外国控制，以及企业进入和生产，并利用跨国生产模型测算相应的等价成本变化。研究先按经济活动整理各年的准入规则，再利用实际改革估计企业行为和生产变化，最后按照与模型一致的统计口径构造成本冲击。基准分析选择改革前已有可观测外资生产的活动，研究有限准入限制放松的影响。'
modify('P035','两种模型的结果一致只能说明匹配较为稳定，准确性仍须与人工标准比较。','两种模型结果的一致程度用于衡量编码稳定性，准确性仍须通过与人工标注比较来判断。')
modify('P058','且活动间干扰符合预设边界的条件下','且活动间相互影响符合既定识别假设的条件下')
modify('P064','并相应收敛结论','并相应降低结论的确定性')
modify('P070','交互效应和非线性剂量响应的解释限于实际改革所覆盖的范围。','交互效应及限制强度与结果之间的非线性关系，只在实际改革覆盖的范围内解释。')
modify('P084','权重依据目标协方差或统一量纲设定','权重根据各目标指标的协方差或统一后的量纲确定')
modify('P084','也可事先确定哪些矩用于联合匹配、哪些矩用于检验。','也可事先确定哪些统计指标用于联合拟合，哪些用于检验。')
modify('P085','据此计算部门平均等价成本和相应的一般均衡情景。','据此计算部门平均等价成本，并在上述假设下求解一般均衡。')
modify('P094','基准模型根据反演结果，调整受改革部门中外国企业在华生产的部门平均等价成本楔子。','根据反演结果，基准模型调整受改革部门中外国企业在华生产的平均成本楔子。')
modify('P112','即使其他规格能够得到结果，原规格存在的问题仍如实报告。','不同规格的成功与失败情况一并列示，以便比较。')
for key in ['P003','P035','P058','P064','P070','P084','P085','P094','P112']:
    overrides.append({'id':key,'before':records[key]['text'],'after':all_edits[key]['after'],'reason':'主代理复核后进一步减少模板句、连续名词和生硬转折，保留原意及限定'})
(ROOT/'root_overrides.json').write_text(json.dumps(overrides,ensure_ascii=False,indent=2),encoding='utf-8')
print('ROOT_FINAL_LANGUAGE_REVISIONS',len(overrides))
