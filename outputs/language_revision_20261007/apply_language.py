from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json,hashlib,copy,re,difflib
from collections import Counter

ROOT=Path(__file__).resolve().parent
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}'
manifest=json.loads((ROOT/'source_manifest.json').read_text(encoding='utf-8'))
source=Path(manifest['source'])
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['sha256'],'Source changed after extraction; preserve latest edits'
records={r['id']:r for r in json.loads((ROOT/'current_paragraphs.json').read_text(encoding='utf-8'))}
edits={}
for filename in ['first_half_edits.json','second_half_edits.json','root_edits.json','root_overrides.json']:
    for e in json.loads((ROOT/filename).read_text(encoding='utf-8')):
        key=e['id'];assert key in records
        assert e['before']==records[key]['text'],('Original mismatch',key)
        assert records[key]['kind'] not in ['heading','caption','equation'],('Protected paragraph',key)
        if key in edits and filename!='root_overrides.json':raise ValueError('Duplicate edit '+key)
        assert re.findall(r'⟦[MK]\d{3}⟧',e['after'])==re.findall(r'⟦[MK]\d{3}⟧',e['before']),('Protected token changed',key)
        b=re.sub(r'⟦[MK]\d{3}⟧','',e['before']);a=re.sub(r'⟦[MK]\d{3}⟧','',e['after'])
        assert Counter(re.findall(r'\d+(?:\.\d+)?',b))==Counter(re.findall(r'\d+(?:\.\d+)?',a)),('Number changed',key)
        assert '\ufffd' not in a
        edits[key]=e

def format_key(pr):
    return etree.tostring(pr,method='c14n') if pr is not None else b''

def style_chars(runs):
    text='';props=[]
    for run in runs:
        part=''.join(run.xpath('.//w:t/text()',namespaces=NS))
        pr=run.find('w:rPr',NS)
        text+=part;props.extend([pr]*len(part))
    return text,props

def rewrite_text(old_runs,new):
    old,props=style_chars(old_runs)
    default=next((p for p in props if p is not None),None)
    output=[]
    for kind,i,j,k,l in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes():
        if kind=='equal':output.extend(zip(new[k:l],props[i:j]))
        elif kind in ['replace','insert']:
            pr=props[i] if i<len(props) else props[-1] if props else default
            output.extend((c,pr) for c in new[k:l])
    grouped=[]
    for ch,pr in output:
        key=format_key(pr)
        if grouped and grouped[-1][0]==key:grouped[-1][2]+=ch
        else:grouped.append([key,pr,ch])
    result=[]
    # Word's lastRenderedPageBreak is a non-printing layout cache, not a hard break.
    # Carry it without dropping user package features; Word recomputes pagination.
    for original in old_runs:
        for cache in original.findall('w:lastRenderedPageBreak',NS):
            run=etree.Element(W+'r')
            pr=original.find('w:rPr',NS)
            if pr is not None:run.append(copy.deepcopy(pr))
            run.append(copy.deepcopy(cache));result.append(run)
    for _,pr,text in grouped:
        if not text:continue
        run=etree.Element(W+'r')
        if pr is not None:run.append(copy.deepcopy(pr))
        t=etree.SubElement(run,W+'t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=text
        result.append(run)
    return result

def apply(p,key):
    e=edits[key];segments=[[]];protected=[]
    for child in p:
        tag=etree.QName(child).localname
        if tag=='pPr':continue
        if tag=='oMath':
            token=f'⟦M{len(protected)+1:03d}⟧';protected.append((token,child));segments.append([])
        elif tag=='r':
            text=''.join(child.xpath('.//w:t/text()',namespaces=NS))
            fonts=child.find('w:rPr/w:rFonts',NS)
            mono=fonts is not None and 'Consolas' in list(fonts.attrib.values())
            if mono and text:
                token=f'⟦K{len(protected)+1:03d}⟧';protected.append((token,child));segments.append([])
            else:
                unexpected=[etree.QName(c).localname for c in child if etree.QName(c).localname not in ['rPr','t','lastRenderedPageBreak']]
                assert not unexpected,('Non-text run feature',key,unexpected)
                segments[-1].append(child)
        else:raise ValueError(tag)
    parts=re.split(r'(⟦[MK]\d{3}⟧)',e['after'])
    assert parts[1::2]==[k for k,_ in protected]
    new=[]
    for i,text in enumerate(parts[::2]):
        new.extend(rewrite_text(segments[i],text))
        if i<len(protected):new.append(copy.deepcopy(protected[i][1]))
    for child in list(p):
        if etree.QName(child).localname!='pPr':p.remove(child)
    for child in new:p.append(child)

with ZipFile(source) as zin:
    infos=zin.infolist();members={info.filename:zin.read(info.filename) for info in infos}
root=etree.fromstring(members['word/document.xml'])
paths={}
for i,e in enumerate(root.find('w:body',NS),1):
    tag=etree.QName(e).localname
    if tag=='p':paths[f'P{i:03d}']=e
    elif tag=='tbl':
        for ri,row in enumerate(e.findall('w:tr',NS)):
            for ci,cell in enumerate(row.findall('w:tc',NS)):
                for pi,p in enumerate(cell.findall('w:p',NS)):paths[f'T{i:03d}R{ri:02d}C{ci:02d}P{pi:02d}']=p
for key,e in edits.items():apply(paths[key],key)
math=[hashlib.sha256(etree.tostring(e,method='c14n')).hexdigest() for e in root.xpath('//m:oMath',namespaces=NS)]
assert math==manifest['math_hashes'],'Native math changed'
assert len(root.find('w:body',NS))==manifest['body_blocks'],'Structure changed'
assert '⟦' not in ''.join(root.xpath('//w:t/text()',namespaces=NS)),'Unreplaced token'
members['word/document.xml']=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
target=source.with_name(source.stem+'_语言修订版.docx');version=2
while target.exists():target=source.with_name(source.stem+f'_语言修订版_v{version}.docx');version+=1
temp=ROOT/'polished_pending.docx'
with ZipFile(temp,'w') as zout:
    for info in infos:zout.writestr(info,members[info.filename])
with ZipFile(temp) as z:
    assert z.testzip() is None
    for name,h in manifest['unchanged_package_hashes'].items():assert hashlib.sha256(z.read(name)).hexdigest()==h,(name,'Non-target package member changed')
temp.replace(target)
result={'source':str(source),'source_sha256':manifest['sha256'],'output':str(target),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'changed_records':len(edits),'changed_body_paragraphs':sum(records[k]['kind']=='body' for k in edits),'changed_table_cells':sum(records[k]['kind']=='table' for k in edits),'changed_reference_notes':sum(records[k]['kind']=='reference' for k in edits),'native_math_unchanged':len(math),'other_package_members_unchanged':len(manifest['unchanged_package_hashes']),'headings_and_captions_unchanged':True,'body_blocks_unchanged':True,'number_tokens_unchanged':True}
(ROOT/'change_log.json').write_text(json.dumps(list(edits.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
