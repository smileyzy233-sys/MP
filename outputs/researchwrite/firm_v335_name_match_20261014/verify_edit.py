from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import hashlib,json,re,sys
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
SOURCE=BASE/'sources/current_before.docx'
TARGET=Path(sys.argv[1]) if len(sys.argv)>1 else BASE/'v335_candidate.docx'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,condition):
    checks.append({'check':name,'passed':bool(condition)})
    assert condition,name
with ZipFile(SOURCE) as z:old={n:z.read(n) for n in z.namelist()}
with ZipFile(TARGET) as z:
    check('DOCX ZIP intact',z.testzip() is None)
    new={n:z.read(n) for n in z.namelist()}
x0=etree.fromstring(old['word/document.xml']);x1=etree.fromstring(new['word/document.xml'])
p0=x0.xpath('//w:body//w:p',namespaces=NS);p1=x1.xpath('//w:body//w:p',namespaces=NS)
patches=json.loads((BASE/'approved_edits.json').read_text(encoding='utf-8'))
edited={r['p'] for r in patches}
layout=json.loads((BASE/'layout_breaks.json').read_text(encoding='utf-8')) if (BASE/'layout_breaks.json').exists() else []
layout_prior={pid-1 for pid in layout}
check('All paragraph positions preserved',len(p0)==len(p1))
check('Untargeted paragraphs byte-identical',all(etree.tostring(a)==etree.tostring(b) for i,(a,b) in enumerate(zip(p0,p1)) if i not in edited|layout_prior))
check('All 69 native math objects unchanged',[etree.tostring(e) for e in x0.findall('.//m:oMath',NS)]==[etree.tostring(e) for e in x1.findall('.//m:oMath',NS)] and len(x1.findall('.//m:oMath',NS))==69)
check('Footer unchanged',all(new.get(n)==v for n,v in old.items() if re.match(r'word/footer\d+\.xml$',n)))
check('All header parts deleted',not any(re.match(r'word/header\d+\.xml$',n) for n in new))
check('No header references',len(x1.findall('.//w:headerReference',NS))==0)
check('Styles unchanged',all(new.get(n)==old[n] for n in ['word/styles.xml','word/stylesWithEffects.xml']))
check('Three editable tables preserved',len(x1.findall('.//w:tbl',NS))==3)
check('Hyperlinks preserved',[etree.tostring(e) for e in x0.findall('.//w:hyperlink',NS)]==[etree.tostring(e) for e in x1.findall('.//w:hyperlink',NS)])
for n,b in new.items():
    if n.startswith('word/') and n.endswith('.xml'):
        tree=etree.fromstring(b)
        for tag in ['keepNext','keepLines','pageBreakBefore']:
            check(f'{n}: {tag} disabled',all(e.get(W+'val','true') in ['0','false','off'] for e in tree.findall('.//w:'+tag,NS)))
plain=''.join(x1.xpath('.//w:t/text()',namespaces=NS))
for phrase in ['有业务资料与仅有行业代码的识别方式','若仅部分活动受到放宽','具体活动未知时，处理身份记为未知','同一四位小类内有可核实的业务或条件差异时','企业具体产品及政策待遇仍需业务资料识别']:
    check('Removed previous policy rule: '+phrase,phrase not in plain)
for phrase in ['识别改革前所属类别的政策暴露','依据行业类别名称识别政策暴露','同一分类版本、同一类别名称及同一匹配口径','名称匹配结果、改革前后的限制状态及实际放宽结论分列保存','将整个行业类别纳入相应条款的政策覆盖范围']:
    check('Required policy method: '+phrase,phrase in plain)
check('No placeholder leakage','{{M' not in plain)
check('No replacement glyph','\ufffd' not in plain)
check('v3.3 original preserved',sha(ROOT/'企业微观层面_v3.3.docx')=='6caf8e57849bc454f5a695c412ab962680e5460cf1fa310cb0df61d3eefc017c')
check('Previous revision note preserved',sha(ROOT/'企业微观层面_v3.35_修订说明.docx')=='ee84a9fbbe2cb9bcbe1f5eefbd91a1980b272ac832aaf8b2dd1aaf879808c956')
result={'target':str(TARGET),'sha256':sha(TARGET),'all_passed':True,'checks':checks,'changed_paragraphs':len(edited),'cannot_count_after':plain.count('不能')}
(BASE/'qa'/('verification_current.json' if TARGET.name=='企业微观层面_v3.35.docx' else 'verification_candidate.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'all_passed':True,'checks':len(checks),'changed_paragraphs':len(edited),'cannot_count_after':plain.count('不能')},ensure_ascii=False))
