"""풀어둔 리소스(extract/u)에서 UTF-16 화면 문구 후보 집계."""
import os,sys,re,json,glob,collections
sys.path.insert(0,os.path.dirname(__file__));import wstrs
IDENT=re.compile(r'[_\/]|^[a-z0-9]|[a-z][A-Z]|\.\w{2,4}$|^[A-Z0-9]+\d$|^\W+$')
def is_ui(t):
    s=t.strip()
    if len(s)<2 or not re.search(r'[A-Za-z]{2}',s): return False
    return not IDENT.search(s)
out={};c=collections.Counter();cn=collections.Counter()
for fn in glob.glob('extract/u/*'):
    if fn.endswith('_list.txt'): continue
    d=open(fn,'rb').read();ss=[(o,s) for o,s in wstrs.find(d,2) if is_ui(s)]
    if ss:
        k=os.path.basename(fn);out[k]=ss;t=k.split('.')[-1];c[t]+=len(ss);cn[t]+=1
json.dump(out,open('work/res_strings.json','w',encoding='utf-8'),ensure_ascii=False)
print(c.most_common());print(cn.most_common())
