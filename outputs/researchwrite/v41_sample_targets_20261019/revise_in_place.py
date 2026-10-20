from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
import sys, copy, hashlib, json, re, os, io

ROOT=Path(r'A:\桌面\study');BASE=Path(__file__).resolve().parent
TARGET=ROOT/'企业微观层面_v4.1.docx'
EXPECTED='879ad86c74bb105f021d995a981da3d3d8e7599d64cb0eb8ae9feeb56d4b2c1b'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}';SPACE='{http://www.w3.org/XML/1998/namespace}space'
def sha(data):return hashlib.sha256(data).hexdigest()
def text(e):return ''.join(e.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
def xml(e):return etree.tostring(e,encoding='UTF-8',xml_declaration=True,standalone=True)

def replace_text_nodes(p,old,new):
    ts=p.xpath('.//w:t',namespaces=NS)
    joined=''.join(t.text or '' for t in ts)
    assert joined.count(old)==1,(old,joined.count(old))
    start=joined.index(old);end=start+len(old);offset=0;inserted=False
    for t in ts:
        value=t.text or '';a=offset;b=a+len(value);offset=b
        if b<=start or a>=end:continue
        left=value[:max(0,start-a)] if a<=start else ''
        right=value[end-a:] if b>=end else ''
        t.text=left+(new if not inserted else '')+right
        t.set(SPACE,'preserve');inserted=True

def para(p,content):
    # Preserve the paragraph and its current typography; new inline math is OMML.
    import latex2mathml.converter
    transform=etree.XSLT(etree.parse(r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL'))
    rp=p.find('w:r/w:rPr',NS);rp=copy.deepcopy(rp) if rp is not None else None
    for e in list(p):
        if e.tag!=W+'pPr':p.remove(e)
    for token in re.split(r'(\$[^$]+\$)',content):
        if not token:continue
        if token.startswith('$') and token.endswith('$'):
            mml=etree.fromstring(latex2mathml.converter.convert(token[1:-1]).encode('utf-8'))
            om=etree.fromstring(etree.tostring(transform(mml)))
            for run in om.findall('.//m:r',NS):
                prop=etree.Element(W+'rPr')
                fonts=etree.SubElement(prop,W+'rFonts')
                for key in ['ascii','hAnsi','cs']:fonts.set(W+key,'Cambria Math')
                fonts.set(W+'eastAsia','宋体')
                sz=etree.SubElement(prop,W+'sz');sz.set(W+'val','24')
                pos=1 if len(run) and run[0].tag=='{'+NS['m']+'}rPr' else 0
                run.insert(pos,prop)
            p.append(om)
        else:
            run=etree.SubElement(p,W+'r')
            if rp is not None:run.append(copy.deepcopy(rp))
            t=etree.SubElement(run,W+'t');t.text=token;t.set(SPACE,'preserve')

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    BASE.mkdir(parents=True,exist_ok=True)
    original=TARGET.read_bytes();assert sha(original)==EXPECTED,'Current file changed; preserve and reread'
    # Internal recovery bytes, not a new document version or deliverable.
    recovery=BASE/'source_before.bin'
    if not recovery.exists():recovery.write_bytes(original)
    else:assert sha(recovery.read_bytes())==EXPECTED
    with ZipFile(io.BytesIO(original)) as z:blobs={name:z.read(name) for name in z.namelist()}
    root=etree.fromstring(blobs['word/document.xml']);body=root.find('w:body',NS);nodes=list(body)
    assert text(nodes[31])=='A.6 从企业预测形成部门生产目标'
    assert text(nodes[42])=='A.7 从部门生产目标到MP成本与一般均衡反事实'
    before_nodes=[etree.tostring(n) for n in nodes]
    equations=root.xpath('//w:body/w:p[w:r/w:tab]',namespaces=NS)
    before_equations=[etree.tostring(e) for e in equations]
    edits={}
    def change(i,old,new):
        replace_text_nodes(nodes[i],old,new);edits.setdefault(i,[]).append({'old':old,'new':new})
    change(1,'分别预测外国与国内控制生产，聚合为部门目标','分别预测税调样本企业的外国与国内控制生产，形成部门份额变化目标')
    change(11,'按统一价值口径加总，为A.6的部门目标提供基础','在税调样本内按统一价值口径加总，为A.6的部门份额变化目标提供基础')
    flow=nodes[3].findall('w:tr',NS)[-1].find('w:tc/w:p',NS)
    replace_text_nodes(flow,'按部门加总生产与形成情景目标','税调样本按部门加总 → 形成份额变化目标')
    edits[3]=[{'flow':'Explicit tax-survey sample aggregation and share-change target'}]
    replacements={
      32:'本节把A.5的企业回归结果转为税调样本的部门情景预测，考察在同一年取消纳入研究的清单限制时，样本中的外国控制生产份额会改变多少。这一份额变化就是交给A.7结构模型拟合的部门生产目标。',
      33:r'先沿用A.5的模型形式，分别以外国控制生产和国内控制生产为结果进行估计，得到两套预测方程。在同一基准年份$t^*$，以同一批税调样本企业构造两种情景：情景0保留实际的$\mathrm{Intensity}_{ft}$，情景1将该强度统一设为0，模拟取消相应清单限制。预测时保留各方程的系数、固定效应和控制变量，并保持企业范围、行业归属和控制口径一致，只替换强度输入，分别预测外国与国内控制生产。',
      34:r'再沿路径B将税调样本企业的预测生产归入模型部门，在同一预测样本内分别加总为外国生产$F_{j,t^*}^{a}$与国内生产$D_{j,t^*}^{a}$，其中$a=0,1$表示两种情景。各情景的外国控制生产份额为外国生产占外国与国内生产之和的比重，两种份额之差即部门目标：',
      40:'部门目标采用税调样本内的份额变化。强度未知或无法预测的记录保持缺失，两种情景使用相同的有效样本范围；企业、AMNE与结构模型保持一致的部门划分、生产者价值和控制口径。将样本份额变化用于模型部门，假定税调样本能够反映该部门对清单限制变化的反应。',
      43:'A.6给出了税调样本的部门外国控制生产份额变化，本节利用现有跨国生产、贸易和投入产出模型，寻找能够使模型部门产生相应份额变化的MP成本调整。[10] 这里的“反演”是依据份额变化目标反推等效成本变化。',
    }
    for i,content in replacements.items():
        old=text(nodes[i]);para(nodes[i],content);edits[i]=[{'old':old,'new':text(nodes[i])}]
    change(37,'例如，表A2使用同一金额单位下的虚拟预测值说明计算','例如，表A2以税调样本为对象，使用同一金额单位下的虚拟预测值说明计算')
    change(38,'表A2  两种限制情景的预测示例（虚拟数值）','表A2  两种限制情景的税调样本预测示例（虚拟数值）')
    header=nodes[39].find('w:tr/w:tc/w:p',NS)
    replace_text_nodes(header,'部门预测结果','税调样本预测结果');edits[39]=[{'header':'税调样本预测结果'}]
    change(46,'按A.6相同的部门、控制定义和价值口径计算两种情景的份额差，再与','按与税调样本一致的部门划分、控制定义和价值口径计算模型的情景份额差，再与样本目标')
    change(50,'一般均衡的份额变化可能不同于A.6的条件目标','一般均衡的份额变化可能不同于A.6的样本条件目标')
    # Structural checks before publication.
    assert before_equations==[etree.tostring(e) for e in equations],'Six numbered OMML equations changed'
    for i,n in enumerate(nodes):
        if i not in edits:assert etree.tostring(n)==before_nodes[i],('Unrelated body edit',i)
    plain=text(body)
    obsolete=['扩展权重','调查外生产','补充生产','扩展到部门总体','补充调查外']
    assert not any(s in plain for s in obsolete),'Population extrapolation remains'
    assert '假定税调样本能够反映该部门' in plain
    assert '强度未知或无法预测的记录保持缺失' in plain
    assert len(body.findall('w:tbl',NS))==3
    labels=[int(re.search(r'（A(\d+)）$',text(p))[1]) for p in equations]
    assert labels==list(range(1,7)),labels
    flags_changed=[]
    blobs['word/document.xml']=xml(root)
    for name,data in list(blobs.items()):
        if name.startswith('word/') and name.endswith('.xml'):
            tree=root if name=='word/document.xml' else etree.fromstring(data);changed=False
            for tag in ['keepNext','keepLines','pageBreakBefore']:
                for item in tree.findall('.//w:'+tag,NS):
                    if item.get(W+'val','true').lower() not in ['0','false','off']:
                        item.set(W+'val','0');changed=True;flags_changed.append([name,tag])
            if changed:blobs[name]=xml(tree)
    # Build in memory and replace only if the user's current file still matches.
    buf=io.BytesIO()
    with ZipFile(buf,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():z.writestr(name,data)
    result=buf.getvalue()
    with ZipFile(io.BytesIO(result)) as z:assert z.testzip() is None
    temp=BASE/'publish.tmp';temp.write_bytes(result)
    assert sha(TARGET.read_bytes())==EXPECTED,'User edited the file during preparation; do not overwrite'
    os.replace(temp,TARGET)
    (BASE/'changes.json').write_text(json.dumps(edits,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'final_actual.txt').write_text('\n\n'.join(f'[{i}] {text(n)}' for i,n in enumerate(body)),encoding='utf-8')
    metadata={'path':str(TARGET),'before_sha256':EXPECTED,'after_sha256':sha(result),'changed_body_blocks':sorted(edits),'numbered_equations_unchanged':True,'numbered_equations':labels,'tables':3,'pagination_flags_disabled':flags_changed,'only_document_overwritten':str(TARGET)}
    (BASE/'build_meta.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(metadata,ensure_ascii=False,indent=2))
