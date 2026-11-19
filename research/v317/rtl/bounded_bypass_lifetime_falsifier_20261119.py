"""Exhaustive witness for lifetime starvation under per-batch K=1 bypass.

Four queued requests, two bank reads each, two ports per bank. An arbitration
policy maximizes grants subject to each chosen request bypassing <=1 older
unselected request *in the current batch*. Among equal-cardinality choices,
select lexicographically smallest chosen index tuple. After grants, append
identical requests to restore four entries. This constructs a legal adversarial
arrival stream, not an empirical workload or RTL implementation.
"""
from collections import Counter
from itertools import combinations, product

def legal(q, ids):
    counts=Counter(bank for i in ids for bank in q[i])
    return all(count<=2 for count in counts.values())

def permitted(ids,k=1):
    chosen=set(ids)
    return all(sum(j not in chosen for j in range(i))<=k for i in ids)

def choose(q,k=1):
    feasible=[ids for n in range(5) for ids in combinations(range(4),n)
              if legal(q,ids) and permitted(ids,k)]
    return sorted(feasible,key=lambda ids:(-len(ids),ids))[0]

def find_witness(b=2):
    for flat in product(range(b),repeat=8):
        q=tuple(zip(flat[::2],flat[1::2]))
        selected=choose(q)
        if 0 in selected or not selected:continue
        survivors=tuple(req for i,req in enumerate(q) if i not in selected)
        for tail in product(tuple(product(range(b),repeat=2)),repeat=len(selected)):
            nxt=survivors+tail
            if nxt==q:
                return q,selected,tail
    return None

def test():
    w=find_witness()
    assert w is not None
    q,chosen,tail=w
    assert 0 not in chosen and len(q)==4 and legal(q,chosen)
    assert permitted(chosen,1)
    for cycle in range(1000):
        assert choose(q,1)==chosen
        q=tuple(req for i,req in enumerate(q) if i not in chosen)+tail
        assert q==w[0]
    print('PASS 1000-cycle oldest-starvation witness',w)

if __name__=='__main__':test()
