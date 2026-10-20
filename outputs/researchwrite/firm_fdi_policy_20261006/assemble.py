from pathlib import Path
import re, json, hashlib

ROOT=Path(__file__).resolve().parent
front=(ROOT/'drafts/front_module.md').read_text(encoding='utf-8')
emp=(ROOT/'drafts/empirical_module.md').read_text(encoding='utf-8')
struct=(ROOT/'drafts/structural_module.md').read_text(encoding='utf-8')
end=(ROOT/'drafts/end_module.md').read_text(encoding='utf-8')

front=front.replace('$g$ 为改革事件','$e$ 为改革事件').replace('$policy\\_unit\\_id$','`policy_unit_id`').replace('$activity\\_id$','`activity_id`')
front=front.replace('活动 $u$ 在年份 $t$ 的限制向量定义为','活动 $u$ 在地区 $r$ 适用的年份 $t$ 限制向量定义为')
front=front.replace('z_{ut}','z_{urt}').replace('P_{ut}','P_{urt}').replace('E_{ut}','E_{urt}').replace('C_{ut}','C_{urt}').replace('O_{ut}','O_{urt}').replace('G_{ut}','G_{urt}').replace('R_{ut}','R_{urt}').replace('cap_{ut}','cap_{urt}')
front=front.replace('教师研究修订材料采用','《中国高水平制度型开放与全球产业链网络重塑》的修订材料采用')
front=front.replace('制度指标具有可追溯的政策内容。','制度指标具有可追溯的政策内容（研究修订材料，制度型开放测度部分）。')
emp=emp.replace(r'\(', '$').replace(r'\)', '$')
emp=re.sub(r'## A\.(\d+)\u3000',r'## A\1 ',emp)
emp=re.sub(r'### A\.\d+\.\d+\u3000','### ',emp)
emp=emp.replace('对 $g\\in\\{F,D\\}$','对 $q\\in\\{F,D\\}$').replace('Y^g','Y^q').replace('alpha^g','alpha^q').replace('lambda^g','lambda^q').replace('eta^g','eta^q').replace('beta^g','beta^q').replace('pi^g','pi^q')
emp=emp.replace('份额为：','份额分别定义。活动产出为：',1)
emp=emp.replace('F_{urt}=\\sum_fD^F_{ft}Q_{furt},\\qquad\nD_{urt}=\\sum_f(1-D^F_{ft})Q_{furt},\\qquad\nM^{\\mathrm{obs}}_{jt}=\\frac{\\sum_{u\\in j,r}F_{urt}}{\\sum_{u\\in j,r}(F_{urt}+D_{urt})}. \\tag{E1}',
 'F_{urt}=\\sum_fD^F_{ft}Q_{furt},\\qquad D_{urt}=\\sum_f(1-D^F_{ft})Q_{furt}. \\tag{E1a}\n$$\n\n部门观测份额为：\n\n$$\nM^{\\mathrm{obs}}_{jt}=\\frac{\\sum_{u\\in j,r}F_{urt}}{\\sum_{u\\in j,r}(F_{urt}+D_{urt})}. \\tag{E1b}')
emp=emp.replace('式（E1）是观测份额','式（E1b）是观测份额').replace('通过式（E1）覆盖','通过式（E1a）—（E1b）覆盖')
emp=emp.replace('\\widehat M^{v}_{jte}=\\frac{\\sum_{u\\in j,r}\\widehat F^{v}_{urte}}{\\sum_{u\\in j,r}(\\widehat F^{v}_{urte}+\\widehat D^{v}_{urte})},\\qquad\n\\Delta\\widehat M_{jte}=\\widehat M^{1}_{jte}-\\widehat M^{0}_{jte}. \\tag{E2}',
 '\\widehat M^{v}_{jte}=\\frac{\\sum_{u\\in j,r}\\widehat F^{v}_{urte}}{\\sum_{u\\in j,r}(\\widehat F^{v}_{urte}+\\widehat D^{v}_{urte})}. \\tag{E2}')
