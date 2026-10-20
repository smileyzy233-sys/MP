from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parent
parts=[(ROOT/n).read_text(encoding='utf-8') for n in ['front_module.md','policy_module.md','identification_module.md','back_module.md']]
ident=parts[2]
ident=re.sub(r'^# A\.3',r'## A.3',ident,flags=re.M)
ident=re.sub(r'^## A\.3\.',r'### A.3.',ident,flags=re.M)
ident=ident.replace('采用生产者收入时须按 X/τ 处理','采用生产者收入时须按 $X/\\tau$ 处理')
ident=ident.replace('先加总生产价值，再计算比值：','先加总生产价值，再计算比值：')
ident=ident.replace('分母为零时份额未定义。','跨部门总体份额也先加总生产价值，再计算比值。分母为零时份额未定义。')
ident=ident.replace('粗部门模型不能直接区分细活动的处理与对照。','粗部门模型只描述部门，不能直接区分细活动的处理与对照。')
ident=ident.replace('控制权重分类','所有权重新分类')
ident=ident.replace('h=-1 为参照期','h=t-t_e 为相对改革时间，H_e 为事先确定的事件窗口，h=-1 为参照期')
ident=ident.replace('企业层面另用 A.2.4 的改革前暴露跟踪存量企业，','企业层面另用 A.2.4 的改革前暴露跟踪存量企业，采用企业固定效应及基期行业、地区年度效应；')
ident=ident.replace(r'\sum_f D_{ft}^{F}Q_{furt}',r'{\sum_f D_{ft}^{F}Q_{furt}}').replace(r'\sum_f(1-D_{ft}^{F})Q_{furt}',r'{\sum_f(1-D_{ft}^{F})Q_{furt}}')
ident=ident.replace(r'Q_{Cmj}=\sum_n V_j(X_{nCmj},\tau_{nCj},P)',r'Q_{Cmj}={\sum_n\mathcal V_j(X_{nCmj},\tau_{nCj},P)}')
ident=ident.replace(r'G_c(\delta)',r'\mathcal G^c(\boldsymbol\delta)').replace(r'\Delta O',r'\Delta\mathcal O').replace(r'\mathbf v(\delta)',r'\mathbf v(\boldsymbol\delta)').replace(r'-\mu.',r'-\widehat{\boldsymbol\mu}.')
ident=ident.replace(r'\widehat\delta=\arg\min_{\delta\in\mathcal D}',r'\widehat{\boldsymbol\delta}=\underset{\boldsymbol\delta\in\mathcal D}{\operatorname{argmin}}')
ident=ident.replace('基准规格为：','基准规格为：')
inline_map={
 'b∈{F,D}':r'b\in\{F,D\}', 'Y_{urt}^{b}':r'Y_{urt}^{b}', 'T_{ur,e}':r'T_{ur,e}',
 'h=-1':r'h=-1', 'B_{ur,e}':r'B_{ur,e}', 'exp(β_{e,h}^{b})-1':r'\exp(\beta_{e,h}^{b})-1',
 'Q_{furt}':r'Q_{furt}', 'D_{ft}^{F}':r'D_{ft}^{F}', 'v=1':r'v=1','v=0':r'v=0',
 'S_{je}':r'\mathcal S_{je}', 'δ_j':r'\delta_j','G_c(δ)':r'\mathcal G^c(\boldsymbol\delta)',
 'c∈{PE,GE}':r'c\in\{PE,GE\}','θ_j/(1−ρ_j)':r'\theta_j/(1-\rho_j)',
 '𝒳':r'\mathcal X', 'μ':r'\widehat{\boldsymbol\mu}',
 'X_{nCmj}':r'X_{nCmj}',
 'h=t-t_e':r'h=t-t_e','H_e':r'\mathcal H_e',
}
def prose_convert(s):
 s=s.replace('改革事件 e ', '改革事件 $e$ ').replace('事件 e ', '事件 $e$ ')
 s=s.replace('活动 u、地区 r ', '活动 $u$、地区 $r$ ')
 s=s.replace('部门 j ', '部门 $j$ ')
 s=s.replace('令 V_j ', '令 $\\mathcal V_j$ ').replace('P 为相应', '$P$ 为相应')
 s=s.replace('；O 按', '；$\\mathcal O$ 按').replace('ΔO 比较', '$\\Delta\\mathcal O$ 比较')
 s=s.replace('参数域 D 遵循', '参数域 $\\mathcal D$ 遵循').replace('权重 W 按', '权重 $W$ 按')
 pattern='|'.join(re.escape(k) for k in sorted(inline_map,key=len,reverse=True))
 return re.sub(pattern,lambda m:'$'+inline_map[m.group(0)]+'$',s)
