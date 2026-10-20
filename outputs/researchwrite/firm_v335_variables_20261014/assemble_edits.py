from pathlib import Path
import json,re
B=Path(__file__).resolve().parent
src={r['p']:r['text'] for r in json.loads((B/'sources/current_before_paragraphs.json').read_text(encoding='utf-8'))}
rows={}
for name in ['terminology_main.json','terminology_back.json']:
 for r in json.loads((B/'reviews'/name).read_text(encoding='utf-8')):
  assert r['old']==src[r['p']],r['p']
  rows[r['p']]=r
def put(p,value,reason='统一术语及变量来源，保留原方法'):
 rows[p]={'p':p,'old':src[p],'new':value,'reason':reason}
put(66,'以GB2002口径下的企业行业代码H6361为例：H为门类“批发和零售业”，63为大类“批发业”，636为中类“矿产品、建材及化工产品批发”，小类6361的名称为“煤炭及制品批发”。[9] 税调记录采用GB2002时，便可由H6361取得这一GB小类名称，将其与各版目录条款所述活动一并输入LLM。')
ins=json.loads((B/'insertions.json').read_text(encoding='utf-8'))
ins.append({'id':'coal_policy_example','after':66,'style_from':64,'text':'例如，2007目录限制类“六、批发和零售业”第2项列举粮食、棉花等商品的批发、零售和配送，并对超过30家分店、销售多个供应商不同种类和品牌商品的连锁店规定中方控股。[1] “煤炭及制品批发”与该项列举的商品活动不相符，记录为该条款未命中，同时保存条款原文、编号及其控股条件。其他条款沿同一方法检索和复核，命中条款的具体要求用于汇总该版限制状态。'})
(B/'insertions.json').write_text(json.dumps(ins,ensure_ascii=False,indent=2),encoding='utf-8')
put(95,'生产的部门归属与依据改革前GB小类名称确定的固定Treat分别记录。企业各期行业代码按所属GB版本处理，经必要的新旧类目转换统一到GB2017（含第1号修改单），再与ISIC Rev.4衔接，归入所选发布版的AMNE部门，最后聚合到模型部门。[7,9,10] 分类注释和一对多关系用于核查当期分类转换的候选范围。ISIC提供国际比较口径，AMNE部门和模型部门在此基础上采用各自的行业汇总范围。')
put(96,'GB2002代码先查本地《GBT 4754—2002和GBT 4754—2011对照表.xls》，完成GB2002—GB2011新旧分类转换，再查GB2017附录B中的GB2011—GB2017新旧类目对照；GB2011代码直接查该附录B。GB2017附录C提供GB2017—ISIC Rev.4对照。所选AMNE发布版的部门表列明各AMNE部门包含的ISIC范围，例如2024版readme-aamne.xlsx中的Country_Industry表。每一步保存来源文件与版本、原代码、目标候选、完整或部分内容的对应关系及依据位置。一个旧代码对应多个目标时，保留全部候选及适用范围，产出分配以可核实的分业务产出为依据。')
put(97,'当期生产归属可分别在AMNE部门和模型部门层面确定。某一层级的全部合理候选归入同一部门时，即可在该层级明确归属；候选跨部门且现有代码无法进一步区分时，保持未确定。未来若取得可核实的分业务产出资料，可据此分配到对应部门。')
put(99,rows[99]['new'].replace('C4190说明了核实版本的重要性。','企业行业代码C4190在不同GB版本中含义不同。').replace('GB2017附录B、附录C及2024版AMNE示例','GB2017附录B、附录C及2024版AMNE部门表'))
put(104,rows[104]['new'].replace('有41个行业','列有41个行业汇总项目'))
put(105,rows[105]['new'].replace('本地代码资料中有20部门设定','本地模型程序中有20部门设定'))
put(110,'设{{M0}}为根据改革前GB小类确定的行业比较组，{{M1}}为改革前地区，{{M2}}为估计使用的信息。基准条件均值写为')
put(116,rows[116]['new'].replace('不同层级之间的可比性','组内不同GB小类之间的可比性'))
put(117,src[117].replace('行业和地区分组在改革前固定','行业比较组和地区分组在改革前固定'))
put(123,src[123].replace('所属类别','所属GB小类'))
put(124,src[124].replace('改革前控制类型、行业类别和部门','改革前控制类型、GB小类和模型部门归属'))
put(135,src[135].replace('按改革前行业、地区和处理身份','按改革前行业分组、地区和处理身份'))
put(136,'A.6.2 行业加总与生产权重')
put(142,'分母为零时该份额没有定义。若将若干不重叠的较细统计单元{{M0}}（如已统一口径的GB小类或AMNE部门）汇入同一模型部门，应先加总外国和国内生产，再计算份额。这等价于按各统计单元的总生产价值{{M1}}加权：')
put(144,src[144].replace('汇总行业份额','汇总较细统计单元的份额'))
put(145,'跨统计单元加总统一货币、价格年份与估值口径。共同价格因子可能在单个统计单元份额的分子、分母中抵消，模型部门份额仍需使用口径一致的各统计单元生产价值。无法归属、控制关系不明及调查外的生产分别报告，根据其占比和构成判断样本份额的代表性。')
put(151,rows[151]['new'].replace('当期行业代码及其分类版本','当期企业行业代码及其GB版本').replace('依据改革前GB小类名称的匹配判断固定','依据改革前GB小类的本轮实际放宽判断固定'))
put(158,rows[158]['new'].replace('相应的处理与对照类别','相应的处理与对照GB小类').replace('细行业类别之间的关系','GB小类之间的关系'))
put(175,rows[175]['new'].replace('相应的类别比较组','相应的GB小类政策暴露分组'))
put(188,rows[188]['new'].replace('形成固定处理身份','逐版记录限制状态，比较本轮实际放宽，形成固定处理身份'))
put(189,'政策匹配复核中的分歧及其解决依据随记录保存；若某项判断发生变化，可据修订后的Treat检验估计对该判断的敏感程度。生产估计报告适当聚类下的区间，部门补充假设和结构参数采用有来源的替代设定。能够实施重抽样时，依据政策赋值和误差相关结构重新估计生产目标及成本，同时报告未收敛或无法反演的情况。')
put(197,src[197].replace('Country_Industry表及ReadMe_analyticalAMNE表','列明ISIC范围的Country_Industry部门表及ReadMe_analyticalAMNE表'))
put(199,rows[199]['new'].replace('GB2017本地PDF第99页','GB2002本地PDF第34、36页对应H6361示例。GB2017本地PDF第99页'))
put(198,'[8] 本地2007—2014年度全国税收调查整理DTA、税调基本信息07_20.dta及“税调变量说明07-16”。2007填报说明第1—2页提供信息表及行业口径依据；现有DTA的整理者标签、配套说明和有限抽查用于核对企业行业代码，原始报送表到当前字段的完整转换记录仍待取得。')
put(199,'[9] 国家统计局：GB/T 4754—2002、GB/T 4754—2011、GB/T 4754—2017《国民经济行业分类》及2019年第1号修改单；《2017年国民经济行业分类注释》；GB2002—GB2011对照表。H6361见GB2002本地PDF第34、36页；分类转换见GB2017附录B、C，所用对照表及1329/1322差异详见A.4。标准及修改单；分类注释。')
for p,r in rows.items():
 assert re.findall(r'\{\{M\d+\}\}',r['old'])==re.findall(r'\{\{M\d+\}\}',r['new']),p
 assert p not in range(73,88),p
(B/'approved_edits.json').write_text(json.dumps(sorted(rows.values(),key=lambda r:r['p']),ensure_ascii=False,indent=2),encoding='utf-8')
if not (B/'layout_breaks.json').exists():(B/'layout_breaks.json').write_text('[]',encoding='utf-8')
print(len(rows),'approved edits; table A2 rebuilt; 2 inserted paragraphs')
