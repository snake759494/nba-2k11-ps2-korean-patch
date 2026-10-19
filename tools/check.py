"""번역 검사: printf 지정자 순서, {n} 집합, |태그|, \n 개수, ð 개수, [n] 집합."""
import json, glob, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
PF = re.compile(r'%[-+ #0]*\d*(?:\.\d+)?[lh]*[diuxXcsfeEgG%]')
def sig(s):
    return ([m for m in PF.findall(s) if m != '%%'], sorted(re.findall(r'\{\d+[^}]*\}', s)), sorted(re.findall(r'\|[A-Z_0-9]+\|', s)),
            s.count('\n'), s.count('ð'), sorted(re.findall(r'\[\d\]', s)))
bad = 0
for bp in sorted(glob.glob('translation/en/*.json')):
    name = os.path.basename(bp); kp = os.path.join('translation', 'ko', name)
    if not os.path.exists(kp): continue
    K = json.load(open(kp, encoding='utf-8'))
    for it in json.load(open(bp, encoding='utf-8')):
        v = K.get(str(it['id']))
        if v is None: continue
        a, b = sig(it['en']), sig(v)
        if a != b:
            bad += 1; print(name, it['id'], repr(it['en'][:80]), '=>', repr(v[:80]), [x for x, y in zip(a, b) if x != y])
    for k in K:
        if not any(str(it['id']) == k for it in json.load(open(bp, encoding='utf-8'))): print('unknown id', name, k)
print('problems:', bad)
