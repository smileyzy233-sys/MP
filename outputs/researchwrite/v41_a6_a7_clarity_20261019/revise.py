from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree
import copy,hashlib,json,re
import latex2mathml.converter

ROOT=Path(r'A:\桌面\study');BASE=Path(__file__).resolve().parent
TARGET=ROOT/'企业微观层面_v4.1.docx';STAGE=BASE/'review.docx';SNAPSHOT=BASE/'input.docx'
EXPECTED='e24e3a2732c4405f5c0d8441bd1f716bddc2aa31d976f1533487c345be39e698'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}';M='{'+NS['m']+'}';SPACE='{http://www.w3.org/XML/1998/namespace}space'
XSL=etree.XSLT(etree.parse(r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL'))
def sha(data):return hashlib.sha256(data).hexdigest()
def txt(e):return ''.join(e.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
def el(name):return etree.Element(W+name)
def xb(e):return etree.tostring(e,encoding='UTF-8',xml_declaration=True,standalone=True)

def math(tex,size=12):
    ml=etree.fromstring(latex2mathml.converter.convert(tex).encode('utf-8'))
    om=etree.fromstring(etree.tostring(XSL(ml)))
    assert not any(t.text and '\\' in t.text for t in om.findall('.//m:t',NS)),tex
    for r in om.findall('.//m:r',NS):
        rp=el('rPr');fonts=el('rFonts')
        for key in ['ascii','hAnsi','cs']:fonts.set(W+key,'Cambria Math')
        fonts.set(W+'eastAsia','宋体');rp.append(fonts)
        sz=el('sz');sz.set(W+'val',str(int(2*size)));rp.append(sz)
        r.insert(1 if len(r) and r[0].tag==M+'rPr' else 0,rp)
    return om

def replace(p,text,size=12):
    rp=p.find('w:r/w:rPr',NS);rp=copy.deepcopy(rp) if rp is not None else None
    for c in list(p):
        if c.tag!=W+'pPr':p.remove(c)
    for token in re.split(r'(\$[^$]+\$)',text):
        if not token:continue
        if token.startswith('$') and token.endswith('$'):p.append(math(token[1:-1],size))
        else:
            r=el('r')
            if rp is not None:r.append(copy.deepcopy(rp))
            t=el('t');t.text=token;t.set(SPACE,'preserve');r.append(t);p.append(r)

A6=[
('h','A.6 从企业预测形成部门生产目标'),
('p','本节把A.5的企业回归结果转为部门层面的情景预测，回答：在同一年取消纳入研究的清单限制，某一部门的外国控制生产份额会改变多少？这一份额变化就是交给A.7结构模型拟合的“部门生产目标”。'),
('p',r'先沿用A.5的模型形式，分别以外国控制生产和国内控制生产为结果进行估计，得到两套预测方程。选择同一基准年份$t^*$和同一批企业：情景0输入企业实际的$\mathrm{Intensity}_{ft}$，情景1将纳入比较、强度已知且可以预测的记录设为0。两种情景保留各方程的系数、固定效应、控制变量与企业行业归属，只改变强度输入，分别预测外国与国内控制生产。'),
('p',r'再沿路径B将企业预测归入模型部门，分别加总为外国生产$F_{j,t^*}^{a}$与国内生产$D_{j,t^*}^{a}$，其中$a=0,1$表示两种情景。每种情景的外国控制生产份额，都用外国生产除以外国与国内生产之和。两种份额相减，得到部门目标：'),
('eq4',''),
('p',r'例如，表A2使用同一金额单位下的虚拟预测值说明计算。保留限制时，外国生产份额为$200/(200+800)=20\%$；取消限制时为$300/(300+900)=25\%$。因此$\mu_j=0.05$，即模型需要拟合外国生产份额提高5个百分点的变化。外国、国内及总生产同时保留，用来辨认份额变化来自哪类生产调整。'),
('cap','表A2  两种限制情景的预测示例（虚拟数值）'),
('table',''),
('p','上述加总首先对应调查覆盖样本。扩展到部门总体时，使用有调查依据的扩展权重，或以同口径行业资料补充调查外生产；企业、AMNE与模型保持一致的生产者价值和控制口径。强度未知和其他无法预测的生产不填零。把补充生产在两种情景中保持实际值，意味着假定这部分不随限制变化而反应，这一假设与样本覆盖共同决定部门目标的范围。'),
('p','这些预测保持企业集合和行业归属不变，沿用回归模型的条件解释，尚未加入企业迁移、新进入和价格反馈。滞后规格需要分别输入两种情景的完整强度路径；补充比较历史政策变化时，情景0采用旧规则、情景1采用后续规则，其余计算相同。'),
]
A7=[
('h','A.7 从部门生产目标到MP成本与一般均衡反事实'),
('p','A.6给出了外国生产份额需要变化多少，本节利用现有跨国生产、贸易和投入产出模型，寻找能够产生这一变化的部门MP成本。[10] 这里的“反演”是从生产目标反推成本：企业回归提供生产变化，结构模型决定与之相应的等效成本变化。'),
('p',r'模型中的MP效率越高，单位生产成本越低。以$i$表示生产国、$m$表示企业母国、$j$表示部门，$C$表示中国，效率$\xi_{im}^{j}$与成本乘数的关系为'),
('eq5',''),
('p',r'取消限制的基准比较从实际经济状态出发，将其作为情景0。同时给定各部门一组候选MP成本变化，模型据此生成外国与国内生产；按A.6相同的部门、控制定义和价值口径计算两种情景的份额差，再与$\mu_j$比较。通过调整这组成本，使模型生成的份额差尽可能接近各部门目标，得到拟合的成本变化。对表A2的虚拟例子，拟合目标是份额提高5个百分点，成本需要改变多少由模型中的生产反应决定。'),
('p',r'令$\delta_j$表示情景1相对于情景0的部门MP成本对数变化。外国合计生产目标对应部门内各外国母国的共同$\delta_j$；$\delta_j<0$表示成本下降。成本与效率的变化倍数分别为'),
('eq6',''),
('p','完成成本拟合后，将相应变化用于一般均衡反事实。采用局部均衡拟合时，先固定选定的价格、工资和需求，以对应回归预测中的给定环境；转入一般均衡后，价格、工资、生产及模型中的创新通过生产地选择、贸易和中间投入共同调整。研究据此比较部门产出、外国与国内生产、生产布局及实际收入和福利。一般均衡的份额变化可能不同于A.6的条件目标，这一差异体现模型加入的市场反馈。'),
('p','历史政策比较沿用同一逻辑；实际资料对应后续规则情景1时，反向恢复旧规则情景0。反演结果依赖回归与结构假设，是情景等效成本，不能将强度分数、回归系数或残差直接当作MP成本。参考模型未设股权收购决策，因此所有权重新归属主导的份额变化不能直接解释为效率改善；基期外国生产为零的活动，也不能由现有帽子代数自动产生准入后的新进入。'),
]
TABLE=[['部门预测结果','情景0：实际限制','情景1：取消限制'],['外国控制生产','200','300'],['国内控制生产','800','900'],['总生产','1,000','1,200'],['外国控制生产份额','20%','25%']]

def make_table(template):
    table=copy.deepcopy(template);rows=[copy.deepcopy(r) for r in table.findall('w:tr',NS)]
    for r in table.findall('w:tr',NS):table.remove(r)
    widths=[4000,2620,2621];grid=table.find('w:tblGrid',NS)
    for c in list(grid):grid.remove(c)
    for width in widths:
        c=el('gridCol');c.set(W+'w',str(width));grid.append(c)
    for i,values in enumerate(TABLE):
        tr=copy.deepcopy(rows[0] if i==0 else rows[-1] if i==len(TABLE)-1 else rows[2])
        pr=tr.find('w:trPr',NS)
        if pr is None:pr=el('trPr');tr.insert(0,pr)
        for c in list(pr):
            if c.tag in [W+'trHeight',W+'tblHeader']:pr.remove(c)
        if i==0:pr.append(el('tblHeader'))
        for j,(cell,value) in enumerate(zip(tr.findall('w:tc',NS),values)):
            ps=cell.findall('w:p',NS)
            for p in ps[1:]:cell.remove(p)
            replace(ps[0],value,10.5)
            prc=cell.find('w:tcPr',NS);cw=prc.find('w:tcW',NS);cw.set(W+'w',str(widths[j]));cw.set(W+'type','dxa')
            ppr=ps[0].find('w:pPr',NS)
            jc=ppr.find('w:jc',NS)
            if jc is None:jc=el('jc');ppr.append(jc)
            jc.set(W+'val','left' if j==0 else 'center')
        table.append(tr)
    return table

if __name__=='__main__':
    data=TARGET.read_bytes()
    if SNAPSHOT.exists():
        assert sha(SNAPSHOT.read_bytes())==EXPECTED
        data=SNAPSHOT.read_bytes()
    else:
        assert sha(data)==EXPECTED,'Target changed; reread before editing'
        SNAPSHOT.write_bytes(data)
    with ZipFile(SNAPSHOT) as z:blobs={n:z.read(n) for n in z.namelist()}
    root=etree.fromstring(blobs['word/document.xml']);body=root.find('w:body',NS);nodes=list(body)
    first=next(i for i,e in enumerate(nodes) if txt(e).startswith('A.6 '))
    seventh=next(i for i,e in enumerate(nodes) if txt(e).startswith('A.7 '))
    last=next(i for i,e in enumerate(nodes) if txt(e)=='参考文献与资料')
    # Preserve existing break paragraph before bibliography outside the edited range.
    while last>seventh and not txt(nodes[last-1]):last-=1
    eqs={int(re.search(r'（A(\d+)）$',txt(e))[1]):e for e in nodes[first:last] if re.search(r'（A\d+）$',txt(e))}
    new=[]
    for items,heading in [(A6,first),(A7,seventh)]:
        for kind,text in items:
            if kind.startswith('eq'):e=copy.deepcopy(eqs[int(kind[2:])])
            elif kind=='table':e=make_table(nodes[17])
            else:
                template=nodes[heading] if kind=='h' else nodes[16] if kind=='cap' else nodes[first+1]
                e=copy.deepcopy(template);replace(e,text,11 if kind=='cap' else 12)
            new.append(e)
    for e in new:nodes[first].addprevious(e)
    for e in nodes[first:last]:body.remove(e)
    # Keep the explanatory example and its editable table together using an ordinary break.
    for example in [e for e in new if txt(e).startswith('例如，表A2') or txt(e).startswith('令δ')]:
        page=el('p');pr=el('pPr');page.append(pr)
        spacing=el('spacing');spacing.set(W+'before','0');spacing.set(W+'after','0');spacing.set(W+'line','20');spacing.set(W+'lineRule','exact');pr.append(spacing)
        rr=el('r');br=el('br');br.set(W+'type','page');rr.append(br);page.append(rr);example.addprevious(page)
    # Suppress only the forbidden paragraph pagination settings, wherever inherited.
    blobs['word/document.xml']=xb(root);changed_parts=[]
    for name,data in list(blobs.items()):
        if name.startswith('word/') and name.endswith('.xml'):
            tree=root if name=='word/document.xml' else etree.fromstring(data);changed=False
            for tag in ['keepNext','keepLines','pageBreakBefore']:
                for e in tree.findall('.//w:'+tag,NS):
                    if e.get(W+'val','true').lower() not in ['0','false','off']:e.set(W+'val','0');changed=True
            if changed:blobs[name]=xb(tree);changed_parts.append(name)
    # Outside-section content is kept byte-for-byte unless a forbidden flag needed suppression.
    after=list(body);newfirst=next(i for i,e in enumerate(after) if txt(e).startswith('A.6 '));newlast=next(i for i,e in enumerate(after) if txt(e)=='参考文献与资料')
    for old,newnode in zip(nodes[:first],after[:newfirst]):assert etree.tostring(old)==etree.tostring(newnode)
    assert [txt(e) for e in nodes[last:]]==[txt(e) for e in after[newlast-(next(i for i,e in enumerate(nodes[last:]) if txt(e)=='参考文献与资料')):]]
    with ZipFile(STAGE,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():z.writestr(name,data)
    actual=[{'i':i,'text':txt(e)} for i,e in enumerate(body)]
    (BASE/'actual.json').write_text(json.dumps(actual,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'actual.txt').write_text('\n\n'.join(f"[{q['i']}] {q['text']}" for q in actual),encoding='utf-8')
    meta={'input_sha256':EXPECTED,'stage_sha256':sha(STAGE.read_bytes()),'changed_sections':['A.6','A.7'],'forbidden_flag_parts_changed':changed_parts,'prefix_nodes_preserved':first,'new_section_nodes':len(new),'native_omml':len(root.findall('.//m:oMath',NS)),'editable_tables':len(body.findall('w:tbl',NS))}
    (BASE/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False))
