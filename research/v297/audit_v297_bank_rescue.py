#!/usr/bin/env python3
"""Independent exhaustive oracle and fail-closed V297 aggregate audit.
Does not use the JavaScript candidate's greedy, oracle, or port-safety functions.
"""
import itertools
import json
import math
import sys
from collections import Counter


def feasible(indices, requests, valid, capacity):
    if len(indices) > capacity or any(not valid[i] for i in indices):
        return False
    counts = Counter(bank for i in indices for bank in requests[i])
    return all(value <= 2 for value in counts.values())


def audit_exhaustive():
    cases = 0
    for flat in itertools.product(range(3), repeat=6):
        req = [flat[0:2], flat[2:4], flat[4:6]]
        for valid in itertools.product((False, True), repeat=3):
            for B in (1, 2):
                greedy = []
                for i in range(3):
                    if feasible(greedy + [i], req, valid, B):
                        greedy.append(i)
                oracle = max(len(subset) for size in range(B+1)
                             for subset in itertools.combinations(range(3), size)
                             if feasible(subset, req, valid, B))
                blocker = (B == 2 and len(greedy) == 1 and
                           feasible([1, 2], req, valid, B))
                selected = [1, 2] if blocker else greedy
                assert feasible(selected, req, valid, B)
                assert len(selected) == oracle
                assert len(selected) - len(greedy) == int(blocker)
                cases += 1
    assert cases == 11664
    return cases


def audit_report(obj):
    assert obj['evidenceTier'] == 'SYNTHETIC_THREE_REQUEST_ADMISSION_ONLY'
    assert obj['exhaustive']['canonicalCases'] == 5832
    assert obj['exhaustive']['configurationsChecked'] == audit_exhaustive()
    assert obj['exhaustive']['mutantDetected'] is True
    assert obj['cyclesPerSeed'] == 100000
    assert [r['regime'] for r in obj['results']] == [
        'motif_iid', 'uniform16', 'all_hot', 'single_issue', 'single_ready', 'bursty']
    for r in obj['results']:
        dev, hold = r['development'], r['holdout']
        p, eg = dev['p'], dev['baseline']
        expected = p / (1 + p)
        assert math.isclose(r['iidPredictedGain'], expected, abs_tol=1e-12)
        assert math.isclose(r['breakEvenClockRatio'], eg / (eg + expected), abs_tol=1e-12)
        assert math.isclose(r['absolutePredictionError'], abs(hold['gain']-expected), abs_tol=1e-12)
        assert r['withinFrozenTolerance'] == (r['absolutePredictionError'] <= .005)
        assert hold['gain'] >= 0 and hold['gain'] <= hold['p'] + 1e-9
        assert hold['baseline'] <= hold['oracle'] + 1e-9
        assert hold['baseline'] + hold['gain'] <= hold['oracle'] + 1e-9
        assert r['maxPortViolations'] == 0
        assert r['holdoutSeeds'] == [2027,2039,2053,2063]
        if r['regime'] not in ('motif_iid', 'uniform16', 'bursty'):
            assert hold['gain'] == 0
        if r['regime'] != 'bursty':
            assert r['withinFrozenTolerance']
        else:
            assert not r['withinFrozenTolerance']  # preserve observed iid failure
    assert all(obj[k] is False for k in ('rtlValidated','physicalTimingValidated','matchedAreaValidated','actualGpuThroughputValidated'))
    return {'independentExhaustiveCases':11664,'regimes':len(obj['results']),'iidStressFailurePreserved':True,'gpuPerformanceEstablished':False}


if __name__ == '__main__':
    assert len(sys.argv)==2, 'usage: audit_v297_bank_rescue.py results.json'
    data=json.load(open(sys.argv[1], encoding='utf8'))
    print(json.dumps(audit_report(data), sort_keys=True))
