from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
from difflib import SequenceMatcher
import json, re, hashlib, copy

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
SOURCE=BASE/'sources/current_before.docx'
TARGET=ROOT/'企业微观层面_v3.35.docx'
EXPECTED='797a3563f9d79acb77d41ef63ea2226f07c9b12f5f0c55f001b760060f776f5f'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}';M='{'+NS['m']+'}'
XMLSPACE='{http://www.w3.org/XML/1998/namespace}space'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xmlbytes(x):return etree.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
def paragraph_text(p):
    text='';n=0
    for c in p:
        if c.tag==W+'pPr':continue
        if c.tag in [M+'oMath',M+'oMathPara']:
            text+='{{M'+str(n)+'}}';n+=1
        else:text+=''.join(c.xpath('.//w:t/text()',namespaces=NS))
    return text

def replace_segment(nodes,old,new):
    assert ''.join(n.text or '' for n in nodes)==old
    if old==new:return
    if not nodes:raise ValueError('No text node for insertion')
    spans=[];pos=0
    for node in nodes:
        n=len(node.text or '');spans.append((pos,pos+n,node));pos+=n
    for op,a,b,c,d in reversed(SequenceMatcher(None,old,new,autojunk=False).get_opcodes()):
        if op=='equal':continue
        replacement=new[c:d]
        if a==b:
            # At a run boundary, prefer the preceding run's style; at start use the first.
            candidates=[x for x in spans if x[0]<a<=x[1]]
            st,en,node=candidates[-1] if candidates else spans[0]
            ix=a-st;s=node.text or '';node.text=s[:ix]+replacement+s[ix:]
            node.set(XMLSPACE,'preserve');continue
        hits=[x for x in spans if x[0]<b and x[1]>a]
        if not hits:raise ValueError((old,new,a,b))
        for index,(st,en,node) in enumerate(hits):
            s=node.text or '';lo=max(a-st,0);hi=min(b-st,en-st)
            node.text=s[:lo]+(replacement if index==0 else '')+s[hi:]
            node.set(XMLSPACE,'preserve')
    assert ''.join(n.text or '' for n in nodes)==new, (old,new,''.join(n.text or '' for n in nodes))

def patch_paragraph(p,old,new):
    assert paragraph_text(p)==old
    old_tokens=re.findall(r'\{\{M\d+\}\}',old)
    assert re.findall(r'\{\{M\d+\}\}',new)==old_tokens,'Native math sequence changed'
    chunks=re.split(r'\{\{M\d+\}\}',new)
    groups=[[]]
    for c in p:
        if c.tag==W+'pPr':continue
        if c.tag in [M+'oMath',M+'oMathPara']:groups.append([])
        else:groups[-1].extend(c.xpath('.//w:t',namespaces=NS))
    for nodes,after in zip(groups,chunks):replace_segment(nodes,''.join(n.text or '' for n in nodes),after)
    assert paragraph_text(p)==new

