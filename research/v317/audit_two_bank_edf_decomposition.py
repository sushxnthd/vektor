"""Independent exhaustive audit: two-bank EDF decomposes under full bank-width output.

Model: two independent single-port banks, two output slots per cycle, unit
requests with inclusive release/deadline windows. No shared downstream
bottleneck, multi-bank atomicity, queue head blocking, or service latency.
This is a synthetic negative control, NOT a physical GPU performance result.
"""
from functools import lru_cache
from itertools import product
import json

H = 3
TYPES = [(r, d, b) for r in range(H) for d in range(r, H) for b in (0, 1)]

def eligible(jobs, t, used):
    return [i for i, (r, d, _) in enumerate(jobs)
            if not (used >> i & 1) and r <= t <= d]

def edf(jobs):
    used = 0
    for t in range(H):
        candidates = sorted(eligible(jobs, t, used),
                            key=lambda i: (jobs[i][1], jobs[i][0], i))
        banks = set()
        for i in candidates:
            bank = jobs[i][2]
            if bank not in banks:
                used |= 1 << i
                banks.add(bank)
    return used.bit_count()

def oracle(jobs):
    @lru_cache(None)
    def solve(t, used):
        if t == H:
            return 0
        candidates = eligible(jobs, t, used)
        actions = [()]
        actions += [(i,) for i in candidates]
        actions += [(i, j) for i in candidates for j in candidates
                    if i < j and jobs[i][2] != jobs[j][2]]
        return max(len(action) + solve(t + 1, used | sum(1 << i for i in action))
                   for action in actions)
    return solve(0, 0)

def audit():
    cases = matches = 0
    for jobs in product(TYPES, repeat=4):
        e, o = edf(jobs), oracle(jobs)
        assert e <= o, (jobs, e, o)
        assert e == o, (jobs, e, o)
        renamed = tuple((r, d, 1 - b) for r, d, b in jobs)
        assert edf(renamed) == e and oracle(renamed) == o
        cases += 1
        matches += e == o
    assert cases == 20736
    return dict(evidence_tier="SYNTHETIC_EXHAUSTIVE_NOT_PHYSICAL",
                cases=cases, edf_matches_oracle=matches,
                improvement_cases=cases - matches,
                inference="With independent banks and enough output slots, per-bank EDF is a strong zero-headroom control in this bounded model.",
                limitations="Not a theorem for unbounded jobs, shared outputs, atomic multi-bank requests, FIFO, or real GPU traces.")

if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
