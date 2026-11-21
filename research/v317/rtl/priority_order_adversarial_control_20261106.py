#!/usr/bin/env python3
"""Independent priority-order control for the frozen V317 four-request bank example."""
from itertools import permutations
from collections import Counter

REQUESTS=((0,1),(0,0),(1,1),(2,2))

def admit(requests, order, ports=2, output_cap=4):
    used=Counter(); admitted=[]
    for i in order:
        if len(admitted)>=output_cap: break
        a,b=requests[i]; demand=Counter((a,b))
        if all(used[k]+v<=ports for k,v in demand.items()):
            used.update(demand); admitted.append(i)
    return tuple(admitted)

def run():
    scores={order:len(admit(REQUESTS,order)) for order in permutations(range(4))}
    fixed=scores[tuple(range(4))]
    best=max(scores.values())
    rotating=[scores[tuple(range(k,4))+tuple(range(k))] for k in range(4)]
    assert fixed==2 and best==3 and rotating==[2,3,3,2]
    assert sum(rotating)==10
    assert len(scores)==24
    print('fixed_priority=',fixed,'best_static_priority=',best,
          'rotating_mean=',sum(rotating)/4,
          'oracle_over_best_static=',best/best,
          'oracle_over_rotating=',best/(sum(rotating)/4))
    print('best_orders=',sum(x==best for x in scores.values()),'of',len(scores))
if __name__=='__main__':run()
