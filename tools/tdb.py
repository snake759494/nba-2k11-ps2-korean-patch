"""_TDB 문자열 DB: 0x60부터 (해시, 자기상대오프셋) * n, 이후 UTF-16 문자열들. 포인터 = &오프셋필드 - 1 + 값."""
import struct
def parse(d):
    n = struct.unpack_from('<I', d, 0x54)[0]
    out = []
    for i in range(n):
        h, o = struct.unpack_from('<2I', d, 0x60 + 8 * i)
        p = 0x60 + 8 * i + 3 + o
        e = p
        while d[e:e + 2] != b'\0\0': e += 2
        out.append((h, d[p:e].decode('utf-16-le')))
    return out
def build(d, items, keys=None):
    """items: [(hash, 문자열)] 원래 순서. keys: 항목별 중복 제거 기준(원문). 원문이 다르면 번역이 같아도 따로 둔다
    (게임이 문자열 포인터로 항목을 구분하는 경우가 있어, 합치면 경기 중 멈춤)."""
    n = len(items)
    head = bytearray(d[:0x60 + 8 * n])
    strs = bytearray(); pos = {}
    base = 0x60 + 8 * n
    # 원본처럼 앞에 'INVALID TEXT' 등 순서는 상관없음
    keys = keys or [s for h, s in items]
    for (h, s), k in zip(items, keys):
        if k not in pos:
            pos[k] = base + len(strs); strs += s.encode('utf-16-le') + b'\0\0'
    for i, ((h, s), k) in enumerate(zip(items, keys)):
        fld = 0x60 + 8 * i + 4
        struct.pack_into('<2I', head, 0x60 + 8 * i, h, pos[k] - (fld - 1))
    out = head + strs
    while len(out) % 16: out += b'\0'
    struct.pack_into('<I', out, 4, len(out) - 0x20)
    return bytes(out)
