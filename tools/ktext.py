"""번역 불러오기와 게임용 인코딩.
번역: translation/ko/<묶음>.json {id: 한국어}, 원문: work/batches/<묶음>.json [{id, en}]
수동 보정: translation/fix/*.json {원문: 번역 | null}
한글 음절은 kfont.KBASE + 순번(자주 쓰는 순)으로 바꾼다(게임이 문자를 부호 있는 16비트로 비교)."""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(__file__))
import kfont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TR = os.path.join(ROOT, 'translation')
SUBST = {'·': '.', '…': '...', '“': '"', '”': '"', '‘': "'", '’': "'", '–': '-', '—': '-', '　': ' ', '×': 'x'}
def is_syl(ch): return 0xAC00 <= ord(ch) <= 0xD7A3

def load_map(prefix):
    """원문 -> 번역 (묶음 이름이 prefix 로 시작하는 것만)."""
    m = {}
    for bp in sorted(glob.glob(os.path.join(TR, 'en', prefix + '*.json'))):
        name = os.path.splitext(os.path.basename(bp))[0]
        kp = os.path.join(TR, 'ko', name + '.json')
        if not os.path.exists(kp): continue
        K = json.load(open(kp, encoding='utf-8'))
        for it in json.load(open(bp, encoding='utf-8')):
            v = K.get(str(it['id']))
            if v is not None and v != it['en']: m[it['en']] = v
    for fp in sorted(glob.glob(os.path.join(TR, 'fix', prefix + '*.json'))):
        for k, v in json.load(open(fp, encoding='utf-8')).items():
            if v is None: m.pop(k, None)
            else: m[k] = v
    return m

class Translator:
    def __init__(self, scopes=('tdb', 'elf', 'mrk', 'lay', 'nm')):
        self.maps = {sc: load_map(sc) for sc in scopes}
        nm = self.maps.get('nm', {})
        # 번역문 속 영문 고유명사(팀·선수 이름)를 로스터 번역으로 치환, 이름 자체인 문자열은 그대로 이름 번역
        import re
        W = re.compile(r"[A-Z][A-Za-z'\-]+(?: [A-Z][A-Za-z'\-]+)*")
        def sub(m):
            t = m.group(0)
            if t in nm and not t.isupper(): return nm[t]
            return ' '.join(nm.get(w, w) if not w.isupper() else w for w in t.split(' '))
        for sc in scopes:
            if sc == 'nm': continue
            mp = self.maps[sc]
            for k in list(mp): mp[k] = W.sub(sub, mp[k])
        if 'tdb' in self.maps:
            for k, v in nm.items(): self.maps['tdb'].setdefault(k, v)
        used = {}
        for mp in self.maps.values():
            for v in mp.values():
                for ch in v:
                    if is_syl(ch): used[ch] = used.get(ch, 0) + 1
        self.sylls = sorted(used, key=lambda c: (-used[c], c))
        if os.environ.get('KO_MAXSYL'): self.sylls = self.sylls[:int(os.environ['KO_MAXSYL'])]
        self.code = {s: chr(kfont.KBASE + i) for i, s in enumerate(self.sylls)}
    def pad(self, n):
        """시험용: 음절 목록을 n 개까지 KS X 1001 음절로 채움."""
        for i in range(2350):
            if len(self.sylls) >= n: break
            c = bytes([0xb0 + i // 94, 0xa1 + i % 94]).decode('euc-kr')
            if c not in self.code:
                self.code[c] = chr(kfont.KBASE + len(self.sylls)); self.sylls.append(c)
    def enc(self, s):
        out = []
        for ch in s:
            ch = SUBST.get(ch, ch)
            for c in ch:
                if is_syl(c): out.append(self.code.get(c, '?'))
                elif ord(c) <= 0xff: out.append(c)
                else: raise ValueError('unencodable %r in %r' % (c, s))
        return ''.join(out)
    def get(self, scope, en):
        v = self.maps[scope].get(en)
        return None if v is None else self.enc(v)
