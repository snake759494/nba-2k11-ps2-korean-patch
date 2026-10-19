"""전체 빌드: 원본 ISO → 한글 ISO.
1) 실행 파일 UTF-16 문구 제자리 번역  2) _TDB 재작성  3) LITE 의 FONT 7종에 한글 범위 추가  4) 기타 데이터 번역
바뀐 아카이브 항목은 '3.' 파트를 ISO 끝으로 옮긴 뒤 그 뒤에 덧붙이고, 아카이브 표·ISO9660·UDF 를 갱신."""
import os, sys, struct, shutil, json, time, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import iso, isoedit, vc, lz, kfont, ktext, tdb, codepatch, rost
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'NBA 2K11 (USA).iso')
DST = os.path.join(ROOT, 'NBA 2K11 (USA) (Korean).iso')
VCX = os.path.join(ROOT, 'tools', 'bin', 'vcx.exe')
TMP = os.path.join(ROOT, 'work', 'tmp')
SEC = 2048
LITE = 0x55fc18a7
TDB = 0xd7c5aaac
ROST = 0x480fae44
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

def compress(data):
    os.makedirs(TMP, exist_ok=True)
    a, b = os.path.join(TMP, 'c_in.bin'), os.path.join(TMP, 'c_out.bin')
    open(a, 'wb').write(data); subprocess.run([VCX, 'c', a, b], check=True)
    r = open(b, 'rb').read(); os.remove(a); os.remove(b); return r

def units(d):
    """LITE 같은 순차 단위 묶음: (오프셋, 헤더32B, 페이로드)."""
    o = 0; out = []
    while o + 0x20 <= len(d):
        mg = d[o:o + 4]
        if not mg.strip(b'\0'): break
        A = struct.unpack_from('<I', d, o + 4)[0]
        out.append((o, d[o:o + 0x20], d[o + 0x20:o + 0x20 + A])); o += 0x20 + A
    return out, d[o:]

def rebuild_lite(d, sylls, report):
    us, tail = units(d)
    out = bytearray()
    for o, h, p in us:
        if h[:4] == b'FONT':
            u = lz.decompress(p)[0]
            if os.environ.get('KO_FONTMODE') == 'same':
                B, C = struct.unpack_from('<2I', h, 8)
                pad = int(os.environ.get('KO_PAD', '0')) if not report else 0
                nu = u[:B] + bytes(pad) + u[B:]; B += pad; info = {'pad': pad}
            else:
                nu, B, C, info, _ = kfont.build(u, sylls)
            c = compress(nu)
            c += bytes((-len(c)) % 16)              # 단위는 16바이트 정렬
            h = bytearray(h); struct.pack_into('<3I', h, 4, len(c), B, C)
            out += h + c; report.append(info)
        else:
            out += h + p
    return bytes(out + tail)

def patch_tdb(d, tr):
    items = tdb.parse(d); n = 0; out = []
    keys = sorted(set(s for h, s in items if tr.get('tdb', s) is not None))
    sel = os.environ.get("KO_TDBSET"); log("tdb keys", len(keys))
    allow = None if sel is None else set(keys[int(i)] for i in sel.split(',') if i)
    for h, s in items:
        v = tr.get('tdb', s)
        if allow is not None and s not in allow: v = None
        if v is not None: n += 1; out.append((h, v))
        else: out.append((h, s))
    r = tdb.build(d, out, [s for h, s in items])
    # 원본보다 작아지면 경기 중 멈춤(게임이 TDB 크기에 의존) → 원본 크기까지 0으로 채움
    if len(r) < len(d):
        r = bytearray(r + bytes(len(d) - len(r))); import struct as _s; _s.pack_into('<I', r, 4, len(r) - 0x20); r = bytes(r)
    return r, n

MRK = [0x75b369c2, 0x65a838a1, 0x9e1b2a33, 0xb0ac8a7e, 0xc9bda939, 0xef66b103]
def inplace(data, tr, scopes=('mrk', 'tdb', 'nm')):
    """데이터 안 UTF-16 문자열 제자리 번역 (길이 이내, 남는 칸은 0)."""
    import wstrs
    d = bytearray(data); n = 0
    for o, s in wstrs.find(data, 2):
        v = None
        for sc in scopes:
            v = tr.maps[sc].get(s)
            if v is not None: break
        if v is None: continue
        v = tr.enc(v)
        if len(v) > len(s): print('  [MRK too long]', repr(s[:40]), len(v), '>', len(s)); continue
        d[o:o + 2 * len(s)] = bytes(2 * len(s))
        d[o:o + 2 * len(v)] = v.encode('utf-16-le'); n += 1
    return bytes(d), n

ELFSET = set(int(x) for x in os.environ.get('KO_ELFSET', '').split(',') if x)
ELFBAD = set(json.load(open(os.path.join(ROOT, 'work', 'elf_bad.json')))) if os.path.exists(os.path.join(ROOT, 'work', 'elf_bad.json')) and os.environ.get('KO_ELFSET') is None else set()

