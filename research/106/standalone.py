"""Vektor-106 minimal, zero-dependency independent sector-law reproducer.
Host-side SGEMM memory-expression replay, NOT GPU execution or compiler tracing.
"""
from collections import Counter
from dataclasses import dataclass
from math import ceil
import random

@dataclass(frozen=True)
class Case:
    warps: int
    pitch: int
    steps: int
    sector: int = 128

def count(c, affine):
    lanes = [(w, l) for w in range(c.warps) for l in range(32)]
    if affine:
        lanes.sort(key=lambda p: ((p[0]//2)*4+p[1]//8, p[0], p[1]))
    groups = [lanes[i:i+32] for i in range(0, len(lanes), 32)]
    moved = 0
    by_op = Counter()
    for group in groups:
        home = sorted(Counter(w for w, _ in group).items(), key=lambda x: (-x[1], x[0]))[0][0]
        moved += sum(w != home for w, _ in group)
        for k in range(c.steps):
            A = set()
            B = set()
            for w, lane in group:
                row = (w//2)*4 + lane//8
                col = (w%2)*8 + lane%8
                A.add((0x100000 + 4*(row*c.pitch+k))//c.sector)
                B.add((0x200000 + 4*(k*c.pitch+col))//c.sector)
            by_op['A'] += len(A)
            by_op['B'] += len(B)
        C = set()
        for w, lane in group:
            row = (w//2)*4 + lane//8
            col = (w%2)*8 + lane%8
            C.add((0x300000 + 4*(row*c.pitch+col))//c.sector)
        by_op['C'] += len(C)
    return sum(by_op.values()), moved, by_op

def main():
    rng = random.Random(1062026)
    structured = []
    for _ in range(112):
        c = Case(rng.choice([2,4,6,8,10,12,14,16]), 32*rng.randint(1,16), rng.randint(1,32))
        b, _, _ = count(c, False)
        a, m, _ = count(c, True)
        structured.append((b-a == 2*c.warps*(c.steps+1), m == 16*c.warps))
    surprise = []
    for _ in range(16):
        c = Case(rng.choice([1,2,3,4,5,7,9,11]), rng.choice([33,47,63,65,96,129]),
                 rng.randint(1,48), rng.choice([64,128,256]))
        b, _, _ = count(c, False)
        a, m, _ = count(c, True)
        surprise.append((b-a == 2*c.warps*(c.steps+1), m == 16*c.warps, b-a))
    assert all(a and b for a,b in structured)
    assert sum(x[0] for x in surprise) == 2
    assert sum(x[1] for x in surprise) == 6
    wins = losses = ties = 0
    for w in (2,4,8):
        for k in (1,2,4,8,16,32):
            c = Case(w,128,k)
            b,_,_=count(c,False)
            a,m,_=count(c,True)
            for B in (1,2,4,8,16,32,64):
                for M in (4,8,16,32,64):
                    for setup in (0,8,32):
                        d=ceil(b/B)-(ceil(a/B)+ceil(m/M)+setup)
                        wins+=d>0;losses+=d<0;ties+=d==0
    assert (wins,losses,ties)==(689,1110,91)
    print('PASS 112/112 aligned SGEMM predictions; 16 surprise probes')
    print('PASS 1890 non-overlap cost proxies:',wins,'wins',losses,'losses',ties,'ties')
    print('All numbers are host-side sector counts or service proxies, not GPU cycles.')

if __name__ == '__main__': main()
