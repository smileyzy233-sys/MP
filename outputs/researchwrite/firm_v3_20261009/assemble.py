from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parent
front=(ROOT/'front_draft.md').read_text(encoding='utf-8')
policy=(ROOT/'policy_draft.md').read_text(encoding='utf-8')
back=(ROOT/'back_draft.md').read_text(encoding='utf-8')
policy=re.sub(r'^(#{1,2}) ',lambda m:'#'+m[1]+' ',policy,flags=re.M)
policy=policy.replace('六类变量沿用原方案的经济含义，取值越大表示相应限制越强。','六类变量分别记录不同的准入要求，取值越大表示相应限制越强。')
policy=policy.replace('其限制向量为：','其限制向量为：').replace('$$z_{pv}=','$$\\boldsymbol z_{pv}=')
policy=policy.replace('需要分别核实政策生效时已经实施的行业标准、文件明确采用的分类依据和企业数据实际使用的行业版本，再将其转换至本研究的固定分类。三者可能不同。','分别记录政策生效时已经实施的行业标准、文件明确采用的分类依据和企业数据实际使用的行业版本，据此核查不同资料的分类范围。三者可能不同。')
policy=policy.replace('企业数据采用何种标准，也应查阅相应统计说明。','企业数据采用何种标准，也应查阅相应统计说明。[^1]')
policy=policy.replace('原条款在后续版本中未出现时，','原条款在后续版本中未出现时，')
policy=policy.replace('并保留判断依据。\n\n表A1','并保留判断依据。[^2]\n\n表A1')
policy=policy.replace(r'\cos\!',r'\operatorname{cos}\!')
policy=policy.replace('设$\\ell$为企业源数据中的业务—地区记录','设$\\ell$为企业源数据中可区分的业务记录，同时保留相应生产地区')
policy=policy.replace('Z^k_{ft,e}', 'Z^k_{fte}')
policy=policy.replace(r',\quad k\in\{P,E,C,O,G,R\}.\tag{A5}',r'.\tag{A5}')
policy=policy.replace('业务记录仅对应企业自身资料，不作为跨版本政策活动编号。','其中，$k$取表A2中的六类限制。业务记录对应企业自身资料，不承担政策单元的跨版本连接。')
back=back.replace('\n###PLACEHOLDER\n','\n')
back=back.replace('事件$e$的基准规格为：','以$\\mathcal X$表示回归的条件信息，事件$e$的基准规格为：')
back=back.replace(r'\mathbb E[Q_{ft}\mid e]',r'\mathbb E[Q_{ft}\mid\mathcal X,e]')
back=back.replace('估计两组生产时检查PPML对全零观测组的处理；','估计两组生产时检查PPML对全零观测组的处理；')
back=back.replace('所得结果均对应原有企业群体。','所得结果均对应原有企业群体。[^3]')
back=back.replace('结构定义沿用研究稿，尚待核实的数值不用于本方案校准。','结构定义沿用研究稿，参数数值在模型校准时核实。')
footnotes='''

[^1]: GB2017于2017年10月1日实施，2017年目录于同年7月28日生效；2002年目录于当年4月生效，而GB2002于10月实施。这些时间提供分类核验参照，不证明目录按同期标准编制。另据国家统计局说明，2017年年度统计仍采用GB2011。参见[GB2017标准信息](https://std.samr.gov.cn/gb/search/gbDetailed?id=71F772D811F1D3A7E05397BE0A0AB82A)、[2017年目录](https://zfxxgk.ndrc.gov.cn/web/iteminfo.jsp?id=2808)、[2002年目录](https://www.ndrc.gov.cn/xxgk/zcfb/fzggwl/200507/t20050707_960602_ext.html)、[GB2002标准信息](https://std.samr.gov.cn/gb/search/gbDetailed?id=71F772D79DA6D3A7E05397BE0A0AB82A)及参考资料中的统计说明。

[^2]: 例如，2017年目录允许鼓励类与外资特别管理措施重合；2018年种业政策解释还对负面清单条目之外的作物说明准入要求。应结合全部适用规则判断，不能仅凭目录类别或条目是否出现赋值。参见[2017年目录原文](https://www.ndrc.gov.cn/xwdt/ztzl/gbmjcbzc/swb/201801/t20180122_1209171.html)和[2018年农业政策解释](https://dcj.mofcom.gov.cn/article/zcjd/jdtzhz/201811/20181102810202.shtml)。

[^3]: 对始终没有外国控制生产的企业，外国生产结果全为零；带企业固定效应的PPML可能因分离而剔除相关观测。应核对实际估计样本及预测覆盖，不能将被剔除企业视为未受改革影响。参见[PPMLHDFE作者文档](https://scorreia.com/help/ppmlhdfe.html)。
'''
text='\n\n'.join([front.strip(),policy.strip(),back.strip()])+footnotes
(ROOT/'proposal_v3.md').write_text(text,encoding='utf-8')
stats={'chinese_chars':len(re.findall(r'[\u4e00-\u9fff]',text)),'characters':len(text),'display_labels':re.findall(r'\\tag\{(A\d+)\}',text),'headings':re.findall(r'^#{2,3} (.+)$',text,re.M)}
(ROOT/'draft_stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(stats,ensure_ascii=False,indent=2))
