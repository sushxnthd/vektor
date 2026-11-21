"""Independent exhaustive subset-mask audit of V317 weighted protected service.
Run: python3 research/v317/rtl/independent_weighted_mask_audit_20261120.py
Unlike the reference combinations checker, use bitmasks and port-vector feasibility.
No queue, fairness-over-time, timing, energy, or GPU performance claim.
"""
from itertools import product
from collections import defaultdict
from fractions import Fraction

def evaluate(flat):
    req = [flat[i:i+2] for i in range(0, 8, 2)]
    def fits(mask):
        ports = [0]*4
        for i in range(4):
            if mask & (1 << i):
                for bank in req[i]:
                    ports[bank] += 1
        return max(ports) <= 2
    greedy = 0
    for i in range(4):
        trial = greedy | (1 << i)
        if fits(trial):
            greedy = trial
    feasible_protected = [mask for mask in range(1, 16, 2) if fits(mask)]
    assert feasible_protected
    protected = max(mask.bit_count() for mask in feasible_protected)
    return greedy.bit_count(), protected

def main():
    histogram = defaultdict(int)
    totals = {h:[0,0] for h in (1,2,3,5)}
    for flat in product(range(4), repeat=8):
        g,p = evaluate(flat)
        histogram[(g,p)] += 1
        for h in totals:
            weight = h ** sum(x == 0 for x in flat)
            totals[h][0] += weight*g
            totals[h][1] += weight*p
    expected_hist = {(1,1):1468,(2,2):22620,(2,3):2496,
                     (3,3):36432,(4,4):2520}
    expected_totals = {1:(171076,173572),2:(963271,976891),
                       3:(3772044,3818364),5:(31796356,32049412)}
    assert dict(histogram) == expected_hist
    assert sum(histogram.values()) == 4**8
    for h,(g,p) in totals.items():
        assert (g,p) == expected_totals[h]
        assert Fraction(p,g) < Fraction(51,50)
        print(f"h={h} greedy={g} protected={p} ratio={float(Fraction(p,g)):.9f}")
    print("PASS independent 65536-case mask audit; 2496 strict improvements")
if __name__ == "__main__":
    main()
