"""SLUS_219.36 한글 동적 글리프 캐시 패치 (메모리 절약형).
한글 코드(KBASE~)는 폰트의 원래 글리프 조회에서 '없음'이 된다.  폰트 범위표 2번째 (0x7fff, K, CB) 가 캐시 블록.
- HOOK1 (폰트 로더 0x4dbbac): 세트 데이터를 가진 폰트면 전역표 GT[세트] = 데이터 주소.
- HADV (글자 폭 0x4dbcf0): 한글이면 CB 의 전진폭.
- HOOK3 (글자 그리기 0x4dc39c): 글리프 없음 & 한글이면 LRU 슬롯에 비트맵 복사(비캐시 쓰기) 후 s1 = 슬롯 레코드.
텍스처는 매 프레임 RAM 에서 다시 올라가므로 별도 갱신 요청은 필요 없음.
코드 동굴: 어디서도 참조되지 않는 함수 0x32cea0~0x32d190, 0xb548a8~0xb54fe0."""
import os, sys, struct
sys.path.insert(0, os.path.dirname(__file__))
from asm import *
import kfont
VA0, OFF0 = 0x100000, 0x1000
CAVE, CAVE_END = 0x32cea0, 0x32d190
CAVE2, CAVE2_END = 0xb548a8, 0xb54fe0
KB = kfont.KBASE

def _b(op, rs, rt, src, dst):
    return (op << 26) | (R[rs] << 21) | (R[rt] << 16) | (((dst - src - 4) >> 2) & 0xffff)

class Asm:
    def __init__(self, base): self.base = base; self.code = []; self.lab = {}; self.fix = []
    def pc(self): return self.base + 4 * len(self.code)
    def L(self, name): self.lab[name] = self.pc()
    def __call__(self, *ws):
        for w in ws: self.code.append(w)
    def br(self, op, rs, rt, name):
        self.fix.append((len(self.code), op, rs, rt, name)); self.code.append(0)
    def beq(self, rs, rt, name): self.br(4, rs, rt, name)
    def bne(self, rs, rt, name): self.br(5, rs, rt, name)
    def blez(self, rs, name): self.br(6, rs, 'zero', name)
    def b(self, name): self.br(4, 'zero', 'zero', name)
    def done(self):
        for i, op, rs, rt, name in self.fix:
            self.code[i] = _b(op, rs, rt, self.base + 4 * i, self.lab[name])
        return b''.join(struct.pack('<I', w) for w in self.code)

def OR(rd, rs, rt): return (R[rs] << 21) | (R[rt] << 16) | (R[rd] << 11) | 0x25
def sra(rd, rt, sa): return (R[rt] << 16) | (R[rd] << 11) | (sa << 6) | 3
def sh(rt, off, base): return (41 << 26) | (R[base] << 21) | (R[rt] << 16) | (off & 0xffff)
def hi_lo(a):
    lo = a & 0xffff; hi = (a >> 16) + (1 if lo & 0x8000 else 0)
    return hi & 0xffff, lo

