from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree
import copy,sys,json,hashlib,re,importlib.util
from content_v41 import CONTENT,SCORE,REFERENCES

ROOT=Path(r'A:\桌面\study');BASE=Path(__file__).resolve().parent
SOURCE=ROOT/'企业微观层面_v4.docx';OUT=ROOT/'企业微观层面_v4.1.docx'
EXPECTED='26c16648f50072f6125625bf443163d0ed9291e925d30131b2349ba0b38513ef'
sys.path.insert(0,str(ROOT/'outputs/researchwrite/firm_v4_20261019'))
spec=importlib.util.spec_from_file_location('previous_builder',ROOT/'outputs/researchwrite/firm_v4_20261019/build_v4.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
NS=h.NS;W=h.W;M=h.M
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text_of(p):return h.text_of(p)
def xb(e):return h.xb(e)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    assert sha(SOURCE)==EXPECTED,'Current source changed: preserve and reread'
    mf=BASE/'build_meta.json'
    if OUT.exists():
        prior=json.loads(mf.read_text(encoding='utf-8')) if mf.exists() else {}
        assert sha(OUT)==prior.get('output_sha256'),'Another writer owns current output'
    with ZipFile(SOURCE) as z:blobs={n:z.read(n) for n in z.namelist()}
    r=etree.fromstring(blobs['word/document.xml']);b=r.find('w:body',NS);nodes=list(b)
    source_chars=sum(len(text_of(e)) for e in nodes)
    # Copy only approved content into the current file's own formatting templates.
    for e in list(b):
        if e.tag!=W+'sectPr':b.remove(e)
    sect=b.find('w:sectPr',NS)
    def append(e):
        if sect is not None:sect.addprevious(e)
        else:b.append(e)
    for kind,txt in CONTENT:
        if kind=='flow':
            e=copy.deepcopy(nodes[4])
        elif kind=='score':
            e=copy.deepcopy(nodes[40]);h.fill_table(e,SCORE,[1600,3050,4591])
        else:
            template=0 if kind=='title' else 3 if kind=='cap' else 5 if kind=='note' else 7 if kind=='h1' else 136 if kind=='refhead' else 66 if kind.startswith('eq') else 20
            e=copy.deepcopy(nodes[template])
            size=10 if kind=='note' else 11 if kind=='cap' or kind.startswith('eq') else 12
            if kind.startswith('eq'):
                num=int(kind[-1]);h.replace(e,'\t$'+txt+'$\t（A'+str(num)+'）',size)
            else:h.replace(e,txt,size)
        append(e)
    for indices,txt in REFERENCES:
        e=copy.deepcopy(nodes[indices[0]])
        links=[]
        for index in indices:links.extend(copy.deepcopy(x) for x in nodes[index].findall('w:hyperlink',NS))
        h.replace(e,txt,10.5)
        rp=e.find('w:r/w:rPr',NS)
        if links:
            h.run(e,' ',rp)
            for k,link in enumerate(links):
                if k:h.run(e,'；',rp)
                e.append(link)
            h.run(e,'。',rp)
        append(e)
    # Remove all inherited/obsolete breaks; use approved ordinary manual breaks.
    for x in r.xpath('//w:br[@w:type="page"]|//w:lastRenderedPageBreak',namespaces=NS):x.getparent().remove(x)
    layout_file=BASE/'layout_breaks.json'
    layout=json.loads(layout_file.read_text(encoding='utf-8')) if layout_file.exists() else ['A.1 研究问题与作用机制']
    for heading in layout:
        found=[p for p in b if text_of(p)==heading]
        assert len(found)==1,heading
        h.ordinary_before(found[0])
    blobs['word/document.xml']=xb(r)
    for name,data in list(blobs.items()):
        if name.startswith('word/') and name.endswith('.xml'):
            tree=r if name=='word/document.xml' else etree.fromstring(data)
            for tag in ['keepNext','keepLines','pageBreakBefore']:
                for x in tree.findall('.//w:'+tag,NS):x.set(W+'val','0')
            blobs[name]=xb(tree)
    core=etree.fromstring(blobs['docProps/core.xml']);dc={'dc':'http://purl.org/dc/elements/1.1/'}
    subject=core.find('dc:subject',dc)
    if subject is not None:subject.text='企业微观研究讨论方案 v4.1'
    blobs['docProps/core.xml']=xb(core)
    with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
        for name,data in blobs.items():z.writestr(name,data)
    assert sha(SOURCE)==EXPECTED
    actual=[]
    for i,e in enumerate(b):
        if e.tag==W+'tbl':txt='\n'.join(' | '.join(text_of(c) for c in row.findall('w:tc',NS)) for row in e.findall('w:tr',NS))
        else:txt=text_of(e)
        actual.append({'i':i,'tag':etree.QName(e).localname,'text':txt})
    (BASE/'final_actual.json').write_text(json.dumps(actual,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'final_actual.txt').write_text('\n\n'.join(f"[{x['i']}] {x['text']}" for x in actual),encoding='utf-8')
    meta={'source':str(SOURCE),'source_sha256':EXPECTED,'output':str(OUT),'output_sha256':sha(OUT),'source_characters':source_chars,'final_characters':sum(len(text_of(e)) for e in b),'numbered_equations':6,'native_math':len(r.findall('.//m:oMath',NS)),'tables':len(b.findall('w:tbl',NS)),'layout_breaks':layout,'approval':'User: 全部同意; scoped table in previous turn'}
    mf.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'math_manifest.json').write_text(json.dumps(h.helper.MATH_LOG,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False,indent=2))
