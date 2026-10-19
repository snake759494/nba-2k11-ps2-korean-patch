"""LITE 묶음의 FONT 7종에 한글 범위(KBASE~)를 추가.
FONT 구조(S = 구조 시작): +0 u16 first,last / +4 범위 수 / +8 범위표(자기상대 -1) / +0xc 공백폭, 줄높이, 대문자높이, 하강, 상승
 +0x20 TEX0(8B) ... +0x48 텍스처바이트|1, +0x4c u16 w,h, +0x54 텍스처바이트.  범위표: u16 lo,hi + 글리프배열(자기상대 -1)
글리프 0x60B: int 전진폭, 3*int, 정점 4개(x,y,0,0 float), UV(u0,v0,u1,v1 정규화).
B(CPU) 파트 뒤에 C(GPU) 파트 = 4bpp 선형 텍스처(왼쪽 픽셀=하위 니블) + 16색 팔레트(흰색 알파)."""
import os, sys, struct, math
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
KBASE = 0x3400          # 부호 있는 16비트로 비교하므로 0x8000 미만이어야 함
# 폰트별 (한글 TTF, 렌더 크기 px, 굵게(외곽 두께), 기울임)
SPEC = {
    'Arial_11':              ('Galmuri11.ttf', 12, 0, 0),
    'Arial_13_bold':         ('NanumSquareNeo-dEb.ttf', 12, 0, 0),
    'Arial_15_bold':         ('NanumSquareNeo-dEb.ttf', 14, 0, 0),
    'Arial_Black_15_Italic': ('NanumSquareNeo-eHv.ttf', 15, 0, 0.2),
    'Arial_Black_17':        ('NanumSquareNeo-eHv.ttf', 16, 0, 0),
    'Arial_Black_20':        ('NanumSquareNeo-eHv.ttf', 19, 0, 0),
    'Arial_Black_25':        ('NanumSquareNeo-eHv.ttf', 23, 0, 0),
}

def parse(u):
    nl = struct.unpack_from('<I', u, 0x14)[0]
    S = 0x20 + (nl & ~0xf)
    name = u[0x20:S].decode('utf-16-le').split('\0')[0]
    first, last = struct.unpack_from('<2H', u, S)
    nr, rp = struct.unpack_from('<2I', u, S + 4)
    rt = S + 7 + rp
    ranges = []
    for i in range(nr):
        lo, hi, gp = struct.unpack_from('<2HI', u, rt + 8 * i)
        ranges.append((lo, hi, rt + 8 * i + 3 + gp))
    w, h = struct.unpack_from('<2H', u, S + 0x4c)
    tb = struct.unpack_from('<I', u, S + 0x54)[0]
    met = struct.unpack_from('<5i', u, S + 0xc)
    return dict(S=S, name=name, ranges=ranges, w=w, h=h, tb=tb, met=met)

def glyph(u, off):
    I = struct.unpack_from('<4i', u, off); F = struct.unpack_from('<20f', u, off + 16)
    return I, F

_FC = {}
def _font(ttf, size):
    k = (ttf, size)
    if k not in _FC: _FC[k] = ImageFont.truetype(os.path.join(ROOT, ttf), size)
    return _FC[k]

