"""Exhaustive oldest-protected oracle vs same-port compact greedy.
Independent finite combinational enumeration; NOT a GPU IPC or physical result.
Run: python research/v317/rtl/oldest_protected_oracle_20261119.py
"""
from itertools import product
from collections import Counter

def legal(q, indices, ports=2):
    use=Counter(b for i in indices for b in q[i])
    return all(v<=ports for v in use.values())

def greedy(q):
    chosen=[]
    for i in range(4):
        if legal(q,chosen+[i]): chosen.append(i)
    return tuple(chosen)

def oracle(q, protect_oldest):
    candidates=[]
    for bits in range(16):
        ids=tuple(i for i in range(4) if bits & (1<<i))
        if (not protect_oldest or 0 in ids) and legal(q,ids):
            candidates.append(ids)
    return max(candidates,key=lambda ids:(len(ids),-sum(ids)))

def check(banks):
    totals=[0,0,0]
    improvements=[0,0]
    for flat in product(range(banks),repeat=8):
        q=tuple(tuple(flat[i:i+2]) for i in range(0,8,2))
        g=greedy(q); o=oracle(q,False); f=oracle(q,True)
        assert 0 in g and 0 in f
        assert legal(q,g) and legal(q,o) and legal(q,f)
        assert len(g)<=len(f)<=len(o)
        for j,x in enumerate((g,o,f)): totals[j]+=len(x)
        improvements[0]+=len(o)>len(g)
        improvements[1]+=len(f)>len(g)
    return banks,banks**8,totals,improvements

if __name__=="__main__":
    a=check(2); b=check(3)
    assert a==(2,256,[442,494,442],[52,0]),a
    assert b==(3,6561,[14391,15435,14667],[1044,276]),b
    print("PASS exhaustive independent old-head protection",a,b)
