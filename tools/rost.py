"""ROST(480fae44) 문자열 풀: 0x7c6a0~끝, UTF-16 0 종료. 참조 = 4바이트 정렬 필드, 대상 = &필드 - 1 + 값."""
import struct
POOL = 0x7c6a0
def pool(d):
    out = []; o = POOL
    while o < len(d) - 1:
        e = o
        while d[e:e + 2] != b'\0\0': e += 2
        out.append((o, d[o:e].decode('utf-16-le'))); o = e + 2
        while o < len(d) - 1 and d[o:o + 2] == b'\0\0' and (o - POOL) % 2 == 0 and False: o += 2
    return out
def refs(d, starts):
    st = set(starts); r = []
    for o in range(0, POOL, 4):
        v = struct.unpack_from('<I', d, o)[0]
        if v & 1 and (o - 1 + v) in st: r.append((o, o - 1 + v))
    return r

def rebuild(d, get):
    """풀을 같은 자리·같은 크기 안에서 다시 쓴다. get(영문)->게임 문자열 또는 None."""
    P = pool(d)
    R = refs(d, [o for o, s in P])
    new = bytearray(d[:POOL]); pos = {}; out = bytearray()
    old2new = {}
    for o, s in P:
        v = get(s) if s else None
        t = v if v is not None else s
        # 원본 항목마다 따로 둔다(번역이 같아도 합치지 않음 — 게임이 포인터로 구분할 수 있어 합치면 경기 중 멈춤)
        old2new[o] = POOL + len(out); out += t.encode('utf-16-le') + b'\0\0'
    assert POOL + len(out) <= len(d), ('pool overflow', len(out), len(d) - POOL)
    out += bytes(len(d) - POOL - len(out))
    new += out
    n = 0
    for f, t in R:
        struct.pack_into('<I', new, f, old2new[t] - (f - 1)); n += 1
    return bytes(new), sum(1 for o, s in P if s and get(s) is not None)
