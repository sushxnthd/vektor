"""Independent bounded falsification of deadline-first atomic bank scheduling.

Two single-port banks, two output slots, unit-duration requests. A request
with mask 3 atomically consumes both bank ports but yields ONE completion.
All jobs have inclusive release/deadline windows over three cycles. The
oracle maximizes completed requests with hindsight; it is not implementable
as an online hardware scheduler. No physical throughput claim is made.
"""
from functools import lru_cache
from itertools import product
import json

H = 3
TYPES = [(r, d, mask) for r in range(H) for d in range(r, H)
         for mask in (1, 2, 3)]

def actions(jobs, t, done):
    available = [i for i, (r, d, _) in enumerate(jobs)
                 if not (done >> i & 1) and r <= t <= d]
    return [()] + [(i,) for i in available] + [
        (i, j) for i in available for j in available
        if i < j and not (jobs[i][2] & jobs[j][2])]

def score(jobs, policy):
    @lru_cache(None)
    def solve(t, done):
        if t == H:
            return 0
        choices = actions(jobs, t, done)
        if policy == 'oracle':
            return max(len(a) + solve(t + 1, done | sum(1 << i for i in a))
                       for a in choices)
        eligible = [i for i, (r, d, _) in enumerate(jobs)
                    if not (done >> i & 1) and r <= t <= d]
        if policy == 'edf':
            eligible.sort(key=lambda i: (jobs[i][1], jobs[i][0], i))
            selected, occupied = [], 0
            for i in eligible:
                if not (occupied & jobs[i][2]):
                    selected.append(i)
                    occupied |= jobs[i][2]
            chosen = tuple(selected)
        elif policy == 'max_cardinality_edf':
            chosen = min(choices, key=lambda a: (-len(a),
                tuple(sorted((jobs[i][1], jobs[i][0], i) for i in a))))
        else:
            raise ValueError(policy)
        return len(chosen) + solve(t + 1, done | sum(1 << i for i in chosen))
    return solve(0, 0)

def audit():
    counts = dict(cases=0, edf_below_oracle=0,
                  cardinality_below_oracle=0, cardinality_below_edf=0)
    witness = None
    for jobs in product(TYPES, repeat=3):
        edf = score(jobs, 'edf')
        cardinality = score(jobs, 'max_cardinality_edf')
        optimum = score(jobs, 'oracle')
        assert edf <= optimum and cardinality <= optimum
        swapped = tuple((r, d, ((m & 1) << 1) | ((m & 2) >> 1))
                        for r, d, m in jobs)
        assert score(swapped, 'oracle') == optimum
        counts['cases'] += 1
        counts['edf_below_oracle'] += edf < optimum
        counts['cardinality_below_oracle'] += cardinality < optimum
        counts['cardinality_below_edf'] += cardinality < edf
        if edf < optimum and witness is None:
            witness = dict(jobs=jobs, edf=edf,
                           cardinality=cardinality, oracle=optimum)
    assert counts['cases'] == 5832
    assert witness is not None
    return dict(evidence_tier='SYNTHETIC_EXHAUSTIVE_NOT_PHYSICAL',
                counts=counts, first_witness=witness,
                interpretation='Atomic two-bank requests break the independent-bank EDF decomposition; compare against a cardinality-aware equal-resource policy.',
                limitations='Small finite horizon; hindsight oracle; no RTL, physical legality, real kernel, or GPU IPC evidence.')

if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
