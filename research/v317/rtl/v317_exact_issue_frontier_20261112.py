"""Finite FIFO pipeline: exact issue-spacing break-even frontier.

Synthetic falsification only; not an RTL, routed, or measured GPU result.
For fixed workload order, candidate makespan is monotone nondecreasing in
issue spacing h. Compute an exact rational piecewise-linear frontier by
enumerating event-path affine forms, independently checked by recurrence.
"""
from fractions import Fraction as Q
from itertools import product

def recurrence(a,b,h):
    comp=bank=Q(0)
    for i,(x,y) in enumerate(zip(a,b)):
        comp=max(comp,Q(i)*h)+x
        bank=max(bank,comp)+y
    return bank

def path_lines(a,b):
    """All source-to-sink path affine expressions alpha*h+beta.

    A path may start at any issue-release node i*h or the time-zero source.
    Recurrences are max-plus, so propagate all possible affine paths.
    """
    comp=[]
    bank=[]
    for i,(x,y) in enumerate(zip(a,b)):
        release={(Q(i),x)}
        if i: release|={(m,z+x) for m,z in comp}
        comp=release
        nextbank={(m,z+y) for m,z in comp}
        if i: nextbank|={(m,z+y) for m,z in bank}
        bank=nextbank
    return bank

def evaluate(lines,h):
    return max(m*h+z for m,z in lines)

def exact_frontier(a,b,r,c):
    base=recurrence(a,b,Q(0))
    lines=path_lines(a,tuple(x/r for x in b))
    # Candidate must satisfy c*max(m*h+z) < base.
    # At h=0, failure cannot be repaired by increasing h.
    if c*evaluate(lines,Q(0))>=base:
        return None
    bounds=[(base/c-z)/m for m,z in lines if m>0]
    return min(bounds) if bounds else None

def test():
    values=(Q(1),Q(2),Q(3))
    checked=0
    for a in product(values,repeat=3):
      for b in product(values,repeat=3):
       for r,c in ((Q(2),Q(101,100)),(Q(3,2),Q(21,20))):
        lines=path_lines(a,b)
        for h in (Q(0),Q(1,3),Q(1),Q(5,2)):
         assert evaluate(lines,h)==recurrence(a,b,h)
         checked+=1
        frontier=exact_frontier(a,b,r,c)
        if frontier is not None:
         assert frontier>0
         base=recurrence(a,b,Q(0))
         assert c*recurrence(a,tuple(x/r for x in b),frontier)==base
         assert c*recurrence(a,tuple(x/r for x in b),frontier/2)<base
         assert c*recurrence(a,tuple(x/r for x in b),frontier+Q(1,100))>base
    print("PASS",checked,"independent max-plus checks; exact frontiers")

if __name__=="__main__":
    test()