def patch(elf):
    d = bytearray(elf)
    def w32(va, v): struct.pack_into('<I', d, va - VA0 + OFF0, v)
    def r32(va): return struct.unpack_from('<I', d, va - VA0 + OFF0)[0]
    assert r32(0x4dbbac) == jal(0x4f8e58)
    assert r32(0x4dbcf0) == sll('a1', 'a1', 16) and r32(0x4dbcf4) == move('t0', 'a0'), (hex(r32(0x4dbcf0)), hex(r32(0x4dbcf4)))
    assert r32(0x4dc39c) == cvt_w_s(2, 1) and r32(0x4dc3a0) == mfc1('a0', 2)
    assert r32(CAVE) == 0x27bdff10 and r32(CAVE2) == 0x27bdffc0
    GT = CAVE_END - 0x10
    gh, gl = hi_lo(GT)
    # ---------- 동굴 1: HOOK1, HADV ----------
    a = Asm(CAVE)
    a.L('hook1')
    a(addiu('sp', 'sp', -0x20), sd('ra', 0, 'sp'), sd('s0', 8, 'sp'), move('s0', 'a0'), jal(0x4f8e58), NOP,
      lw('t0', -0x1c, 's0'), addiu('t1', 'zero', 2))
    a.bne('t0', 't1', 'h1d'); a(NOP)
    a(lw('t2', -0x18, 's0'), lhu('t0', 8, 't2'), ori('t1', 'zero', 0x7fff))
    a.bne('t0', 't1', 'h1d'); a(NOP)
    a(lw('t6', 0xc, 't2'), lhu('t0', 0xa, 't6'))
    a.beq('t0', 'zero', 'h1d'); a(NOP)
    a(lw('t1', 0xc, 't6'), addu('t1', 't1', 't6'), addiu('t1', 't1', 0xc),
      lhu('t0', 8, 't6'), sll('t0', 't0', 2), lui('t3', gh), addiu('t3', 't3', gl), addu('t3', 't3', 't0'), sw('t1', 0, 't3'))
    a.L('h1d')
    a(ld('ra', 0, 'sp'), ld('s0', 8, 'sp'), jr('ra'), addiu('sp', 'sp', 0x20))
    a.L('hadv')                                               # (지연 슬롯에서 t0 = a0 됨)
    a(sll('a1', 'a1', 16), sra('t1', 'a1', 16), slti('t2', 't1', KB))
    a.bne('t2', 'zero', 'back'); a(NOP)
    a.beq('t0', 'zero', 'back'); a(NOP)
    a(lw('t3', 4, 't0'), addiu('t4', 'zero', 2))
    a.bne('t3', 't4', 'back'); a(NOP)
    a(lw('t3', 8, 't0'), lhu('t4', 8, 't3'), ori('t5', 'zero', 0x7fff))
    a.bne('t4', 't5', 'back'); a(NOP)
    a(lw('t3', 0xc, 't3'), lhu('t4', 0x10, 't3'), addiu('t5', 't1', -KB), sltu('t6', 't5', 't4'))
    a.beq('t6', 'zero', 'back'); a(NOP)
    a(jr('ra'), lw('v0', 0x14, 't3'))
    a.L('back')
    a(j(0x4dbcf8), NOP)
    c1 = a.done(); assert CAVE + len(c1) <= GT, hex(CAVE + len(c1))
    labs = dict(a.lab)
    # ---------- 동굴 2: HOOK3 ----------
    a = Asm(CAVE2)
    a.L('hook3')
    a(addiu('sp', 'sp', -0x40), sd('ra', 0, 'sp'), swc1(0, 8, 'sp'), swc1(1, 0xc, 'sp'), swc1(5, 0x10, 'sp'))
    a.bne('s1', 'zero', 'done'); a(slti('t0', 's4', KB))
    a.bne('t0', 'zero', 'done'); a(NOP)
    a(lw('t9', 0, 's2'), lw('t0', 4, 't9'), addiu('t1', 'zero', 2))
    a.bne('t0', 't1', 'done'); a(NOP)
    a(lw('t8', 8, 't9'), lhu('t0', 8, 't8'), ori('t1', 'zero', 0x7fff))
    a.bne('t0', 't1', 'done'); a(NOP)
    a(lw('t6', 0xc, 't8'),
      addiu('t5', 's4', -KB), lhu('t0', 0x10, 't6'), sltu('t1', 't5', 't0'))
    a.beq('t1', 'zero', 'done'); a(NOP)
    a(lhu('t7', 0x12, 't6'),
      lhu('a0', 0x18, 't6'), addu('a0', 'a0', 't6'),         # OWN
      lhu('a1', 0x1a, 't6'), addu('a1', 'a1', 't6'),         # ST
      lhu('a2', 0x1c, 't6'), addu('a2', 'a2', 't6'),         # MAP
      lhu('a3', 0x1e, 't6'), addu('a3', 'a3', 't6'),         # REC
      lw('t4', 0, 't6'), addiu('t4', 't4', 1), sw('t4', 0, 't6'),
      addiu('v1', 't5', 1),
      sll('t0', 't5', 1), addu('t0', 't0', 'a2'), lhu('t3', 0, 't0'))
    a.beq('t3', 'zero', 'miss'); a(addiu('t3', 't3', -1))
    a(sll('t1', 't3', 1), addu('t1', 't1', 'a0'), lhu('t2', 0, 't1'))
    a.bne('t2', 'v1', 'miss'); a(NOP)
    a(sll('t1', 't3', 2), addu('t1', 't1', 'a1'), sw('t4', 0, 't1'))
    a.b('setrec'); a(NOP)
    a.L('miss')
    a(move('t3', 'zero'), lw('t2', 0, 'a1'), addiu('t1', 'zero', 1))
    a.L('loop')
    a(slt('at', 't1', 't7'))
    a.beq('at', 'zero', 'found'); a(sll('t0', 't1', 2))
    a(addu('t0', 't0', 'a1'), lw('t0', 0, 't0'), sltu('at', 't0', 't2'))
    a.beq('at', 'zero', 'next'); a(NOP)
    a(move('t2', 't0'), move('t3', 't1'))
    a.L('next')
    a.b('loop'); a(addiu('t1', 't1', 1))
    a.L('found')
    a(sll('t0', 't3', 1), addu('t0', 't0', 'a0'), lhu('t1', 0, 't0'))
    a.beq('t1', 'zero', 'noold'); a(addiu('t1', 't1', -1))
    a(sll('t1', 't1', 1), addu('t1', 't1', 'a2'), sh('zero', 0, 't1'))
    a.L('noold')
    a(sh('v1', 0, 't0'),
      sll('t1', 't5', 1), addu('t1', 't1', 'a2'), addiu('t2', 't3', 1), sh('t2', 0, 't1'),
      sll('t1', 't3', 2), addu('t1', 't1', 'a1'), sw('t4', 0, 't1'),
      lhu('t0', 8, 't6'), sll('t0', 't0', 2), lui('t1', gh), addiu('t1', 't1', gl), addu('t1', 't1', 't0'), lw('t8', 0, 't1'),
      lhu('t2', 4, 't6'), lhu('t0', 6, 't6'), mult('t2', 't0'), mflo('t0'), mult('t0', 't5'), mflo('t0'), addu('t8', 't8', 't0'),
      sll('t0', 't7', 5), sll('t1', 't7', 6), addu('t0', 't0', 't1'), addu('t0', 't0', 'a3'),
      sll('t1', 't3', 2), addu('t0', 't0', 't1'), lhu('a0', 0, 't0'), lhu('a1', 2, 't0'),
      lw('t0', 0x38, 't9'), lhu('t1', 0x4c, 't9'), srl('t1', 't1', 1),
      mult('a1', 't1'), mflo('a1'), srl('a0', 'a0', 1), addu('t0', 't0', 'a1'), addu('t0', 't0', 'a0'),
      lui('at', 0x2000), OR('t0', 't0', 'at'),
      lhu('t5', 6, 't6'))
    a.L('row')
    a.blez('t5', 'setrec'); a(move('t4', 'zero'))
    a.L('col')
    a(addu('a0', 't8', 't4'), lbu('a1', 0, 'a0'), addu('a0', 't0', 't4'), sb('a1', 0, 'a0'),
      addiu('t4', 't4', 1), slt('at', 't4', 't2'))
    a.bne('at', 'zero', 'col'); a(NOP)
    a(addu('t8', 't8', 't2'), addu('t0', 't0', 't1'), addiu('t5', 't5', -1))
    a.b('row'); a(NOP)
    a.L('setrec')
    a(sll('t0', 't3', 5), sll('t1', 't3', 6), addu('t0', 't0', 't1'), addu('s1', 'a3', 't0'))
    a.L('done')
    a(lwc1(0, 8, 'sp'), lwc1(1, 0xc, 'sp'), lwc1(5, 0x10, 'sp'), cvt_w_s(2, 1), mfc1('a0', 2),
      ld('ra', 0, 'sp'), jr('ra'), addiu('sp', 'sp', 0x40))
    c2 = a.done(); assert CAVE2 + len(c2) <= CAVE2_END, hex(CAVE2 + len(c2))
    labs.update(a.lab)
    for cav, end, code in ((CAVE, CAVE_END, c1), (CAVE2, CAVE2_END, c2)):
        o = cav - VA0 + OFF0
        d[o:o + (end - cav)] = bytes(end - cav)
        d[o:o + len(code)] = code
    w32(0x4dbbac, jal(labs['hook1']))
    w32(0x4dbcf0, j(labs['hadv']))
    w32(0x4dc39c, jal(labs['hook3'])); w32(0x4dc3a0, NOP)
    return bytes(d), {k: hex(v) for k, v in labs.items() if k in ('hook1', 'hadv', 'hook3')}