emp=emp.replace('这是给定比较样本','令 $\\Delta\\widehat M_{jte}=\\widehat M^{1}_{jte}-\\widehat M^{0}_{jte}$。这是给定比较样本')
start=emp.index('$$\n\\mathbb E[Y^q')
stop=emp.index('$$',start+3)+2
emp=emp[:start]+'''$$
\\mathbb E[Y^q_{urt}\\mid\\mathcal X,e]=\\exp[\\alpha^q_{ur,e}+\\lambda^q_{j(u)t,e}+\\eta^q_{rt,e}+B_{ur,e}'\\pi^q_t+L^q_{ue}(t)]. \\tag{E3a}
$$

其中事件动态项为：

$$
L^q_{ue}(t)=\\sum_{h\\ne-1}\\beta^q_{e,h}T_{ue}\\mathbf1(t-t_e=h). \\tag{E3b}
$$'''+emp[stop:]
emp=emp.replace('| 政策变异 | 主估计对象 |','表A3 限制类型与可识别对象\n\n| 政策变异 | 主估计对象 |')
struct=struct.split('## A8 结构验证与不确定性')[0].rstrip()
struct=struct.replace('教师后续材料采用','研究修订材料采用')
struct=struct.replace('删除原方案的 $IMPC=\\gamma/m$ 定义和转换参数 $\\nu$，直接以 $\\delta_{mj}$ 为反演参数。','本研究直接以 $\\delta_{mj}$ 描述政策引起的模型相对成本，不另引入经验成本到结构成本的尺度转换参数。')
struct=struct.replace('名义或不变价格口径','价格年份与货币口径')
struct=struct.replace('研究实际产出时还须施加与实证一致的价格调整。','当实证采用价格调整后的生产价值时，模型结果也施加一致调整。')
struct=struct.replace('先反演外资生产份额，再用外资实际产出、国内产出及总产出检验','基准用外资生产份额反演，再以外资生产价值、国内生产价值及总生产价值检验')
begin=struct.index('$$\n\\widehat{\\boldsymbol\\delta}')
finish=struct.index('$$',begin+3)+2
struct=struct[:begin]+'''$$
v(\\boldsymbol\\delta)=\\Delta\\mathcal O(\\mathcal G^c(\\boldsymbol\\delta))-\\widehat{\\boldsymbol\\mu}. \\tag{S3a}
$$

$$
\\widehat{\\boldsymbol\\delta}=\\underset{\\boldsymbol\\delta\\in\\mathcal D}{\\operatorname{argmin}}\\ v(\\boldsymbol\\delta)'Wv(\\boldsymbol\\delta). \\tag{S3b}
$$'''+struct[finish:]
struct=struct.replace('实际产出','生产价值')
struct=struct.replace('| 情景 | 政策设定 | 报告边界 |','表A4 反事实情景与实施边界\n\n| 情景 | 政策设定 | 报告边界 |')
end=end.replace('结构层保存','结构层先检查目标对参数的雅可比秩及可识别支持，再保存')
end=end.replace('实际生产统计','观测生产统计')

text='\n\n'.join([front.strip(),emp.strip(),struct.strip(),end.strip()])+'\n'
text=re.sub(r'### A\d+\.\d+ ', '### ', text)
labels={}
counter=0
def renumber(m):
 global counter
 counter+=1
 old=m.group(1) or f'FRONT{counter}'
 labels[old]=str(counter)
 return '\\tag{'+str(counter)+'}'
def display(m):
 expr=m.group(1).strip()
 tag=re.search(r'\\tag\{([^}]+)\}',expr)
 old=tag.group(1) if tag else None
 expr=re.sub(r'\\tag\{[^}]+\}','',expr).strip()
 global counter
 counter+=1
 labels[old or f'FRONT{counter}']=str(counter)
 return '$$ '+expr+' \\tag{'+str(counter)+'} $$'
text=re.sub(r'\$\$(.*?)\$\$',display,text,flags=re.S)
for old,new in sorted(labels.items(),key=lambda x:len(x[0]),reverse=True):
 text=text.replace('（'+old+'）','（'+new+'）')