segments=re.split(r'(\$\$.*?\$\$|\$[^$]+\$)',ident,flags=re.S)
ident=''.join(s if s.startswith('$') else prose_convert(s) for s in segments)
ident=ident.replace('S_{je}',r'\mathcal S_{je}')
ident=ident.replace(r'\mathcal \mathcal S_{je}',r'\mathcal S_{je}')
parts[2]=ident
parts[3]=parts[3].replace('## A.4 禁止准入在企业路线中的处理','## A.4 禁止准入的处理')
parts[3]=parts[3].replace('### A.5.1 经验成本与结构效率项','### A.5.1 反演成本与结构效率项')
parts[3]=parts[3].replace('检验改革组合是否有识别依据，分别求解累计变化','核查改革组合是否有识别依据，求解累计变化')
parts[3]=parts[3].replace('结构分析检查目标能否区分参数、模型能否达到经验目标，以及反演是否存在边界解或多解。','结构分析先检查各成本参数的变化能否在生产目标中产生可区分的反应，并检验相应雅可比矩阵的秩；目标不能区分参数时，不进行多参数反演。再检查模型能否达到经验目标，以及反演是否存在边界解或多解。目标无法达到或出现多解时，说明无法唯一反演的原因及取值范围。')
parts[1]=parts[1].replace('$$z_{urt}=',r'$$\boldsymbol z_{urt}=')
text='\n\n'.join(s.strip() for s in parts)+'\n'
labels={};counter=0
def numbered(m):
 global counter
 expr=m.group(1).strip();tag=re.search(r'\\tag\{([^}]+)\}',expr)
 assert tag,expr
 counter+=1;labels[tag.group(1)]=f'A{counter}'
 expr=re.sub(r'\\tag\{[^}]+\}','',expr).strip()
 return '$$ '+expr+' \\tag{A'+str(counter)+'} $$'
text=re.sub(r'\$\$(.*?)\$\$',numbered,text,flags=re.S)
for old,new in labels.items():text=text.replace('（'+old+'）','（'+new+'）')
# Normalize authoring notation, preserving the same mathematical definitions.
text=text.replace(r'\cos',r'\operatorname{cos}')
text=text.replace('\u3000',' ')
assert '\ufffd' not in text
assert not any(s in text for s in ['IMPC=','\\gamma/m','\\nu','完整的历史制度成本存量'])
assert re.findall(r'^## A\.(\d+) ',text,flags=re.M)==[str(n) for n in range(1,8)]
subs=re.findall(r'^### A\.(\d+)\.(\d+) ',text,flags=re.M)
assert [x for x in subs if x[0]=='1']==[('1',str(i)) for i in range(1,4)]
assert [x for x in subs if x[0]=='2']==[('2',str(i)) for i in range(1,5)]
assert [x for x in subs if x[0]=='3']==[('3',str(i)) for i in range(1,5)]
assert [x for x in subs if x[0]=='5']==[('5',str(i)) for i in range(1,3)]
assert [x for x in subs if x[0]=='6']==[('6',str(i)) for i in range(1,4)]
(ROOT/'proposal_final.md').write_text(text,encoding='utf-8',newline='\n')
(ROOT/'formula_labels.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'draft':str(ROOT/'proposal_final.md'),'chars':len(text),'formulas':counter,'main_sections':7,'subsections':len(subs),'sha256':hashlib.sha256(text.encode()).hexdigest()},ensure_ascii=False))