def _render(ch, ttf, px, slant, pixel):
    """기준선 정렬 렌더링. 결과 캔버스: 가로 2*px, 세로 2*px, 기준선 y = 1.5*px."""
    big = 1 if pixel else 4
    fb = _font(ttf, px * big)
    W = 2 * px * big
    im = Image.new('L', (W, W), 0); d = ImageDraw.Draw(im)
    d.text((px * big // 4, int(1.5 * px * big)), ch, font=fb, fill=255, anchor='ls')
    if slant:
        bl = 1.5 * px * big
        im = im.transform(im.size, Image.AFFINE, (1, slant, -slant * bl, 0, 1, 0), Image.BICUBIC)
    if big > 1:
        im = im.resize((W // big, W // big), Image.BOX)
        im = im.point(lambda v: 0 if v < 24 else v)
    return im

def kglyph_images(sylls, ttf, px, slant):
    """음절 이미지들을 공통 상자로 잘라 반환. box 는 렌더 캔버스 기준(기준선 y=1.5*px)."""
    pixel = ttf.startswith('Galmuri')
    ims = [_render(c, ttf, px, slant, pixel) for c in sylls]
    probe = [_render(c, ttf, px, slant, pixel) for c in '각뷁한글를빛몫']
    xs0, ys0, xs1, ys1 = [], [], [], []
    for im in probe + ims:
        bb = im.getbbox()
        if bb: xs0.append(bb[0]); ys0.append(bb[1]); xs1.append(bb[2]); ys1.append(bb[3])
    box = (min(xs0), min(ys0), max(xs1), max(ys1))
    return [im.crop(box) for im in ims], box

# 공유 비트맵 세트: (TTF, 렌더 px, 주인 폰트)
SETS = [('Galmuri11.ttf', 12, 'Arial_11'),
        ('NanumSquareNeo-dEb.ttf', 14, 'Arial_15_bold'),
        ('NanumSquareNeo-eHv.ttf', 19, 'Arial_Black_20')]
# 폰트별 (세트, 표시 배율, 기울임, 텍스처 크기)
FONTSET = {'Arial_11': (0, 1.0, 0, (256, 256)),
           'Arial_13_bold': (1, 12 / 14, 0, (256, 256)),
           'Arial_15_bold': (1, 1.0, 0, (256, 256)),
           'Arial_Black_15_Italic': (2, 15 / 19, 0.2, (512, 256)),
           'Arial_Black_17': (2, 16 / 19, 0, (512, 256)),
           'Arial_Black_20': (2, 1.0, 0, (512, 256)),
           'Arial_Black_25': (2, 23 / 19, 0, (512, 256))}
_SETCACHE = {}
def glyph_set(si, sylls):
    """세트 si 의 비트맵: (cw, ch, gw, gh, [4bpp 칸 바이트...])."""
    k = (si, tuple(sylls))
    if k in _SETCACHE: return _SETCACHE[k]
    import numpy as np
    ttf, px, _ = SETS[si]
    ims, box = kglyph_images(sylls, ttf, px, 0)
    gw, gh = ims[0].size
    cw, ch = gw + 2, gh + 2
    if cw % 2: cw += 1
    bm = []
    for im in ims:
        c = np.zeros((ch, cw), np.uint8)
        a = np.asarray(im, np.uint16)
        c[1:1 + gh, 1:1 + gw] = np.minimum(15, (a * 15 + 127) // 255).astype(np.uint8)
        bm.append((c[:, 0::2] | (c[:, 1::2] << 4)).astype(np.uint8).tobytes())
    _SETCACHE[k] = (cw, ch, gw, gh, bm)
    return _SETCACHE[k]

def build(u, sylls, cfg=None):
    """한글 동적 캐시 폰트 (메모리 절약형).
    폰트 범위표 = [원본 범위, (0x7fff, K, 캐시 블록 CB)] — 2번째는 조회에 걸리지 않는 표식, 한글 코드는 원래 조회에서 '없음'.
    CB: +0 G, +4 행바이트 u16, +6 행수 u16, +8 세트번호 u16, +0xa 주인 여부 u16, +0xc 세트 데이터 자기상대(주인만),
        +0x10 N u16, +0x12 K u16, +0x14 전진폭 u32, +0x18 pad
        +0x20 owner[K] u16, stamp[K] u32, map[N] u16 (모두 4바이트 정렬), slotrec[K]*0x60, slotxy[K] u16*2
    세트 데이터(주인 폰트에만) = 음절 순서대로 칸 비트맵(행바이트*행수)."""
    import numpy as np
    P = parse(u)
    si, scl, slant, (W, H) = FONTSET[P['name']]
    S = P['S']; w0, h0 = P['w'], P['h']
    B0 = len(u) - (P['tb'] + 0x40)
    tex0 = u[B0:B0 + P['tb']]; pal = u[B0 + P['tb']:B0 + P['tb'] + 0x40]
    lo, hi, G = P['ranges'][0]
    occ = []
    for i in range(hi - lo + 1):
        I, F = glyph(u, G + 0x60 * i)
        if F[18] > F[16]:
            occ.append((int(F[16] * w0) - 1, int(F[17] * h0) - 1, int(math.ceil(F[18] * w0)) + 1, int(math.ceil(F[19] * h0)) + 1))
    I, F = glyph(u, G + 0x60 * (ord('H') - lo))
    cap_top, base = F[1] + 1, F[13] - 1
    cw, ch, gw, gh, bm = glyph_set(si, sylls)
    qw, qh = cw * scl, ch * scl
    mid = (cap_top + base) / 2 + 0.5
    y0 = round(mid - qh / 2)
    adv = round(gw * scl + max(1, SETS[si][1] * scl * 0.08))
    if slant: adv = round((gw - slant * gh * 0.5) * scl) + 1
    sx, sy = cw + 2, ch + 1
    slots = []
    for y in range(0, H - ch + 1, sy):
        for x in range(0, W - cw + 1, sx):
            if any(x < a1 and x + cw > a0 and y < b1 and y + ch > b0 for a0, b0, a1, b1 in occ): continue
            slots.append((x, y))
    K = min(len(slots), 0x7ffe); slots = slots[:K]
    n = len(sylls)
    pix = np.zeros((H, W), np.uint8)
    t0 = np.frombuffer(tex0, np.uint8).reshape(h0, w0 // 2)
    pix[:h0, 0:w0:2] = t0 & 15; pix[:h0, 1:w0:2] = t0 >> 4
    tex = (pix[:, 0::2] | (pix[:, 1::2] << 4)).astype(np.uint8).tobytes()
    gpu = tex + pal
    cpu = bytearray(u[:B0])
    for i in range(hi - lo + 1):
        o = G + 0x60 * i + 0x50
        a0, b0, a1, b1 = struct.unpack_from('<4f', cpu, o)
        struct.pack_into('<4f', cpu, o, a0 * w0 / W, b0 * h0 / H, a1 * w0 / W, b1 * h0 / H)
    while len(cpu) % 16: cpu.append(0)
    rt = len(cpu); cpu += bytes(16)
    cb = len(cpu)
    owner = SETS[si][2] == P['name']
    def al4(x): return (x + 3) & ~3
    o_own = 0x20; o_st = al4(o_own + 2 * K); o_map = o_st + 4 * K; o_rec = (al4(o_map + 2 * n) + 15) & ~15
    o_xy = o_rec + 0x60 * K; o_end = (o_xy + 4 * K + 15) & ~15
    blk = bytearray(o_end)
    for k, (x, y) in enumerate(slots):
        r = struct.pack('<4i', adv, 0, 0, 0)
        sh = slant * qh
        for vx, vy in ((sh, y0), (qw + sh, y0), (0, y0 + qh), (qw, y0 + qh)):
            r += struct.pack('<4f', vx, vy, 0, 0)
        r += struct.pack('<4f', x / W, y / H, (x + cw) / W, (y + ch) / H)
        blk[o_rec + 0x60 * k:o_rec + 0x60 * (k + 1)] = r
        struct.pack_into('<2H', blk, o_xy + 4 * k, x, y)
    setoff = 0
    if owner:
        setoff = o_end
        blk += b''.join(bm)
        while len(blk) % 16: blk.append(0)
    struct.pack_into('<I4HiHHI', blk, 0, 0, cw // 2, ch, si, 1 if owner else 0, setoff - 0xc if owner else 0, n, K, adv)
    hdr_extra = struct.pack('<4H', o_own, o_st, o_map, o_rec)   # +0x18: 배열 위치
    blk[0x18:0x20] = hdr_extra
    cpu += blk
    # 슬롯 좌표 위치는 o_rec + 0x60*K 로 계산 가능
    struct.pack_into('<2Hi', cpu, rt, lo, hi, G - (rt + 3))
    struct.pack_into('<2Hi', cpu, rt + 8, 0x7fff, K, cb - (rt + 8 + 3))
    struct.pack_into('<2I', cpu, S + 4, 2, rt - (S + 7))
    tx = struct.unpack_from('<Q', cpu, S + 0x20)[0]
    tx &= ~((0x3f << 14) | (0xf << 26) | (0xf << 30) | (0x3fff << 37))
    tx |= (W // 64) << 14 | int(math.log2(W)) << 26 | int(math.log2(H)) << 30 | (len(tex) >> 8) << 37
    struct.pack_into('<Q', cpu, S + 0x20, tx)
    struct.pack_into('<I', cpu, S + 0x48, len(tex) | 1)
    struct.pack_into('<2H', cpu, S + 0x4c, W, H)
    struct.pack_into('<I', cpu, S + 0x54, len(tex))
    info = dict(name=P['name'], set=si, cell=(cw, ch), n=n, slots=K, add_cpu=len(cpu) - B0, add_gpu=len(gpu) - (len(u) - B0))
    return bytes(cpu) + bytes(gpu), len(cpu), len(gpu), info, None

def preview(pixinfo, path, scale=2):
    cells, cw, ch, W, H, pix = pixinfo
    im = Image.frombytes('L', (W, H), bytes(min(255, v * 17) for v in pix))
    im.resize((W * scale, H * scale), Image.NEAREST).save(path)
