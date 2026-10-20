from pathlib import Path
import hashlib, json, re, zipfile
from lxml import etree
import pymupdf as fitz

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
meta=json.loads((BASE/'build_meta.json').read_text(encoding='utf-8'))
checks=[]
def check(name,actual,expected=True):
    ok=actual==expected
    checks.append({'check':name,'passed':ok,'actual':actual,'expected':expected})
    assert ok,(name,actual,expected)

check('original_v33_sha256',sha(ROOT/'企业微观层面_v3.3.docx'),'6caf8e57849bc454f5a695c412ab962680e5460cf1fa310cb0df61d3eefc017c')
for item,folder,pagecount in zip(meta['outputs'],['final','note_final2'],[18,2]):
    p=Path(item['path']);name=p.name
    check(name+': unchanged since build',sha(p),item['sha256'])
    check(name+': nonempty',p.stat().st_size>15000)
    with zipfile.ZipFile(p) as z:
        check(name+': ZIP integrity',z.testzip(),None)
        bad=[]
        for fn in z.namelist():
            if fn.startswith('word/') and fn.endswith('.xml'):
                x=etree.fromstring(z.read(fn))
                for tag in ['keepNext','keepLines','pageBreakBefore']:
                    for e in x.findall('.//w:'+tag,NS):
                        if e.get('{'+NS['w']+'}val','true') not in ['0','false','off']:
                            bad.append((fn,tag))
        check(name+': pagination controls disabled in all parts/styles',bad,[])
        x=etree.fromstring(z.read('word/document.xml'))
        check(name+': no tracked insertions/deletions',len(x.xpath('.//w:ins|.//w:del',namespaces=NS)),0)
        check(name+': no rasterized content',len(x.xpath('.//w:drawing|.//w:pict',namespaces=NS)),0)
        raw=''.join(x.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
        check(name+': no raw TeX markers',('$' in raw or '\\tag' in raw or '\\frac' in raw),False)
        check(name+': no Unicode replacement glyph','\ufffd' in raw,False)
        if folder=='final':
            check(name+': native OMML objects',len(x.findall('.//m:oMath',NS)),69)
            tags=[]
            for para in x.findall('.//w:body/w:p',NS):
                if para.find('m:oMath',NS) is not None:
                    s=''.join(para.xpath('.//w:t/text()',namespaces=NS))
                    m=re.fullmatch(r'\s*（A(\d+)）\s*',s)
                    if m:tags.append(int(m.group(1)))
            check(name+': 16 display equation numbers',tags,list(range(1,17)))
            check(name+': editable flowchart plus 2 tables',len(x.findall('.//w:tbl',NS)),3)
            heads=x.xpath('.//w:p[w:pPr/w:pStyle[@w:val="Heading1"]]//w:t/text()',namespaces=NS)
            check(name+': 7 main sections plus references',len(heads),8)
            refs=re.findall(r'\[(\d+)\]',raw[raw.index('参考文献与资料说明'):])
            check(name+': 14 references',refs,[str(i) for i in range(1,15)])
    render=BASE/'render'/folder
    rm=json.loads((render/'render_meta.json').read_text(encoding='utf-8-sig'))
    check(name+': Microsoft Word opens and paginates',rm['pages'],pagecount)
    if folder=='final':check(name+': Word recognizes native equations',rm['math'],69)
    pdf=fitz.open(render/'document.pdf')
    check(name+': PDF page count',len(pdf),pagecount)
    check(name+': no empty rendered pages',all(len(pg.get_text().strip())>100 for pg in pdf))
    # A4 text is searchable; allow punctuation hanging outside the text measure, never outside paper.
    check(name+': text stays on paper',all(all(b[0]>=0 and b[1]>=0 and b[2]<=pg.rect.width+1 and b[3]<=pg.rect.height+1 for b in pg.get_text('blocks')) for pg in pdf))

protected={
 '中国国民经济行业标准/GBT 4754—2017/国民经济行业分类.pdf':'edc8f135ef8242cc634e05a0d29331c00342cf58211776e57d4a838be9618c05',
 '中国国民经济行业标准/GBT 4754—2017/2017版第1号修改单.DOCX':'59e792fca597e715b2afbc3496eb719702706d68bca943e5c24df2f07220d92a',
 '中国国民经济行业标准/1994-2002和2002-2011/GBT 4754—2002和GBT 4754—2011对照表.xls':'844da4a926e72978c2a8c93211817f78a17b26bc50c0a5b322f07ddf7f2412b9',
 'OECD_AMNE/2024版/readme-aamne.xlsx':'c550896f5e9c392ec0dd396c45dad9cd0d43598565a912d6fb9de5dfd336cbd1'
}
for path,h in protected.items():check('protected source unchanged: '+path,sha(ROOT/path),h)
for old,new,count in [('round5','final',18),('note_final','note_final2',2)]:
    for i in range(1,count+1):
        check(f'{new} page {i}: identical to visually reviewed render',sha(BASE/'render'/old/f'page-{i}.png'),sha(BASE/'render'/new/f'page-{i}.png'))
result={'all_passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'outputs':meta['outputs'],'render_main':'render/final','render_note':'render/note_final2','scope':'Document revision and read-only source inspection; no matching, regression, or structural estimation performed.'}
(BASE/'qa'/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'all_passed':result['all_passed'],'checks':len(checks),'pages':[18,2],'equations':16,'native_math_objects':69},ensure_ascii=False))
