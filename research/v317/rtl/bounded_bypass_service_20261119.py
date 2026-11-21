"""Exact four-request bounded-bypass combinational headroom; NOT RTL or GPU IPC.

Each request has two bank reads; each bank has two read ports. The oldest
request has index zero. A selected request may bypass at most K unselected
older requests in the same arbitration batch. This is NOT a lifetime bound
on waiting or a starvation-freedom proof. No output-port limit is imposed,
matching the existing oldest_protected_oracle_20261119.py model.
Run: python research/v317/rtl/bounded_bypass_service_20261119.py
"""
from itertools import product, combinations
from collections import Counter
from fractions import Fraction

def legal(q, ids):
    return all(n<=2 for n in Counter(b for i in ids for b in q[i]).values())

def permitted(ids,k):
    chosen=set(ids)
    return all(sum(j not in chosen for j in range(i))<=k for i in ids)

def greedy(q):
    chosen=[]
    for i in range(4):
        if legal(q,chosen+[i]): chosen.append(i)
    return len(chosen)

def optimum(q,k):
    return max(len(ids) for n in range(5)
               for ids in combinations(range(4),n)
               if legal(q,ids) and permitted(ids,k))

def check(b):
    totals=[0]*5
    for flat in product(range(b),repeat=8):
        q=tuple(zip(flat[::2],flat[1::2]))
        g=greedy(q)
        vals=[optimum(q,k) for k in range(4)]
        assert vals==sorted(vals) and vals[-1]>=g
        totals[0]+=g
        for k,v in enumerate(vals):totals[k+1]+=v
    return totals

if __name__=="__main__":
    for b,expected in ((2,[442,352,456,494,494]),
                       (3,[14391,11745,15135,15435,15435])):
        got=check(b)
        assert got==expected,(b,got)
        print("PASS",b,"banks",got,"K1/greedy",Fraction(got[2],got[0]),
              "K2/greedy",Fraction(got[3],got[0]))
