from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import json, hashlib

BASE=Path(__file__).resolve().parent
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
files={'source':Path(r'A:\桌面\study\企业微观层面_v4.1.docx'),'reference':Path(r'A:\桌面\制度性开放\审稿意见\手动改和写\审稿人回复.docx')}
for label,path in files.items():
    with ZipFile(path) as z:
        root=E.fromstring(z.read('word/document.xml'))
        pars=[]
        for i,p in enumerate(root.xpath('//w:body//w:p',namespaces=NS)):
            out=[]; math=[]
            for c in p:
                if E.QName(c).localname=='pPr': continue
                if c.tag.startswith('{'+NS['m']+'}'):
                    token='{{M'+str(len(math))+'}}'
                    math.append({'token':token,'text':''.join(c.xpath('.//m:t/text()',namespaces=NS)),'xml':E.tostring(c,encoding='unicode')})
                    out.append(token)
                else:
                    for n in c.iter():
                        if n.tag=='{'+NS['w']+'}t':out.append(n.text or '')
                        elif n.tag=='{'+NS['w']+'}tab':out.append('\t')
                        elif n.tag=='{'+NS['w']+'}footnoteReference':out.append('{{F'+n.get('{'+NS['w']+'}id')+'}}')
            pars.append({'i':i,'text':''.join(out),'math':math,'style':p.xpath('string(w:pPr/w:pStyle/@w:val)',namespaces=NS),'table':bool(p.xpath('ancestor::w:tbl',namespaces=NS))})
        notes={}
        for part in ['word/footnotes.xml','word/endnotes.xml']:
            if part in z.namelist():notes[part]=E.fromstring(z.read(part)).xpath('//w:t/text()',namespaces=NS)
        data={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'paragraphs':pars,'notes':notes,'math_count':len(root.xpath('//m:oMath',namespaces=NS)),'table_count':len(root.xpath('//w:tbl',namespaces=NS))}
        (BASE/(label+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        text='\n\n'.join(f'[{p["i"]}] ({p["style"]}{",table" if p["table"] else ""}) {p["text"]}'+('  [数学: '+ '; '.join(m['token']+'='+m['text'] for m in p['math'])+']' if p['math'] else '') for p in pars)
        (BASE/(label+'.txt')).write_text(text+'\n\nNOTES\n'+json.dumps(notes,ensure_ascii=False,indent=2),encoding='utf-8')
        print(label, len(pars), data['math_count'], data['table_count'],len(text))
