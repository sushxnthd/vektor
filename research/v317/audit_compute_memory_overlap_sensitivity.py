#!/usr/bin/env python3
"""Exact overlap-sensitivity audit for the archived V317 workload roofline.

The prior max(compute,memory) model assumes perfect overlap. This audit
interpolates between full overlap and serialized service; it is NOT a GPU
measurement and cannot override electrical or area no-go decisions.
"""
from fractions import Fraction as Q

def time_seconds(compute, memory, overlap):
    """T = C + M - overlap*min(C,M), overlap in [0,1]."""
    C, M, a = Q(compute), Q(memory), Q(overlap)
    if C <= 0 or M <= 0 or not 0 <= a <= 1:
        raise ValueError("invalid service or overlap")
    return C + M - a * min(C, M)

def speedup(cb, mb, cc, mc, overlap_base, overlap_candidate):
    return time_seconds(cb, mb, overlap_base) / time_seconds(
        cc, mc, overlap_candidate)

def minimum_candidate_overlap(cb, mb, cc, mc, overlap_base):
    """Strict speedup requires candidate overlap > returned threshold."""
    target = time_seconds(cb, mb, overlap_base)
    return (Q(cc) + Q(mc) - target) / min(Q(cc), Q(mc))

def test():
    # Prior illustrative clock/cycle regime: Cb=1s, Cc=900/975s;
    # equal 0.4s memory floor. No measured workload is asserted.
    cb, cc, mb, mc = Q(1), Q(900,975), Q(2,5), Q(2,5)
    assert speedup(cb,mb,cc,mc,1,1) == Q(975,900)
    assert speedup(cb,mb,cc,mc,0,0) == Q(7,5) / (cc+mc) > 1
    # Baseline full overlap, candidate zero overlap: nominal compute win reverses.
    assert speedup(cb,mb,cc,mc,1,0) < 1
    threshold = minimum_candidate_overlap(cb,mb,cc,mc,1)
    assert threshold == Q(21,26)
    assert speedup(cb,mb,cc,mc,1,threshold) == 1
    assert speedup(cb,mb,cc,mc,1,threshold-Q(1,100)) < 1
    assert speedup(cb,mb,cc,mc,1,threshold+Q(1,100)) > 1
    for i in range(101):
        a=Q(i,100)
        assert time_seconds(cb,mb,a) >= max(cb,mb)
        assert time_seconds(cb,mb,a) <= cb+mb
        if i:
            assert time_seconds(cb,mb,a) <= time_seconds(cb,mb,Q(i-1,100))
    for args in [(0,1,1,1,1,1),(1,1,1,1,-1,1),(1,1,1,1,1,2)]:
        try: speedup(*args)
        except ValueError: pass
        else: raise AssertionError("invalid input accepted")
    return threshold

if __name__ == "__main__":
    threshold=test()
    print("PASS: overlap endpoints, exact crossover, 101 monotonic bounds, 3 invalid controls")
    print("Candidate overlap must exceed", threshold, "when baseline fully overlaps")
    print("No RTL/electrical/real-kernel validation claimed.")
