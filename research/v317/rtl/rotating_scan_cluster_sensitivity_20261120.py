#!/usr/bin/env python3
"""V317 development-only paired sensitivity; never evaluates reserved holdouts.

Post-hoc descriptive analysis, not a preregistered significance claim.
The four development seeds are the resampling unit, not the 60 correlated cells.
"""
import importlib.util
import math
from pathlib import Path
from collections import defaultdict

source = Path(__file__).with_name("rotating_scan_prospective_20261120.py")
spec = importlib.util.spec_from_file_location("v317_development", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
seeds = tuple(range(20261121, 20261125))
rows = module.evaluate(seeds)["rows"]
assert len(rows) == 60
by_seed = defaultdict(list)
by_regime = defaultdict(list)
by_rate = defaultdict(list)
for row in rows:
    ratio = row["rotating"]["throughput"] / row["compact"]["throughput"]
    assert ratio > 0 and math.isfinite(ratio)
    assert abs(ratio - row["ratio"]) < 1e-14
    by_seed[row["seed"]].append(math.log(ratio))
    by_regime[row["regime"]].append(math.log(ratio))
    by_rate[str(row["rate"])].append(math.log(ratio))
assert set(by_seed) == set(seeds)
assert all(len(v) == 15 for v in by_seed.values())
assert all(len(v) == 20 for v in by_regime.values())
assert all(len(v) == 12 for v in by_rate.values())

def gm(logs):
    return math.exp(sum(logs) / len(logs))

print("DEVELOPMENT ONLY; four seed clusters, 60 correlated cells; no holdout")
for seed in seeds:
    print("seed", seed, "geomean", format(gm(by_seed[seed]), ".12f"))
for seed in seeds:
    retained = [x for other in seeds if other != seed for x in by_seed[other]]
    print("leave-one-seed-out", seed, format(gm(retained), ".12f"))
for regime in sorted(by_regime):
    print("regime", regime, format(gm(by_regime[regime]), ".12f"))
for rate in sorted(by_rate):
    print("arrival", rate, format(gm(by_rate[rate]), ".12f"))
# Enumerate all 4**4 seed-level cluster resamples exactly; no pseudorandom bootstrap.
cluster_means = [sum(by_seed[s]) / 15 for s in seeds]
resamples = sorted(math.exp(sum(cluster_means[i] for i in indices) / 4)
                   for indices in __import__("itertools").product(range(4), repeat=4))
print("cluster bootstrap descriptive 2.5/97.5 pct", resamples[6], resamples[249])
print("max seed geomean", max(gm(v) for v in by_seed.values()))
# Conservative conditional upper bound: if no unmeasured physical factor improves
# effective throughput, multiplying by clock/occupancy/bandwidth factors <=1 cannot
# turn any observed development scenario into a >=1.02x gain.
assert max(row["ratio"] for row in rows) < 1.02
print("NO-GO development materiality; no physical or prospective validation")