# Final content QA corrections keep the estimation domain and legal scope explicit.
text=text.replace('### 事件表、比较对象与事件窗口','### 改革事件与比较窗口')
text=text.replace('\\sum_{u\\in j,r}\\widehat F','\\sum_{(u,r)\\in\\mathcal S_{je}}\\widehat F')
text=text.replace('\\sum_{u\\in j,r}(\\widehat F','\\sum_{(u,r)\\in\\mathcal S_{je}}(\\widehat F')
text=text.replace('构造有改革 $v=1$ 与无该改革 $v=0$ 的预测：','构造有改革 $v=1$ 与无该改革 $v=0$ 的预测。令 $\\mathcal S_{je}$ 为部门 $j$ 中实际进入事件 $e$ 估计和预测的活动—地区集合，仅在该集合上汇总：')
text=text.replace('这是给定比较样本、固定效应和识别假设的条件预测份额','这是给定集合 $\\mathcal S_{je}$、固定效应和识别假设的条件预测份额')
text=text.replace('结构目标同时保留外国及国内生产的预测响应；','若需要构造全部门目标，必须预先说明未进入 $\\mathcal S_{je}$ 单元的补全规则。例如将这些单元在有改革和无该改革两状态的参考产出保持相同，是额外的条件情景假设，不能宣称它们的响应已被识别。结构目标同时保留外国及国内生产的预测响应；')
text=text.replace('T_{ue}','T_{ur,e}').replace('L^q_{ue}','L^q_{ur,e}')
text=text.replace('$T_{ur,e}$ 表示受到该次改革的活动，','$T_{ur,e}$ 表示该活动—地区单元适用该次改革。投资者资格或特殊待遇不同的情况，按预先定义的法律待遇组分别建立事件及比较单元；式（6）—（7）在一个固定待遇组内使用，省略其组下标。')
text=text.replace('基准使用 PPML 条件均值；','基准使用泊松伪最大似然（PPML）条件均值方法（Santos Silva and Tenreyro，2006）；')
text=text.replace('令 $a_{fu,e0}$ 为改革前活动生产比重','令 $a_{fur,e0}$ 为改革前活动与生产地区联合生产比重')
text=text.replace('Z^k_{ft,e}=\\sum_u a_{fu,e0}z^k_{u,r(f,e0),t},\\qquad \\sum_u a_{fu,e0}=1.', 'Z^k_{ft,e}=\\sum_{u,r}a_{fur,e0}z^k_{urt},\\qquad \\sum_{u,r}a_{fur,e0}=1.')
text=text.replace('以该暴露定义意向处理，','式（8）的政策状态按冻结的改革前法律待遇组取值，企业同时在多个地区生产时仍采用联合基期权重。以该暴露定义意向处理（ITT），')
text=text.replace('反事实仅调整实际受改革外国企业在华生产的成本楔子。未受改革部门及中国企业境外生产的政策楔子保持不变，','基准向受改革部门的外国在华生产施加反演得到的部门平均等价楔子；活动组扩展才将政策楔子限定于实际受改革组。未受改革部门及中国企业境外生产的政策楔子保持不变，')
text=text.replace('增强规格在部门内设置受改革与未改革暴露组，采用与实证相同的比较算子；','增强规格在部门内设置受改革与未改革暴露组，在相同集合 $\\mathcal S_{je}$ 上采用与实证相同的比较算子；')
text=text.replace('部门汇总目标至多','粗部门基准的目标补全遵守式（5）的样本域和补全条件。部门汇总目标至多')
text=text.replace('其中 $g_j$ 为拟合流量的对数响应，','其中 $Q_{Cj}^{F}=\\sum_{m\\ne C}Q_{Cmj}$ 为该部门外国在华生产价值，$g_j$ 为拟合流量的对数响应，')
text=text.replace('比较不同结构参数下的结果，不再用ν尺度转换作为福利稳健性检验。','比较不同结构参数、经验目标与闭合条件下的结果。')
text=text.replace('Optimal Ownership and Firm Performance An Analysis','Optimal Ownership and Firm Performance: An Analysis')
text=text.replace('cap_{urt}',r'\mathrm{cap}_{urt}')
text=text.replace('分类版本 GB4 ISIC4 exact narrow partial ambiguous','分类版本 GB4 ISIC4 匹配类型')
text=text.replace('LLM输出 人工决定 修改依据 复核日期','LLM输出 人工决定 变更依据')
text=text.replace('F_{urt}=\\sum_fD^F_{ft}Q_{furt},\\qquad D_{urt}=\\sum_f(1-D^F_{ft})Q_{furt}.','F_{urt}={\\sum_fD^F_{ft}Q_{furt}},\\qquad D_{urt}={\\sum_f(1-D^F_{ft})Q_{furt}}.')
text=text.replace('Z^k_{ft,e}=\\sum_{u,r}a_{fur,e0}z^k_{urt},\\qquad \\sum_{u,r}a_{fur,e0}=1.','Z^k_{ft,e}={\\sum_{u,r}a_{fur,e0}z^k_{urt}},\\qquad {\\sum_{u,r}a_{fur,e0}}=1.')
text=text.replace('Q_{Cmj}=\\sum_n\\mathcal V_j(X_{nCmj},\\tau_{nCj},P),','Q_{Cmj}={\\sum_n\\mathcal V_j(X_{nCmj},\\tau_{nCj},P)},')
text=text.replace('其中 $Q_{Cj}^{F}=\\sum_{m\\ne C}Q_{Cmj}$ 为该部门外国在华生产价值，','其中 $Q_{Cj}^{F}$ 为各外国母国在该部门的在华生产价值之和，')
# Inline conditional log-flow responses are statistics, not unconditional welfare effects.
if '\ufffd' in text: raise ValueError('Replacement glyph')
draft=ROOT/'drafts/proposal_final.md'
draft.write_text(text,encoding='utf-8',newline='\n')
(ROOT/'equation_map.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'draft':str(draft),'chars':len(text),'display_equations':counter,'sha256':hashlib.sha256(draft.read_bytes()).hexdigest()},ensure_ascii=False))
