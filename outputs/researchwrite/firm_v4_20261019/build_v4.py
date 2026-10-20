from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
import copy, re, json, hashlib, importlib.util
from edits_v4 import EDITS, FLOW, TABLE_A1, TABLE_A2, A3, REFERENCE_17

ROOT=Path(r'A:\桌面\study'); BASE=Path(__file__).resolve().parent
SOURCE=ROOT/'企业微观层面_v3.37.docx'; OUT=ROOT/'企业微观层面_v4.docx'
EXPECTED='f7792b617b2237c50d42f25ac76a2fe0e25aa641ddc2e9e4532e45384554d271'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}'; M='{'+NS['m']+'}'; SPACE='{http://www.w3.org/XML/1998/namespace}space'
sp=importlib.util.spec_from_file_location('math_helper',ROOT/'outputs/researchwrite/firm_v335_20261013/build_v335.py')
helper=importlib.util.module_from_spec(sp); sp.loader.exec_module(helper)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xb(x):return etree.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
def el(n):return etree.Element(W+n)
def text_of(e):return ''.join(e.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
def shift(s):return re.sub(r'（A(\d+)）',lambda m:'（A'+str(int(m[1])+2)+'）',s)

def run(p,txt,rp):
    r=el('r')
    if rp is not None:r.append(copy.deepcopy(rp))
    for t in re.split('(\n|\t)',txt):
        if not t:continue
        if t=='\n':r.append(el('br'))
        elif t=='\t':r.append(el('tab'))
        else:
            q=el('t');q.text=t;q.set(SPACE,'preserve');r.append(q)
    p.append(r)

def replace(p,txt,size=12):
    rp=p.find('w:r/w:rPr',NS);rp=copy.deepcopy(rp) if rp is not None else None
    for c in list(p):
        if c.tag!=W+'pPr':p.remove(c)
    for tok in re.split(r'(\$[^$]+\$)',txt):
        if not tok:continue
        if tok.startswith('$') and tok.endswith('$'):p.append(helper.math_el(tok[1:-1],size))
        else:run(p,tok,rp)

def fill_table(tab,rows,widths=None):
    templates=[copy.deepcopy(r) for r in tab.findall('w:tr',NS)]
    for r in tab.findall('w:tr',NS):tab.remove(r)
    if widths is not None:
        grid=tab.find('w:tblGrid',NS)
        for c in list(grid):grid.remove(c)
        for width in widths:
            c=el('gridCol');c.set(W+'w',str(width));grid.append(c)
    for i,values in enumerate(rows):
        template=templates[0] if i==0 else templates[-1] if i==len(rows)-1 else templates[min(i,len(templates)-2)]
        tr=copy.deepcopy(template);cells=tr.findall('w:tc',NS)
        while len(cells)>len(values):tr.remove(cells.pop())
        assert len(cells)==len(values)
        for j,(cell,txt) in enumerate(zip(cells,values)):
            ps=cell.findall('w:p',NS)
            for q in ps[1:]:cell.remove(q)
            replace(ps[0],txt,10.5)
            if widths is not None:
                pr=cell.find('w:tcPr',NS);tcw=pr.find('w:tcW',NS)
                if tcw is None:tcw=el('tcW');pr.insert(0,tcw)
                tcw.set(W+'w',str(widths[j]));tcw.set(W+'type','dxa')
        # Only first row is a repeated header; no fixed heights.
        pr=tr.find('w:trPr',NS)
        if pr is None:pr=el('trPr');tr.insert(0,pr)
        for h in pr.findall('w:tblHeader',NS):pr.remove(h)
        for h in pr.findall('w:trHeight',NS):pr.remove(h)
        if i==0:pr.append(el('tblHeader'))
        tab.append(tr)

def ordinary_before(target):
    p=el('p');pr=el('pPr');p.append(pr)
    s=el('spacing');s.set(W+'before','0');s.set(W+'after','0');s.set(W+'line','20');s.set(W+'lineRule','exact');pr.append(s)
    ind=el('ind');ind.set(W+'firstLine','0');pr.append(ind)
    r=el('r');rp=el('rPr');sz=el('sz');sz.set(W+'val','2');rp.append(sz);r.append(rp)
    br=el('br');br.set(W+'type','page');r.append(br);p.append(r);target.addprevious(p)

if __name__=='__main__':
    assert sha(SOURCE)==EXPECTED,'Input changed; reread before modifying'
    meta_file=BASE/'build_meta.json'
    if OUT.exists():
        prior=json.loads(meta_file.read_text(encoding='utf-8')) if meta_file.exists() else {}
        assert sha(OUT)==prior.get('output_sha256'),'Existing output is not ours; preserve'
    with ZipFile(SOURCE) as z:blobs={n:z.read(n) for n in z.namelist()}
    root=etree.fromstring(blobs['word/document.xml']);body=root.find('w:body',NS);nodes=list(body)
    original=''.join(text_of(n) for n in nodes)
    # Number existing equations and references after the two new scoring equations.
    for t in root.xpath('//w:t|//m:t',namespaces=NS):
        if t.text:
            t.text=shift(t.text)
            if t.tag==W+'t' and re.fullmatch(r'A\d+',t.text):t.text='A'+str(int(t.text[1:])+2)
            if t.tag==M+'t' and t.text=='Restrict':t.text='Intensity'
    for e in root.xpath('//w:br[@w:type="page"]|//w:lastRenderedPageBreak',namespaces=NS):e.getparent().remove(e)
    for i,txt in EDITS.items():
        replace(nodes[i],shift(txt),11 if i==3 else 12)
    fill_table(nodes[4],FLOW)
    fill_table(nodes[23],TABLE_A1,[1701,3402,4138])
    section=[]
    for kind,txt in A3:
        if kind=='table':
            p=copy.deepcopy(nodes[42]);fill_table(p,TABLE_A2,[1530,3530,4181])
        else:
            template={'h1':32,'h2':33,'cap':41,'p':34,'eq1':60,'eq2':60}[kind]
            p=copy.deepcopy(nodes[template])
            if kind.startswith('eq'):
                number=int(kind[-1]);replace(p,'\t$'+txt+'$\t（A'+str(number)+'）',11)
            else:replace(p,txt,11 if kind=='cap' else 12)
        section.append(p)
    for p in section:nodes[32].addprevious(p)
    for i in range(32,47):body.remove(nodes[i])
    reference=copy.deepcopy(nodes[148]);replace(reference,REFERENCE_17,10.5);nodes[148].addnext(reference)
    # Remove obsolete empty pagination paragraphs.
    for p in list(body):
        if p.tag==W+'p' and not text_of(p) and p.find('m:oMath',NS) is None:body.remove(p)
    # Optional manual layout breaks are ordinary page breaks and are rebuilt deterministically.
    layout_file=BASE/'layout_breaks.json'
    layout=json.loads(layout_file.read_text(encoding='utf-8')) if layout_file.exists() else ['A.1 研究问题、政策背景与作用机制']
    for title in layout:
        hits=[p for p in body if text_of(p)==title]
        assert len(hits)==1,(title,len(hits));ordinary_before(hits[0])
    # Canonical rule is enforced in all parts, including unused/base/table styles.
    blobs['word/document.xml']=xb(root)
    for n,b in list(blobs.items()):
        if n.startswith('word/') and n.endswith('.xml'):
            tree=root if n=='word/document.xml' else etree.fromstring(b)
            for tag in ['keepNext','keepLines','pageBreakBefore']:
                for e in tree.findall('.//w:'+tag,NS):e.set(W+'val','0')
            if n=='word/styles.xml':
                defaults=tree.find('w:docDefaults/w:pPrDefault/w:pPr',NS)
                if defaults is not None:
                    for tag in ['keepNext','keepLines','pageBreakBefore']:
                        q=defaults.find('w:'+tag,NS)
                        if q is None:q=el(tag);defaults.append(q)
                        q.set(W+'val','0')
            blobs[n]=xb(tree)
    core=etree.fromstring(blobs['docProps/core.xml'])
    nsc={'dc':'http://purl.org/dc/elements/1.1/'}
    for tag,value in [('title','企业所受到的清单限制强度与经营表现及部门成本分析'),('subject','年度企业面板研究方案 v4')]:
        e=core.find('dc:'+tag,nsc)
        if e is not None:e.text=value
    blobs['docProps/core.xml']=xb(core)
    with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
        for n,b in blobs.items():z.writestr(n,b)
    assert sha(SOURCE)==EXPECTED
    record=[]
    for i,e in enumerate(body):
        if e.tag==W+'tbl':txt='\n'.join(' | '.join(text_of(c) for c in row.findall('w:tc',NS)) for row in e.findall('w:tr',NS))
        else:txt=text_of(e)
        record.append({'i':i,'tag':etree.QName(e).localname,'text':txt})
    (BASE/'final_actual.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'final_actual.txt').write_text('\n\n'.join(f"[{q['i']:03} {q['tag']}] {q['text']}" for q in record),encoding='utf-8')
    meta={'source':str(SOURCE),'source_sha256':EXPECTED,'output':str(OUT),'output_sha256':sha(OUT),'source_characters':len(original),'final_characters':sum(len(q['text']) for q in record),'revised_slots':len(EDITS),'new_scoring_equations':2,'native_math_objects':len(root.findall('.//m:oMath',NS)),'ordinary_page_break_targets':layout}
    meta_file.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'math_manifest.json').write_text(json.dumps(helper.MATH_LOG,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False,indent=2))
