"""Exhaustive negative control: EDF vs hindsight optimum for unit requests.

Single output slot/cycle, unit requests, release/deadline windows, two
nominal banks. Synthetic scheduling only; not a physical GPU claim.
"""
from functools import lru_cache
from itertools import product
import json

H = 4

def edf(jobs):
    done = set()
    for t in range(H):
        eligible = [i for i, (r,d,b) in enumerate(jobs)
                    if i not in done and r <= t <= d]
        if eligible:
            done.add(min(eligible, key=lambda i: (jobs[i][1],jobs[i][0],i)))
    return len(done)

def oracle(jobs):
    @lru_cache(None)
    def solve(t,used):
        if t == H: return 0
        options = [i for i,(r,d,b) in enumerate(jobs)
                   if not (used >> i & 1) and r <= t <= d]
        return max([solve(t+1,used)] +
                   [1+solve(t+1,used|(1<<i)) for i in options])
    return solve(0,0)

def audit():
    types = [(r,d,b) for r in range(H) for d in range(r,H) for b in (0,1)]
    cases = matches = 0
    for jobs in product(types,repeat=3):
        e,o = edf(jobs),oracle(jobs)
        assert o >= e
        cases += 1
        matches += e == o
        renamed = tuple((r,d,1-b) for r,d,b in jobs)
        assert edf(renamed) == e and oracle(renamed) == o
    assert cases == 8000 and matches == cases
    return dict(evidence_tier="SYNTHETIC_EXHAUSTIVE_NOT_PHYSICAL",
                cases=cases,edf_matches_hindsight=matches,
                hindsight_improvement_cases=cases-matches,
                physical_validation=False,
                inference="No scheduling headroom in this restricted unit-job single-output model; does not generalize to multi-output or nonunit service.")

if __name__ == "__main__":
    print(json.dumps(audit(),indent=2))
