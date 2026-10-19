import sys,os,collections;sys.path.insert(0,os.path.dirname(__file__));import vc,iso
T=vc.table();P=vc.parts()
out=open(sys.argv[1],'w',encoding='utf-8')
c=collections.Counter()
with open(iso.ISO,'rb') as f:
    for h,s,sec in T:
        f.seek(vc.iso_off(sec,P=P));b=f.read(32)
        out.write('%08x %10d %8d %s\n'%(h,s,sec,b.hex()))
        c[b[:4]]+=1
for k,v in c.most_common(): print(v,k)
