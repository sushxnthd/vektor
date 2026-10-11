"""Vektor-107: host-side cache-stage accounting, NOT GPU performance."""
from collections import OrderedDict
from random import Random

def evaluate(w=2,pitch=128,steps=8,sector=32,cap=0,ways=1,order="step",regroup=False):
    lanes=[(w0,l) for w0 in range(w) for l in range(32)]
    if regroup:
        lanes.sort(key=lambda t:((t[0]//2)*4+t[1]//8,t[0],t[1]))
    groups=[lanes[i:i+32] for i in range(0,len(lanes),32)]
    tasks=((g,op,k) for k in range(steps) for op in ("A","B") for g in groups) if order=="step" else ((g,op,k) for g in groups for k in range(steps) for op in ("A","B"))
    sets=[OrderedDict() for _ in range(cap//ways if cap else 0)]
    reads=writes=misses=hits=0
    def address(warp,lane,op,k):
        row=(warp//2)*4+lane//8
        col=(warp%2)*8+lane%8
        if op=="A":return 0x100000+4*(row*pitch+k)
        if op=="B":return 0x200000+4*(k*pitch+col)
        return 0x300000+4*(row*pitch+col)
    def consume(group,op,k):
        nonlocal reads,writes,misses,hits
        sectors=sorted({address(a,b,op,k)//sector for a,b in group})
        if op=="C":
            writes+=len(sectors);return
        reads+=len(sectors)
        for s in sectors:
            if not sets:
                misses+=1;continue
            st=sets[s%len(sets)]
            if s in st:
                hits+=1;st.move_to_end(s)
            else:
                misses+=1
                if len(st)==ways:st.popitem(last=False)
                st[s]=None
    for g,op,k in tasks:consume(g,op,k)
    for g in groups:consume(g,"C",0)
    return reads,writes,misses,hits

def verify():
    assert evaluate()==(80,8,80,0)
    assert evaluate(regroup=True)==(64,8,64,0)
    assert evaluate(sector=128)==(80,8,80,0)
    assert evaluate(sector=128,regroup=True)==(48,4,48,0)
    assert evaluate(cap=256,ways=256)==(80,8,20,60)
    assert evaluate(cap=256,ways=256,regroup=True)==(64,8,20,44)
    rng=Random(1077707);neg=[0,0]
    for _ in range(96):
        w=rng.choice([2,4,6,8,10,12])
        p=rng.choice([32,64,96,128,256])
        k=rng.choice([1,2,4,8,16])
        s=rng.choice([32,64,128])
        cap=rng.choice([0,4,8,16,32,64,128,256])
        ways=min(cap,rng.choice([1,2,4,8,16])) if cap else 1
        for i,order in enumerate(("step","group")):
            b=evaluate(w,p,k,s,cap,ways,order,False)
            a=evaluate(w,p,k,s,cap,ways,order,True)
            assert b[0]==b[2]+b[3] and a[0]==a[2]+a[3]
            neg[i]+=a[2]>b[2]
    assert neg==[0,5],neg
    print("PASS: 32B 88->72, 128B 88->52, ideal cache 20->20")
    print("PASS: 96 paired issue-order tests; regressions step=0 group=5")

if __name__=="__main__":verify()
