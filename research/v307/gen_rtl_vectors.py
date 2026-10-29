"""Independent deterministic Python decision oracle for clocked RTL comparison."""
import random
from simulator import select

def make(seed, count):
    rng=random.Random(seed)
    for _ in range(count):
        ready=rng.randrange(1,32)
        valid=rng.randrange(32)&ready
        cur=0; nxt=0; qs=[]
        for w in range(5):
            a,b=rng.sample(range(8),2)
            c,d=rng.sample(range(8),2)
            m=(1<<a)|(1<<b); n=(1<<c)|(1<<d)
            cur|=m<<(w*8); nxt|=n<<(w*8)
            qs.append((m,n) if (ready>>w)&1 and (valid>>w)&1 else ((m,) if (ready>>w)&1 else ()))
        exp=[select((0,)*5,tuple(qs),p) for p in ('max_now','pressure','future_tie')]
        yield ready,valid,cur,nxt,*exp

if __name__=='__main__':
    for v in make(307,256): print(' '.join(f'{x:x}' for x in v))
