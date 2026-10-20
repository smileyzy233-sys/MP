from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parent
path=ROOT/'proposal_v3.md';text=path.read_text(encoding='utf-8');before=text
review=(ROOT/'qa/prose_review.md').read_text(encoding='utf-8')
changes=[]
for match in re.finditer(r'^### (\d+)\. .*?\n\n原段：\n\n(.*?)\n\n建议改为：\n\n(.*?)\n\n理由：',review,re.M|re.S):
    idx=int(match[1]);old,new=match[2].strip(),match[3].strip()
    if idx in [3,10,13,14]:continue
    assert text.count(old)==1,(idx,text.count(old))
    text=text.replace(old,new);changes.append({'review_item':idx,'old':old,'new':new})
replacements={
    'A.1.3 政策文本抽取与人工审计':'A.1.3 政策文本抽取与人工核验',
    'A.3.3 总体外资控制企业生产份额的构造':'A.3.3 外国控制企业生产份额的构造',
    '观测算子$O$将模型结果按实证所用部门、样本范围、时间和比较方式计算为同一组指标。':'以$O$表示按实证口径计算模型结果的函数，统一部门、样本范围、时间及比较方式。',
    '上述比较保持企业业务描述不变，逐版判断适用规则，无需连接前后政策单元。改革后的业务调整作为企业反应研究，不据此重新划分原有处理组。':'改革后的业务调整作为企业反应研究，不据此重新划分原有处理组。',
    '由此形成原有企业的政策暴露，供A.3识别其所有权和生产反应；改革后新设企业的生产另由完整行业统计纳入。':'上述暴露用于识别A.3中的原有企业反应。',
    '四位行业年度效应适用于行业内部存在政策待遇差异的事件。全国性改革完整覆盖一个小类时，该效应会吸收政策变化':'四位行业×年份固定效应适用于行业内部存在政策待遇差异的事件。全国性改革完整覆盖一个小类时，该组固定效应会吸收政策变化',
    'PE成本进入GE求解后，报告均衡反馈带来的生产变化；':'PE成本进入GE求解后，报告生产结果及其与PE目标的差异；',
    '附加生产假设下得到的均衡结果，连同这些假设一并报告。':'需要补充生产假设的情景，应同时说明所用假设。',
    '实证稳健性围绕A.3.1—A.3.2的识别条件展开，比较不同事件窗口、对照范围和同期政策处理。':'实证稳健性围绕A.3.1—A.3.2的识别条件展开，检验公告前趋势，并比较不同事件窗口、对照范围和同期政策处理。'
}
for old,new in replacements.items():
    assert old in text,old;text=text.replace(old,new)
text=text.replace('处理分组按改革前业务、地区及资格确定，并在事件窗口内固定。','处理分组按改革前业务、地区及资格确定，并在事件窗口内固定；有真实业务权重时，再考察改革覆盖比重的差异。')
text=text.replace('$c_{fe0}$和$r_{fe0}$分别为改革前行业和地区；','$c_{fe0}$和$r_{fe0}$按已核实的改革前主业及主要生产地区确定，多业务、多地区企业无法明确归属时单列分析；')
old='本节根据改革带来的部门生产变化，计算跨国生产模型中的成本需要调整多少。先将经验生产目标统一到模型部门和计价口径，再改变外国企业在华生产的成本，使模型产生与目标相符的生产变化。以$\\delta_j$表示部门$j$成本的对数相对变化，负值表示下降。该结果回答所研究改革对应多大的成本调整，基准成本还可能包含准入政策之外的因素。'
new='本节将改革带来的生产变化统一到模型部门和计价口径，调整外国企业在华生产成本，使模型结果与估计目标相符。以$\\delta_j$表示成本的对数相对变化，负值表示下降。它衡量改革前后成本改变多少，基准成本另由模型数据和校准确定。\n\n每次改革事先确定与模型均衡比较相符的观察期限，以所选年份有改革和无改革的预测份额之差构成$\\widehat{\\boldsymbol\\mu}$。份额以0至1计量，换为百分点时乘以100。需要补充预测集合之外的产出时，先在完整部门范围重算两种情景的份额，再形成目标。以下省略事件及比较期下标，分别反演各次改革的成本变化。'
assert old in text;text=text.replace(old,new)
# Preserve empirical scope statement instead of an unexplained numerical extrapolation.
text=text.replace('企业、固定企业组和行业面板各自形成预测集合，结果分别解释。','企业、固定企业组和行业面板各自形成预测集合，结果分别解释。')
path.write_text(text,encoding='utf-8')
log={'before_chinese':len(re.findall(r'[\u4e00-\u9fff]',before)),'after_chinese':len(re.findall(r'[\u4e00-\u9fff]',text)),'accepted_paragraph_reviews':[c['review_item'] for c in changes],'not_adopted':{'3':'保留用户要求的四版分类名称与非强制转换说明','10':'不能删掉刚补充的外国/国内两套预测方程','13':'保留明确的三种样本名称，避免指代不清','14':'采用另写的成本含义及事件/期限定义'},'method_repairs':['F/D分别估计','公告前h0参照','业务地区联合权重','明确μ为选定期限份额差且补全后重算','多业务固定效应主业/主地区来源','T与真实覆盖权重关系']}
(ROOT/'qa/integrated_revision.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(log,ensure_ascii=False,indent=2))
