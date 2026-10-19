"""세이브스테이트 메모리에서 폰트 캐시 상태 보기.  (실행 중에는 FONT 헤더 필드가 포인터로 바뀌므로 이름 길이로 S 계산)"""
import sys, os, struct, re
sys.path.insert(0, os.path.dirname(__file__)); import emu
def fonts(m):
    out = {}
    for x in re.finditer(re.escape('Arial_'.encode('utf-16-le')), m):
        a = x.start()
        if m[a - 0x14:a - 0x10] != b'FONT': continue
        name = m[a:a + 0x40].decode('utf-16-le', 'replace').split('\0')[0]
        S = a + (0x20 if len(name) < 16 else 0x30)
        if struct.unpack_from('<H', m, S)[0] == 0x21: out[name] = S
    return out
def cache(m, S):
    first, last = struct.unpack_from('<2H', m, S); nr, rp = struct.unpack_from('<2I', m, S + 4)
    rp &= 0x1ffffff
    e = [struct.unpack_from('<2HI', m, rp + 8 * i) for i in range(nr)]
    e = [(a, b, c & 0x1ffffff) for a, b, c in e]
    return first, last, e
if __name__ == '__main__':
    m = emu.eemem(sys.argv[1])
    for name, S in fonts(m).items():
        first, last, e = cache(m, S)
        if len(e) != 3: print(name, 'ranges', len(e)); continue
        K = e[2][1]; CB = e[2][2]
        G = struct.unpack_from('<I', m, CB)[0]
        own = struct.unpack_from('<%dI' % K, m, CB + 0x10); st = struct.unpack_from('<%dI' % K, m, CB + 0x10 + 4 * K)
        used = [i for i in range(K) if own[i]]
        bad = [i for i in used if struct.unpack_from('<I', m, (own[i] & 0x1ffffff) + 4)[0] != i + 1]
        print(name, hex(S), 'K', K, 'G', G, 'used', len(used), 'bad', len(bad), 'maxstamp', max(st),
              'tex', hex(struct.unpack_from('<I', m, S + 0x38)[0]), 'W', struct.unpack_from('<2H', m, S + 0x4c))
