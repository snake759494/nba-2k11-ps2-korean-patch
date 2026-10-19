import sys,os,collections,json;sys.path.insert(0,os.path.dirname(__file__));import vc,lz,iso
T=vc.table();P=vc.parts();c=collections.Counter();out=[]
with open(iso.ISO,'rb') as f:
    for h,s,sec in T:
        if s>60_000_000: continue
        f.seek(vc.iso_off(sec,P=P));d=f.read(s)
        ch,end=lz.chain(d)
        for o,mg,A,B,C,D in ch:
            c[mg]+=1; out.append(['%08x'%h,o,mg.decode('latin1'),A,B,C,D])
        if not ch: out.append(['%08x'%h,-1,d[:4].decode('latin1'),s,0,0,0])
json.dump(out,open(sys.argv[1],'w'))
print(c.most_common())