def patch_elf(elf, tr):
    """실행 파일 UTF-16 문자열 제자리 번역. 여유 = 원문 길이 + 다음 문자열 전까지의 0 패딩(4바이트 정렬 경계 이내)."""
    import wstrs
    d = bytearray(elf); n = 0; long = []
    rng = os.environ.get('KO_ELFRANGE'); idx = -1
    lo_, hi_ = (map(int, rng.split(':')) if rng else (0, 1 << 30))
    for o, s in wstrs.find(elf, 2):
        # 코드 영역의 우연한 바이트 열을 건드리지 않도록: 문자열 데이터 구간 또는 긴 문장만
        if not (0x7f0000 <= o < 0x850000 or (len(s) >= 10 and ' ' in s)): continue
        v = tr.maps['elf'].get(s)
        if v is None and len(s) > 2:      # 2글자 이하는 내부 코드 표일 수 있으므로 ELF 전용 번역만
            v = tr.maps['tdb'].get(s) or (tr.maps['nm'].get(s) if len(s) >= 4 else None)
        if v is None: continue
        idx += 1
        if not (lo_ <= idx < hi_): continue
        if os.environ.get('KO_ELFSET') is not None and idx not in ELFSET: continue
        if idx in ELFBAD: continue
        v = tr.enc(v)
        e = o + 2 * len(s)
        k = e
        while k + 2 <= len(d) and d[k:k + 2] == b'\0\0': k += 2
        room = max(len(s), min((k - o) // 2 - 1, ((e + 2 + 3) // 4 * 4 - o) // 2 - 1))
        if len(v) > room: long.append((s, len(v), room)); continue
        d[o:o + 2 * len(s) + 2] = bytes(2 * len(s) + 2)
        d[o:o + 2 * len(v)] = v.encode('utf-16-le'); n += 1
    for s, a, b in long: print('  [ELF too long]', repr(s[:50]), a, '>', b)
    return bytes(d), n

def main(tr, elf_patch=None, data_patch=None):
    sylls = tr.sylls
    ents = {p: (l, s) for p, l, s, r in iso.walk(SRC)}
    T = vc.table(SRC); P = vc.parts(SRC)
    byh = {e[0]: list(e) for e in T}
    def get(h): return vc.read(tuple(byh[h]), SRC, P)
    new = {}
    rep = []
    if not os.environ.get('KO_NOLITE'): new[LITE] = rebuild_lite(get(LITE), sylls, rep)
    for r in rep: log('font', r)
    if not os.environ.get('KO_NOROST'): new[ROST], n = rost.rebuild(get(ROST), lambda s: tr.get('nm', s)); log('rost names', n)
    nm_ = 0
    for h in ([] if os.environ.get('KO_NOMRK') else MRK):
        new[h], k = inplace(get(h), tr); nm_ += k
    if not os.environ.get('KO_NOMRK'): new[LITE], k = inplace(new[LITE], tr); nm_ += k
    log('mrk strings', nm_)
    if not os.environ.get('KO_NOTDB'): new[TDB], n = patch_tdb(get(TDB), tr); log('tdb strings', n, len(get(TDB)), '->', len(new[TDB]))
    if data_patch:
        for h, d in data_patch(get).items(): new[h] = d
    el, es = ents['SLUS_219.36']
    elf = iso.read(el, es, SRC)
    elf2, n = (elf, 0) if os.environ.get('KO_NOELF') else patch_elf(elf, tr); log('elf strings', n)
    if not os.environ.get('KO_NOCODE'):
        elf2, labs = codepatch.patch(elf2); log('code', labs)
    assert len(elf2) == len(elf)
    log('copy iso')
    shutil.copyfile(SRC, DST)
    l3, s3 = ents['3.']
    end = os.path.getsize(SRC) // SEC - 1          # 마지막 섹터 = UDF 앵커
    n3 = (s3 + SEC - 1) // SEC
    with open(DST, 'r+b') as f:
        f.seek(el * SEC); f.write(elf2)
        # '3.' 파트를 ISO 끝으로 이동
        nl3 = end
        with open(SRC, 'rb') as g:
            g.seek(l3 * SEC); f.seek(nl3 * SEC)
            rem = n3 * SEC
            while rem:
                b = g.read(min(rem, 1 << 24)); f.write(b); rem -= len(b)
        sec3 = n3
        for h in sorted(new):
            d = new[h]
            f.seek((nl3 + sec3) * SEC); f.write(d); f.write(bytes((-len(d)) % SEC))
            byh[h][1] = len(d); byh[h][2] = 3 * vc.PART + sec3
            sec3 += (len(d) + SEC - 1) // SEC
        hdr_off = ents['0.'][0] * SEC
        for i, e in enumerate(T):
            f.seek(hdr_off + 0x9c + 12 * i); f.write(struct.pack('<3I', *byh[e[0]]))
        f.seek(hdr_off + 0xc + 3 * 4); old = struct.unpack('<I', f.read(4))[0]
        assert old == n3, (old, n3)
        f.seek(hdr_off + 0xc + 3 * 4); f.write(struct.pack('<I', sec3))
        isoedit.relocate(f, DST, '3.', nl3, sec3 * SEC)
        nsec = nl3 + sec3 + 1
        with open(SRC, 'rb') as g:
            g.seek(os.path.getsize(SRC) - SEC); avdp = bytearray(g.read(SEC))
        struct.pack_into('<I', avdp, 12, nsec - 1)
        isoedit._fix_tag(avdp, 0, struct.unpack_from('<H', avdp, 10)[0])
        f.seek((nsec - 1) * SEC); f.write(avdp)
        f.truncate(nsec * SEC)
        isoedit.set_volume_size(f, nsec)
    log('done', nsec, 'sectors')
    return rep

if __name__ == '__main__':
    tr = ktext.Translator()
    log('syllables', len(tr.sylls))
    if len(sys.argv) > 1: tr.pad(int(sys.argv[1]))      # 시험: 음절 수 채우기
    main(tr)
