"""Independent counterexample to treating aggregate bank pressure as matching capacity.

No V307 policy parameters or frozen workload generation are modified.
"""
from itertools import combinations
from simulator import next_pressure, legal


def audit():
    a=(3,3,3,192)  # three (bank0,bank1) edges, one (bank6,bank7)
    b=(3,3,5,9)    # all edges share bank0
    def evaluate(masks):
        queues=tuple((m,) for m in masks)
        h=(0,)*4
        return next_pressure(h,queues),max(s.bit_count() for s in legal(h,queues))
    assert evaluate(a)==(4,2), evaluate(a)
    assert evaluate(b)==(4,1), evaluate(b)
    print({'case_a':{'masks':a,'pressure':4,'max_issued':2},
           'case_b':{'masks':b,'pressure':4,'max_issued':1},
           'conclusion':'Pressure alone cannot determine conflict-free issue capacity'})

if __name__=='__main__': audit()