if __name__=='__main__':
    assert sha(SOURCE)==EXPECTED,'Snapshot changed'
    assert sha(TARGET)==EXPECTED,'Current Word changed externally; review required'
    patches=json.loads((BASE/'approved_edits.json').read_text(encoding='utf-8'))
    assert len({r['p'] for r in patches})==len(patches)
    with ZipFile(SOURCE) as z:
        blobs={i.filename:z.read(i.filename) for i in z.infolist()}
    x=etree.fromstring(blobs['word/document.xml']);paras=x.xpath('//w:body//w:p',namespaces=NS)
    paragraph_before=[etree.tostring(p) for p in paras]
    math_before=[etree.tostring(e) for e in x.findall('.//m:oMath',NS)]
    footers_before={n:b for n,b in blobs.items() if re.match(r'word/footer\d+\.xml$',n)}
    for r in patches:patch_paragraph(paras[r['p']],r['old'],r['new'])
    # Rebuild explicit line breaks only in the revised editable flow cell.
    flow_file=BASE/'flow_lines.json'
    flow=json.loads(flow_file.read_text(encoding='utf-8')) if flow_file.exists() else {}
    for key,lines in flow.items():
        p=paras[int(key)]
        assert ''.join(lines)==paragraph_text(p)
        rpr=copy.deepcopy(p.find('.//w:rPr',NS))
        for child in list(p):
            if child.tag!=W+'pPr':p.remove(child)
        run=etree.SubElement(p,W+'r')
        if rpr is not None:run.append(rpr)
        for index,line in enumerate(lines):
            if index:etree.SubElement(run,W+'br')
            node=etree.SubElement(run,W+'t');node.text=line;node.set(XMLSPACE,'preserve')
    # Remove ordinary breaks left at now inappropriate positions after prose revisions.
    removed_breaks=json.loads((BASE/'remove_breaks.json').read_text(encoding='utf-8'))
    for pid in removed_breaks:
        breaks=paras[pid].xpath('.//w:br[@w:type="page"]',namespaces=NS)
        assert len(breaks)==1,pid
        for br in breaks:br.getparent().remove(br)
    # Use ordinary page breaks for headings stranded by prose shortening.
    layout=json.loads((BASE/'layout_breaks.json').read_text(encoding='utf-8')) if (BASE/'layout_breaks.json').exists() else []
    for pid in layout:
        prior=paras[pid-1]
        assert not prior.xpath('.//w:br[@w:type="page"]',namespaces=NS)
        run=etree.Element(W+'r'); br=etree.SubElement(run,W+'br');br.set(W+'type','page');prior.append(run)
    # Insert short source/definition paragraphs using an existing body/note style.
    inserted={}
    insertions=json.loads((BASE/'insertions.json').read_text(encoding='utf-8')) if (BASE/'insertions.json').exists() else []
    for item in insertions:
        template=paras[item['style_from']]
        node=copy.deepcopy(template)
        for child in list(node):
            if child.tag!=W+'pPr':node.remove(child)
        for br in node.findall('.//w:br',NS):br.getparent().remove(br)
        run=etree.SubElement(node,W+'r')
        rpr=template.find('.//w:rPr',NS)
        if rpr is not None:run.append(copy.deepcopy(rpr))
        text=etree.SubElement(run,W+'t');text.text=item['text'];text.set(XMLSPACE,'preserve')
        anchor=paras[item.get('before',item.get('after'))]
        if 'before' in item:anchor.addprevious(node)
        else:anchor.addnext(node)
        inserted[item['id']]=node
    # Replace A2 with a native editable four-column table.
    table_file=BASE/'table_a2.json'
    if table_file.exists():
        table_spec=json.loads(table_file.read_text(encoding='utf-8'))
        table=x.findall('.//w:tbl',NS)[table_spec['index']]
        original_rows=table.findall('w:tr',NS)
        header_template=copy.deepcopy(original_rows[0].find('w:tc',NS))
        body_template=copy.deepcopy(original_rows[1].find('w:tc',NS))
        for oldrow in original_rows:table.remove(oldrow)
        grid=table.find('w:tblGrid',NS)
        for child in list(grid):grid.remove(child)
        for width in table_spec['widths']:etree.SubElement(grid,W+'gridCol').set(W+'w',str(width))
        for i,row in enumerate(table_spec['rows']):
            tr=etree.SubElement(table,W+'tr');trpr=etree.SubElement(tr,W+'trPr');etree.SubElement(trpr,W+'cantSplit')
            if i==0:etree.SubElement(trpr,W+'tblHeader')
            for value,width in zip(row,table_spec['widths']):
                cell=copy.deepcopy(header_template if i==0 else body_template)
                cell.find('w:tcPr/w:tcW',NS).set(W+'w',str(width))
                p=cell.find('w:p',NS);rpr=copy.deepcopy(p.find('.//w:rPr',NS))
                for child in list(p):
                    if child.tag!=W+'pPr':p.remove(child)
                run=etree.SubElement(p,W+'r');run.append(rpr)
                text=etree.SubElement(run,W+'t');text.text=value;text.set(XMLSPACE,'preserve')
                if i==len(table_spec['rows'])-1:
                    borders=cell.find('w:tcPr/w:tcBorders',NS)
                    for e in list(borders):
                        if e.tag==W+'bottom':borders.remove(e)
                    e=etree.SubElement(borders,W+'bottom');e.set(W+'val','single');e.set(W+'sz','10');e.set(W+'color','000000')
                tr.append(cell)
    # Remove every header type/section; leave footer and page-number fields intact.
    refs=x.findall('.//w:headerReference',NS)
    for e in refs:e.getparent().remove(e)
    rel=etree.fromstring(blobs['word/_rels/document.xml.rels'])
    for e in list(rel):
        if e.get('Type','').endswith('/header'):rel.remove(e)
    ct=etree.fromstring(blobs['[Content_Types].xml'])
    for e in list(ct):
        if re.match(r'/word/header\d+\.xml$',e.get('PartName','')):ct.remove(e)
    removed=[n for n in blobs if re.match(r'word/header\d+\.xml$',n) or re.match(r'word/_rels/header\d+\.xml\.rels$',n)]
    for n in removed:del blobs[n]
    blobs['word/document.xml']=xmlbytes(x)
    blobs['word/_rels/document.xml.rels']=xmlbytes(rel)
    blobs['[Content_Types].xml']=xmlbytes(ct)
    assert math_before==[etree.tostring(e) for e in x.findall('.//m:oMath',NS)],'Equations changed'
    assert footers_before=={n:b for n,b in blobs.items() if re.match(r'word/footer\d+\.xml$',n)},'Footer changed'
    # Paragraph controls were already disabled; retain this invariant in every part.
    for n,b in blobs.items():
        if n.startswith('word/') and n.endswith('.xml'):
            tree=etree.fromstring(b)
            for tag in ['keepNext','keepLines','pageBreakBefore']:
                assert all(e.get(W+'val','true') in ['0','false','off'] for e in tree.findall('.//w:'+tag,NS)),(n,tag)
    candidate=BASE/'v335_candidate.docx'
    with ZipFile(candidate,'w',ZIP_DEFLATED) as z:
        for name,blob in blobs.items():z.writestr(name,blob)
    current_paras=x.xpath('//w:body//w:p',namespaces=NS)
    orig_index={id(p):i for i,p in enumerate(paras)}
    insert_index={id(p):key for key,p in inserted.items()}
    records=[{'p':orig_index.get(id(p),insert_index.get(id(p),'table_a2_'+str(i))),'order':i,'text':paragraph_text(p)} for i,p in enumerate(current_paras) if paragraph_text(p)]
    origin_map={str(orig_index[id(p)]):i for i,p in enumerate(current_paras) if id(p) in orig_index}
    edited={r['p'] for r in patches};layout_prior={p-1 for p in layout}|set(removed_breaks)
    for key,index in origin_map.items():
        pid=int(key)
        if pid not in edited|layout_prior:assert paragraph_before[pid]==etree.tostring(current_paras[index]),('Untargeted paragraph changed',pid)
    (BASE/'qa/origin_map.json').write_text(json.dumps(origin_map,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'qa/candidate_paragraphs.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    audit={'source_sha256':EXPECTED,'candidate_sha256':sha(candidate),'changed_paragraphs':len(patches),'ordinary_breaks_before':layout,'removed_breaks_from':removed_breaks,'removed_header_parts':removed,'native_math_objects_unchanged':len(math_before),'footer_bytes_unchanged':True,'pagination_controls_disabled':True}
    (BASE/'qa/edit_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False))
