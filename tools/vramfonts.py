"""세이브스테이트에서 FONT 구조를 찾아 TEX0(TBP/TBW/PSM/CBP) 출력."""
import sys, struct, os
sys.path.insert(0, os.path.dirname(__file__)); import emu
m = emu.eemem(sys.argv[1]); o = 0
while True:
    o = m.find(b'FONT', o)
    if o < 0: break
    nm = m[o + 0x14:o + 0x60].decode('utf-16-le', 'replace').split('\0')[0]
    if nm.startswith('Arial'):
        S = o + 0x14 + ((len(nm) * 2 + 2 + 15) & ~15)
        t = struct.unpack_from('<Q', m, S + 0x20)[0]
        w, h = struct.unpack_from('<2H', m, S + 0x4c)
        tbp = t & 0x3fff; tbw = (t >> 14) & 0x3f; psm = (t >> 20) & 0x3f; cbp = (t >> 37) & 0x3fff
        print('%-22s S=%08x %dx%d TBP %5d TBW %d PSM %d CBP %5d rt %08x' % (nm, S, w, h, tbp, tbw, psm, cbp, struct.unpack_from('<I', m, S + 0x38)[0]))
    o += 4
