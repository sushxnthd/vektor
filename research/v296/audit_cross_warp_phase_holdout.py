#!/usr/bin/env python3
"""Independent fail-closed CSV auditor for V296 phase-correlation prospective cells.

Reimplements the event generator and bank-port admission check without importing
cross_warp_phase_law; imports only the pre-existing exact IID prediction model.
"""
import argparse
import bisect
import csv
import random
from collections import Counter
from itertools import accumulate
from pathlib import Path

from four_request_admission_law import exact_expected

REGIMES = {
    "uniform_control": (0.0, 0.0, 0.0),
    "uniform_partial_sync": (0.0, 0.0, 0.25),
    "uniform_strong_sync": (0.0, 0.0, 0.8),
    "moderate_hotspot_sync": (0.45, 0.2, 0.65),
    "heavy_hotspot_sync": (0.8, 0.2, 0.95),
}
SEEDS = (20261031, 20261101, 20261102)
BATCHES = 30000


def replay(h, rho, s, seed):
    rng = random.Random(seed)
    p = [h + (1-h)/16] + [(1-h)/16]*15
    cdf = list(accumulate(p))
    def bank():
        return min(15, bisect.bisect_right(cdf, rng.random()))
    count = 0
    for _ in range(BATCHES):
        phase = rng.random() < s
        if phase:
            a = bank()
            b = a if rng.random() < rho else bank()
            req = [(a,b)] * 4
        else:
            req = []
            for _ in range(4):
                a = bank()
                b = a if rng.random() < rho else bank()
                req.append((a,b))
        occupied = Counter()
        for a,b in req:
            d = Counter((a,b))
            if all(occupied[k]+v <= 2 for k,v in d.items()):
                occupied.update(d)
                count += 1
    return count


def audit(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    expected = {(name,seed) for name in REGIMES for seed in SEEDS}
    found = set()
    max_error = 0.0
    for row in rows:
        name, seed = row["regime"], int(row["seed"])
        key = (name,seed)
        if key not in expected or key in found:
            raise AssertionError("unknown or duplicate prospective cell")
        found.add(key)
        h,rho,s = REGIMES[name]
        if any(float(row[k]) != x for k,x in (("h",h),("rho",rho),("s",s))):
            raise AssertionError("frozen regime altered")
        if int(row["batches"]) != BATCHES:
            raise AssertionError("frozen batch count altered")
        observed = int(row["observed_admissions_total"])
        if not 0 <= observed <= 4*BATCHES or observed != replay(h,rho,s,seed):
            raise AssertionError("independent event replay disagrees")
        iid = exact_expected(h,rho,4)
        same = rho+(1-rho)*(sum(x*x for x in [h+(1-h)/16]+[(1-h)/16]*15))
        pred = (1-s)*iid+s*(2-same)
        if abs(float(row["predicted_admissions_per_batch"])-pred) > 1e-9:
            raise AssertionError("prediction not derived from frozen formula")
        if abs(float(row["iid_prediction_per_batch"])-iid) > 1e-9:
            raise AssertionError("IID control mismatch")
        error = abs(observed/BATCHES-pred)
        max_error = max(max_error,error)
        if error > 0.035 or row["independent_audit_equal"] != "True" or row["pass_0035"] != "True":
            raise AssertionError("prospective error or pass flag mismatch")
        if name in ("uniform_strong_sync","moderate_hotspot_sync") and abs(observed/BATCHES-iid)<0.25:
            raise AssertionError("IID transfer falsification gate failed")
    if found != expected or len(rows) != 15:
        raise AssertionError("missing prospective cells")
    print("V296_PHASE_INDEPENDENT_CSV_AUDIT_PASS cells=15 max_error=%.8f" % max_error)


def self_test():
    assert replay(1,1,1,20261031) == BATCHES
    try:
        audit(Path("/definitely/missing.csv"))
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing evidence accepted")
    print("V296_PHASE_INDEPENDENT_CSV_SELFTEST_PASS")


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--csv",type=Path)
    a=p.parse_args()
    if a.self_test:self_test()
    if a.csv:audit(a.csv)
    if not a.self_test and not a.csv:p.error("select --self-test or --csv")
