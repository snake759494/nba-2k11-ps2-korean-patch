"""참조되지 않는 함수(죽은 코드) 찾기: jal 대상, 데이터 속 32비트 포인터, lui/addiu 쌍 모두 검사."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__)); import edis
D = edis.D; BASE = 0x100000; OFF = 0x1000; N = 0xa6fddb
W = struct.unpack_from('<%dI' % (N // 4), D, OFF)
refs = set()
for i, w in enumerate(W):
    op = w >> 26
    if op in (2, 3): refs.add(((BASE + 4 * i) & 0xf0000000) | ((w & 0x3ffffff) << 2))
    if BASE <= w < BASE + N: refs.add(w)
    if op == 15:
        rt = (w >> 16) & 31
        for k in range(1, 12):
            if i + k >= len(W): break
            w2 = W[i + k]
            if ((w2 >> 21) & 31) == rt and (w2 >> 26) in (9, 13):
                imm = w2 & 0xffff
                if (w2 >> 26) == 9 and imm & 0x8000: imm -= 0x10000
                refs.add(((w & 0xffff) << 16) + imm); break
# 함수 시작 = addiu sp,sp,-X  (직전이 jr ra + 지연슬롯이거나 nop)
starts = []
for i, w in enumerate(W):
    if (w & 0xffff0000) == 0x27bd0000 and (w & 0x8000):
        starts.append(BASE + 4 * i)
starts.sort()
dead = []
for a, b in zip(starts, starts[1:]):
    if a in refs: continue
    # 직전 명령이 jr ra 계열(두 칸 전)인지
    i = (a - BASE) // 4
    if W[i - 2] != 0x03e00008 and W[i - 1] != 0: continue
    if any(x in refs for x in range(a, b, 4)): continue
    dead.append((a, b - a))
dead.sort(key=lambda x: -x[1])
for a, l in dead[:40]: print(hex(a), hex(l))
