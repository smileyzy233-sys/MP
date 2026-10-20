from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
import copy,re,json,hashlib,importlib.util
from edits_v337 import EDITS,FLOW,TABLE_A1,TABLE_A2

ROOT=Path(r'A:\桌面\study');BASE=Path(__file__).resolve().parent
SOURCE=ROOT/'企业微观层面_v3.36.docx';OUT=ROOT/'企业微观层面_v3.37.docx'
EXPECTED='2819289f94e1cb07c84985832e95b0787dda4eb81762285288fd3ff669719744'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}';M='{'+NS['m']+'}';SPACE='{http://www.w3.org/XML/1998/namespace}space'
sp=importlib.util.spec_from_file_location('math_helper',ROOT/'outputs/researchwrite/firm_v335_20261013/build_v335.py')
helper=importlib.util.module_from_spec(sp);sp.loader.exec_module(helper)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xb(x):return etree.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
def el(n):return etree.Element(W+n)
def text_of(e):return ''.join(e.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
def run(p,text,rpr):
    r=el('r')
    if rpr is not None:r.append(copy.deepcopy(rpr))
    for t in re.split('(\n|\t)',text):
        if not t:continue
        if t=='\n':r.append(el('br'))
        elif t=='\t':r.append(el('tab'))
        else:
            q=el('t');q.text=t;q.set(SPACE,'preserve');r.append(q)
    p.append(r)

def replace(p,text,size=12,keep_links=False):
    rp=p.find('w:r/w:rPr',NS);rp=copy.deepcopy(rp) if rp is not None else None
    links=[copy.deepcopy(e) for e in p.findall('w:hyperlink',NS)] if keep_links else []
    for c in list(p):
        if c.tag!=W+'pPr':p.remove(c)
    for token in re.split(r'(\$[^$]+\$)',text):
        if not token:continue
        if token.startswith('$') and token.endswith('$'):p.append(helper.math_el(token[1:-1],size))
        else:run(p,token,rp)
    if links:
        run(p,' ',rp)
        for i,l in enumerate(links):
            if i:run(p,'；',rp)
            p.append(l)
        run(p,'。',rp)

def fill_table(tab,rows,widths=None):
    templates=[copy.deepcopy(r) for r in tab.findall('w:tr',NS)]
    for r in tab.findall('w:tr',NS):tab.remove(r)
    if widths is not None:
        grid=tab.find('w:tblGrid',NS)
        for c in list(grid):grid.remove(c)
        for w in widths:
            c=el('gridCol');c.set(W+'w',str(w));grid.append(c)
    for i,values in enumerate(rows):
        template=templates[0] if i==0 else (templates[-1] if i==len(rows)-1 else templates[min(i,len(templates)-2)])
        tr=copy.deepcopy(template);cells=tr.findall('w:tc',NS)
        while len(cells)>len(values):tr.remove(cells.pop())
        assert len(cells)==len(values)
        for j,(c,txt) in enumerate(zip(cells,values)):
            ps=c.findall('w:p',NS)
            for q in ps[1:]:c.remove(q)
            replace(ps[0],txt,10.5)
            if widths is not None:
                pr=c.find('w:tcPr',NS)
                tcw=pr.find('w:tcW',NS)
                if tcw is None:tcw=el('tcW');pr.insert(0,tcw)
                tcw.set(W+'w',str(widths[j]));tcw.set(W+'type','dxa')
        tab.append(tr)

def ordinary_before(target):
    p=el('p');pr=el('pPr');p.append(pr)
    s=el('spacing');s.set(W+'before','0');s.set(W+'after','0');s.set(W+'line','20');s.set(W+'lineRule','exact');pr.append(s)
    ind=el('ind');ind.set(W+'firstLine','0');pr.append(ind)
    r=el('r');rp=el('rPr');sz=el('sz');sz.set(W+'val','2');rp.append(sz);r.append(rp)
    br=el('br');br.set(W+'type','page');r.append(br);p.append(r);target.addprevious(p)

if __name__=='__main__':
    assert sha(SOURCE)==EXPECTED,'Actual source changed; preserve and reread'
    meta_file=BASE/'build_meta.json'
    if OUT.exists():
        prior=json.loads(meta_file.read_text(encoding='utf-8')) if meta_file.exists() else {}
        assert sha(OUT)==prior.get('output_sha256'),'Output changed by another writer; preserve'
    with ZipFile(SOURCE) as z:blobs={n:z.read(n) for n in z.namelist()}
    root=etree.fromstring(blobs['word/document.xml']);body=root.find('w:body',NS);nodes=list(body)
    original_text=''.join(text_of(n) for n in nodes)
    display_indices=[i for i,p in enumerate(nodes) if p.tag==W+'p' and p.xpath('./w:r/w:tab',namespaces=NS)]
    math_before=[etree.tostring(nodes[i]) for i in display_indices]
    for e in root.xpath('//w:br[@w:type="page"]|//w:lastRenderedPageBreak',namespaces=NS):e.getparent().remove(e)
    for i,txt in EDITS.items():
        if txt:
            size=10.5 if i>=161 else (10 if i==5 else (11 if i in [3,26,53] else 12))
            replace(nodes[i],txt,size,keep_links=i>=161)
        else:body.remove(nodes[i])
    # Remove empty old page-break paragraphs, retaining no obsolete pagination.
    for p in list(body):
        if p.tag==W+'p' and not text_of(p) and p.find('m:oMath',NS) is None:
            body.remove(p)
    fill_table(nodes[4],FLOW)
    fill_table(nodes[27],TABLE_A1,[1701,3402,4138])
    fill_table(nodes[54],TABLE_A2,[3288,1417,4536])
    layout_file=BASE/'layout_breaks.json'
    layout=json.loads(layout_file.read_text(encoding='utf-8')) if layout_file.exists() else [8]
    for i in layout:
        assert nodes[i].getparent() is body,(i,'removed pagination target')
        ordinary_before(nodes[i])
    assert math_before==[etree.tostring(nodes[i]) for i in display_indices],'Numbered equations changed'
    blobs['word/document.xml']=xb(root)
    for n,b in list(blobs.items()):
        if n.startswith('word/') and n.endswith('.xml'):
            tree=root if n=='word/document.xml' else etree.fromstring(b);changed=False
            for tag in ['keepNext','keepLines','pageBreakBefore']:
                for e in tree.findall('.//w:'+tag,NS):
                    if e.get(W+'val','true') not in ['0','false','off']:e.set(W+'val','0');changed=True
            if changed:blobs[n]=xb(tree)
    core=etree.fromstring(blobs['docProps/core.xml'])
    nsc={'dc':'http://purl.org/dc/elements/1.1/'}
    subject=core.find('dc:subject',nsc)
    if subject is not None:subject.text='年度外资准入限制与企业面板研究方案 v3.37'
    blobs['docProps/core.xml']=xb(core)
    with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
        for n,b in blobs.items():z.writestr(n,b)
    assert sha(SOURCE)==EXPECTED
    record=[{'i':i,'tag':etree.QName(e).localname,'text':text_of(e)} for i,e in enumerate(body)]
    (BASE/'final_actual.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'final_actual.txt').write_text('\n'.join(f"[{q['i']:03} {q['tag']}] {q['text']}" for q in record),encoding='utf-8')
    meta={'source':str(SOURCE),'source_sha256':EXPECTED,'output':str(OUT),'output_sha256':sha(OUT),'source_characters':len(original_text),'final_characters':sum(len(q['text']) for q in record),'deleted_body_slots':[i for i,t in EDITS.items() if not t],'revised_slots':len(EDITS),'preserved_numbered_equations':len(display_indices),'native_math_objects':len(root.findall('.//m:oMath',NS)),'ordinary_page_break_source_indices':layout}
    meta_file.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'math_manifest.json').write_text(json.dumps(helper.MATH_LOG,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False,indent=2))
