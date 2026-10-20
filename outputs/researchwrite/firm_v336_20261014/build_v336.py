from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
import copy, re, json, hashlib, importlib.util
from edits_v336 import EDITS, EQUATIONS, FLOW, TABLE_A2, EXTRA_REFS

ROOT=Path(r'A:\桌面\study')
BASE=Path(__file__).resolve().parent
SOURCE=ROOT/'企业微观层面_v3.35.docx'
OUT=ROOT/'企业微观层面_v3.36.docx'
EXPECTED='580f238eb7513b83edac094d2c3438617815d84d5815abf2fc4958993dd751e6'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
W='{'+NS['w']+'}';M='{'+NS['m']+'}';R='{'+NS['r']+'}'
XMLSPACE='{http://www.w3.org/XML/1998/namespace}space'
spec=importlib.util.spec_from_file_location('math_helper',ROOT/'outputs/researchwrite/firm_v335_20261013/build_v335.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xb(x):return etree.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
def el(n):return etree.Element(W+n)
def text_of(p):return ''.join(p.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
def run(p,text,rpr=None):
    r=el('r')
    if rpr is not None:r.append(copy.deepcopy(rpr))
    parts=re.split('(\n|\t)',text)
    for t in parts:
        if not t:continue
        if t=='\n':r.append(el('br'))
        elif t=='\t':r.append(el('tab'))
        else:
            q=el('t');q.text=t;q.set(XMLSPACE,'preserve');r.append(q)
    p.append(r)
    return r

def clear(p):
    rpr=p.find('w:r/w:rPr',NS)
    rpr=copy.deepcopy(rpr) if rpr is not None else None
    for c in list(p):
        if c.tag!=W+'pPr':p.remove(c)
    return rpr

def append_inline(p,text,rpr,size):
    pattern=r'(\$[^$]+\$|`[^`]+`|\[[^\]]+\]\(https?://[^)]+\))'
    for token in re.split(pattern,text):
        if not token:continue
        if token.startswith('$') and token.endswith('$'):
            p.append(helper.math_el(token[1:-1],size))
        elif token.startswith('`'):
            rp=copy.deepcopy(rpr) if rpr is not None else el('rPr')
            fonts=rp.find('w:rFonts',NS)
            if fonts is None:fonts=el('rFonts');rp.insert(0,fonts)
            fonts.set(W+'ascii','Consolas');fonts.set(W+'hAnsi','Consolas')
            run(p,token[1:-1],rp)
        elif re.fullmatch(r'\[[^\]]+\]\(https?://[^)]+\)',token):
            label,url=re.match(r'\[([^\]]+)\]\(([^)]+)\)',token).groups()
            rid='rIdV336_'+str(len(newlinks)+1)
            rel=etree.SubElement(rels,'{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')
            rel.set('Id',rid);rel.set('Type',NS['r']+'/hyperlink');rel.set('Target',url);rel.set('TargetMode','External')
            newlinks.append(url)
            h=el('hyperlink');h.set(R+'id',rid)
            rp=copy.deepcopy(rpr) if rpr is not None else el('rPr')
            c=rp.find('w:color',NS)
            if c is None:c=el('color');rp.append(c)
            c.set(W+'val','234A70')
            run(h,label,rp);p.append(h)
        else:run(p,token,rpr)

def replace(p,text,size=12):
    rp=clear(p);append_inline(p,text,rp,size)

def ordinary_before(target):
    p=el('p');pp=etree.SubElement(p,W+'pPr');sp=etree.SubElement(pp,W+'spacing');sp.set(W+'line','20');sp.set(W+'lineRule','exact');sp.set(W+'before','0');sp.set(W+'after','0')
    ind=etree.SubElement(pp,W+'ind');ind.set(W+'firstLine','0')
    target.addprevious(p)
    r=el('r');rp=el('rPr');sz=el('sz');sz.set(W+'val','2');rp.append(sz);r.append(rp)
    br=el('br');br.set(W+'type','page');r.append(br);p.append(r)

def fill_table(tab,rows):
    oldrows=tab.findall('w:tr',NS)
    templates=[copy.deepcopy(r) for r in oldrows]
    for r in oldrows:tab.remove(r)
    for i,values in enumerate(rows):
        template=templates[0] if i==0 else (templates[-1] if i==len(rows)-1 else templates[min(i,len(templates)-2)])
        r=copy.deepcopy(template);cells=r.findall('w:tc',NS)
        assert len(cells)==len(values),(i,len(cells),len(values))
        for c,value in zip(cells,values):
            pars=c.findall('w:p',NS)
            p=pars[0]
            for pp in pars[1:]:c.remove(pp)
            replace(p,value,10.5)
        tab.append(r)

if __name__=='__main__':
    assert sha(SOURCE)==EXPECTED,'Source changed; reread required'
    priorpath=BASE/'build_meta.json'
    if OUT.exists():
        prior=json.loads(priorpath.read_text(encoding='utf-8')) if priorpath.exists() else {}
        assert prior.get('output_sha256')==sha(OUT),'Existing output modified outside this build; preserve'
    with ZipFile(SOURCE) as z:blobs={n:z.read(n) for n in z.namelist()}
    x=etree.fromstring(blobs['word/document.xml']);body=x.find('w:body',NS);source_nodes=list(body)
    rels=etree.fromstring(blobs['word/_rels/document.xml.rels']);newlinks=[]
    # Clear old layout decisions before revising all affected semantic slots.
    for br in x.xpath('//w:br[@w:type="page"]|//w:lastRenderedPageBreak',namespaces=NS):br.getparent().remove(br)
    for i,txt in EDITS.items():replace(source_nodes[i],txt,10.5 if i>=156 else (10 if i in [5,26] else (11 if i in [3,24,51] else 12)))
    for i,(tex,number) in EQUATIONS.items():
        p=source_nodes[i];rp=clear(p);run(p,'\t',rp)
        p.append(helper.math_el(tex,11 if number in ['A2','A9'] else 12));run(p,'\t（'+number+'）',rp)
    fill_table(source_nodes[4],FLOW)
    a1=json.loads((BASE/'table_a1.json').read_text(encoding='utf-8'))
    fill_table(source_nodes[25],a1)
    fill_table(source_nodes[52],TABLE_A2)
    for txt in EXTRA_REFS:
        p=copy.deepcopy(source_nodes[169]);replace(p,txt,10.5);source_nodes[170].addprevious(p)
    # Preserve reference page geometry and footer bytes; only ordinary page breaks.
    layoutfile=BASE/'layout_breaks.json'
    layout=json.loads(layoutfile.read_text(encoding='utf-8')) if layoutfile.exists() else [7,24,40,71,124,130,147,155]
    for i in layout:ordinary_before(source_nodes[i])
    for n,b in list(blobs.items()):
        if n.startswith('word/') and n.endswith('.xml'):
            tree=x if n=='word/document.xml' else etree.fromstring(b)
            changed=False
            for tag in ['keepNext','keepLines','pageBreakBefore']:
                for e in tree.findall('.//w:'+tag,NS):
                    if e.get(W+'val','true') not in ['0','false','off']:
                        e.set(W+'val','0');changed=True
            if changed or n=='word/document.xml':blobs[n]=xb(tree)
    blobs['word/_rels/document.xml.rels']=xb(rels)
    core=etree.fromstring(blobs['docProps/core.xml'])
    cns={'dc':'http://purl.org/dc/elements/1.1/','cp':'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'}
    for tag,txt in [('dc:title',EDITS[0]),('dc:subject','年度外资准入限制与企业面板研究方案'),('cp:keywords','外资准入; Restrict; 企业面板; PPML; AMNE; 跨国生产')]:
        e=core.find(tag,cns)
        if e is not None:e.text=txt
    blobs['docProps/core.xml']=xb(core)
    with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
        for n,b in blobs.items():z.writestr(n,b)
    assert sha(SOURCE)==EXPECTED
    meta={'source':str(SOURCE),'source_sha256':EXPECTED,'output':str(OUT),'output_sha256':sha(OUT),'revised_body_slots':len(EDITS),'revised_display_equations':len(EQUATIONS),'math_objects':len(x.findall('.//m:oMath',NS)),'source_index_page_breaks':layout,'links_added':len(newlinks),'preserved_parts':[n for n,b in blobs.items() if n not in ['word/document.xml','word/_rels/document.xml.rels','docProps/core.xml']],'math_engine':'latex2mathml + Microsoft MML2OMML','notes':'Source style/geometry/footer preserved; all prohibited pagination controls disabled.'}
    priorpath.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'math_manifest.json').write_text(json.dumps(helper.MATH_LOG,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=[f'[{i:03d} {etree.QName(e).localname}] {text_of(e)}' for i,e in enumerate(body)]
    (BASE/'v336_actual.txt').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({k:meta[k] for k in ['output_sha256','revised_body_slots','math_objects','links_added']},ensure_ascii=False))
