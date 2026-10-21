"""V266 reproducibility harness. E1 model, NOT RTL/STA/PPA."""
from itertools import product
from collections import Counter
from frozen_generator import generate
C=2;R=.95
INIT={0:0,1:1,2:2,3:3,4:0}
VALUES={i:(0x9e3779b9*(i+1))&0xffffffff for i in range(5)}
def cycles(loc,p):
    words,L=p
    return L*max(Counter(loc[w] for w in words).values())
def static_best(phases):
    ans=10**20
    for x in product(range(4),repeat=5):
        if max(Counter(x).values())>2:continue
        ans=min(ans,sum(cycles(dict(enumerate(x)),p) for p in phases))
    return ans
def adaptive(phases):
    loc=INIT.copy();bank=[{} for _ in range(4)]
    for w,b in loc.items():bank[b][w]=VALUES[w]
    total=moves=0
    for words,L in phases:
        counts=Counter(loc[w] for w in words)
        conflicted=[b for b,n in counts.items() if n>1]
        if conflicted and L>C:
            src=conflicted[0];cold=next(w for w in range(5) if w not in words)
            dest=loc[cold]
            if src!=dest and len(bank[dest])<2:
                w=min(w for w in words if loc[w]==src)
                bank[dest][w]=bank[src].pop(w);loc[w]=dest
                total+=C;moves+=1
        assert all(bank[loc[w]][w]==VALUES[w] for w in range(5))
        assert sum(map(len,bank))==5 and all(len(b)<=2 for b in bank)
        total+=cycles(loc,(words,L))
    return total,moves
for kind in ('positive','negative','divergent'):
    p=generate(kind);s=static_best(p);a,m=adaptive(p)
    print(kind,{'static':s,'adaptive':a,'moves':m,'clock_adjusted_gain':round(.95*s/a,6),'matched_compiler_scripted_gain':1.0})
