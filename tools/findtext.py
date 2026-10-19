import sys,os;sys.path.insert(0,os.path.dirname(__file__));import vc,lz,iso
from multiprocessing import Pool
W=[w for w in sys.argv[1:]]
def units(d):
    ch,end=lz.chain(d)
    if not ch: return [(-1,d)]
    out=[]
    for o,mg,A,B,C,D in ch:
        try: out.append((o,lz.decompress(d[o+0x20:o+0x20+A])[0]))
        except Exception: out.append((o,b''))
    return out
def job(e):
    P=vc.parts();d=vc.read(e,P=P);r=[]
    for o,u in units(d):
        for w in W:
            for enc in ('utf-16-le','latin1'):
                c=u.count(w.encode(enc))
                if c: r.append(('%08x'%e[0],d[:4],o,w,enc[:3],c,len(u)))
    return r
if __name__=='__main__':
    T=[e for e in vc.table() if e[1]<40_000_000]
    with Pool(12) as p:
        for r in p.imap_unordered(job,T,chunksize=8):
            for x in r: print(*x)
