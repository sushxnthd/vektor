#!/usr/bin/env python3
"""V296 bank-port contention falsifier, not a routed GPU measurement.

Prospective synthetic workloads: WIN = disjoint bank alternating streams;
NO_WIN = all requests to bank zero. Both frozen before execution.
Compare identical bank-port count and total request count. Pairwise candidate
has a fixed arbitration overhead per issued pair; baseline greedy has none.
The model is deliberately unfavorable to free bandwidth assumptions.
"""
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class Work:
    name: str
    banks: tuple[int, ...]
    predicted: str

FROZEN = (
    Work("disjoint_alternating", (0,1)*64, "WIN"),
    Work("single_bank_hotspot", (0,)*128, "NO_WIN"),
)

def simulate(work, pairwise, service=4, issue=1, pair_overhead=1, bank_count=2):
    """Discrete nonpreemptive bank queues, one port per bank, finite issue pacing.

    Candidate may issue two adjacent requests together only if their banks
    differ. The extra arbitration overhead is paid per attempted pair,
    including incompatible pairs. Baseline issues one request per issue slot.
    """
    assert service > 0 and issue > 0 and pair_overhead >= 0 and bank_count > 0
    assert all(0 <= b < bank_count for b in work.banks)
    free = [0]*bank_count
    t = 0
    i = 0
    while i < len(work.banks):
        paired = pairwise and i+1 < len(work.banks) and work.banks[i] != work.banks[i+1]
        count = 2 if paired else 1
        if pairwise:
            t += pair_overhead
        for b in work.banks[i:i+count]:
            free[b] = max(t, free[b]) + service
        t += issue
        i += count
    return max(t, *free)

def evaluate(work, service=4, issue=1, overhead=1, area_ratio=Fraction(1001,1000), clock_ratio=Fraction(1001,1000)):
    base = simulate(work, False, service, issue, overhead)
    cand = simulate(work, True, service, issue, overhead)
    gain = Fraction(base, cand) / area_ratio / clock_ratio
    return base, cand, gain

def run():
    for w in FROZEN:
        b,c,g = evaluate(w)
        actual = "WIN" if g > 1 else "NO_WIN"
        assert actual == w.predicted, (w.name,b,c,str(g),actual)
        print(f"{w.name}: baseline={b} candidate={c} throughput_per_area={float(g):.6f} predicted={w.predicted}")
    # Sensitivity: heavier candidate overhead cannot improve its completion time.
    for w in FROZEN:
        last = 0
        for overhead in range(0, 17):
            cycles = simulate(w, True, pair_overhead=overhead)
            assert cycles >= last
            last = cycles
    # No bank capacity is created by fusion: all-hot request completion
    # cannot beat the service lower bound for a single port.
    hot = FROZEN[1]
    assert simulate(hot, True) >= len(hot.banks)*4
    print("synthetic prospective predictions and monotonicity checks passed")

if __name__ == "__main__":
    run()
