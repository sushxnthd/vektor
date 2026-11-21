"""Exact weighted oldest-protected oracle ceiling against scan greedy.
Run: python3 research/v317/rtl/weighted_protected_ceiling_20261120.py
Four ordered two-read requests, four banks, two ports/bank.
All 4^8 assignments; weights proportional to h^number_of_bank_zero_operands.
No hardware, queue, or throughput claim. Negative results retained.
"""
from itertools import product, combinations
from fractions import Fraction

def feasible(q, ids):
    use = [0]*4
    for i in ids:
        for b in q[i]:
            use[b] += 1
            if use[b] > 2:
                return False
    return True

def service(q):
    greedy = []
    for i in range(4):
        if feasible(q, greedy + [i]):
            greedy.append(i)
    protected = max(
        (ids for k in range(1,5)
         for ids in combinations(range(4),k)
         if 0 in ids and feasible(q,ids)),
        key=lambda ids: (len(ids), tuple(-j for j in ids)))
    assert 0 in protected and feasible(q, protected)
    return len(greedy), len(protected)

def run():
    totals = {h: [0,0] for h in (1,2,3,5)}
    for flat in product(range(4),repeat=8):
        q = tuple((flat[2*i],flat[2*i+1]) for i in range(4))
        g,p = service(q)
        for h in totals:
            weight = h ** flat.count(0)
            totals[h][0] += weight*g
            totals[h][1] += weight*p
    expected = {1:(171076,173572),2:(963271,976891),
                3:(3772044,3818364),5:(31796356,32049412)}
    for h,(g,p) in totals.items():
        assert (g,p) == expected[h]
        ratio = Fraction(p,g)
        assert ratio < Fraction(102,100)
        print(f"hot_weight={h} greedy={g} protected={p} ceiling={float(ratio):.9f} pass_no_win=True")
    print("PASS exact weighted protected-oracle service sensitivity")

if __name__ == "__main__":
    run()
