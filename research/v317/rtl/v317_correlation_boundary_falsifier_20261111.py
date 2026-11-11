#!/usr/bin/env python3
"""Exact marginal-preserving correlation falsifier for V317 bank service.

Four ready two-source requests, two read ports per bank. Compare fixed-order
compact greedy with a zero-cost maximum-cardinality oracle. Independent draws
and shared-bank bursts have identical per-operand marginals, but different
cross-operand correlation. No RTL, timing, or GPU throughput claim.
"""
from fractions import Fraction
from itertools import product
import json

def grant_count(operands, banks):
    requests = list(zip(operands[::2], operands[1::2]))
    def legal(mask):
        counts = [0] * banks
        for i, (a, b) in enumerate(requests):
            if mask >> i & 1:
                counts[a] += 1
                counts[b] += 1
        return max(counts) <= 2
    mask = 0
    for i in range(4):
        if legal(mask | (1 << i)):
            mask |= 1 << i
    return mask.bit_count(), max(m.bit_count() for m in range(16) if legal(m))

def iid(banks, probs):
    g = o = Fraction(0)
    for x in product(range(banks), repeat=8):
        weight = Fraction(1)
        for bank in x:
            weight *= probs[bank]
        a, b = grant_count(x, banks)
        g += weight * a
        o += weight * b
    return g, o

def burst(banks, probs):
    g = o = Fraction(0)
    for bank, weight in enumerate(probs):
        a, b = grant_count((bank,) * 8, banks)
        g += weight * a
        o += weight * b
    return g, o

def evaluate(banks, probs, alphas):
    gi, oi = iid(banks, probs)
    gb, ob = burst(banks, probs)
    assert gb == ob == 1
    results = []
    for alpha in alphas:
        g = alpha * gi + (1-alpha) * gb
        o = alpha * oi + (1-alpha) * ob
        ratio = o / g
        results.append(dict(iid_fraction=str(alpha), greedy=str(g),
                            oracle=str(o), maximum_clock_inflation=str(ratio),
                            frequency_loss_ceiling=str(1-1/ratio)))
    return dict(banks=banks, marginal_probabilities=list(map(str, probs)),
                iid_means=[str(gi),str(oi)], burst_means=[str(gb),str(ob)],
                regimes=results)

def run():
    alphas = [Fraction(0), Fraction(1,4), Fraction(1,2),
              Fraction(3,4), Fraction(1)]
    return dict(evidence="exact synthetic upper bound; not physical signoff",
                boundary="T_candidate/T_greedy < (alpha*O_iid+(1-alpha)*O_burst)/(alpha*G_iid+(1-alpha)*G_burst) is necessary for saturated service gain",
                caveat="Marginal bank histogram alone cannot identify the service boundary; cross-operand correlation matters.",
                cases=[evaluate(2,[Fraction(1,2)]*2,alphas),
                       evaluate(3,[Fraction(1,3)]*3,alphas),
                       evaluate(3,[Fraction(2,3),Fraction(1,6),Fraction(1,6)],alphas)])

if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
