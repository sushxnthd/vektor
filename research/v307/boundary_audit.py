"""Exact independent bank-pair compatibility law; pilot-only diagnostic.

This is a classical combinatorial law, not a V307 throughput predictor.
"""
from itertools import combinations
from math import comb
from simulator import program


def compatibility_probability(banks, k, operands=2):
    if banks < k * operands: return 0.0
    total = 1.0
    for i in range(k):
        total *= comb(banks - i*operands, operands)/comb(banks, operands)
    return total


def measure(regime, seeds=(31,32,33,34)):
    counts={2:[0,0],3:[0,0]}
    for seed in seeds:
        queues=program(seed,regime)
        for j in range(48):
            masks=[q[j] for q in queues]
            for k in (2,3):
                for group in combinations(range(5),k):
                    used=0
                    good=True
                    for w in group:
                        if used & masks[w]: good=False
                        used |= masks[w]
                    counts[k][0]+=good
                    counts[k][1]+=1
    return {k: {'compatible':v[0], 'total':v[1], 'rate':v[0]/v[1]} for k,v in counts.items()}

if __name__=='__main__':
    p2=compatibility_probability(8,2)
    p3=compatibility_probability(8,3)
    assert abs(p2-15/28)<1e-12
    assert abs(p3-90/784)<1e-12
    print('exact iid compatibility',p2,p3)
    for r in ('W1','N1','N2'): print(r,measure(r))
