#!/usr/bin/env python3
"""V314 prospective synthetic RF arbitration falsification.

No RTL, physical, real GPU trace, or novelty claim. Frozen protocol:
research/v314/COMPLETION_HINT_PREREG_20261031.md
"""
import argparse
import json
import random
from collections import deque

SLOTS, BANKS, PORTS, DEPTH = 4, 16, 2, 4
WARMUP, MEASURE = 2000, 20000
REGIMES = {
    "hot": dict(seed=314801, arrival=.98, hot=.97, affinity=.85, delay=0),
    "no_win": dict(seed=314802, arrival=.70, hot=0., affinity=0., delay=0),
    "transfer": dict(seed=314803, arrival=.93, hot=.75, affinity=.50, delay=0),
    "dependency": dict(seed=314804, arrival=.97, hot=.94, affinity=.70, delay=6),
}


def offered_trace(regime):
    c = REGIMES[regime]
    rng = random.Random(c["seed"])
    for t in range(WARMUP + MEASURE):
        arrivals = []
        for slot in range(SLOTS):
            if rng.random() >= c["arrival"]:
                arrivals.append(None)
                continue
            b0 = 0 if rng.random() < c["hot"] else rng.randrange(BANKS)
            b1 = 1 + slot if rng.random() < c["affinity"] else (
                0 if rng.random() < c["hot"] else rng.randrange(BANKS))
            # Different physical registers even when both hash to same bank.
            d = rng.choice((0, 0, 0, c["delay"])) if c["delay"] else 0
            arrivals.append((t, (t, t + d), (b0, b1)))
        yield arrivals


def simulate(stream, policy, capture_events=False):
    assert policy in ("age", "hint")
    queues = [deque() for _ in range(SLOTS)]
    stats = dict(issued=0, offered=0, dropped=0, rf_reads=0,
                 early_reads=0, stalled_heads=0)
    latencies, events = [], []
    for t, arrivals in enumerate(stream):
        for lane, item in enumerate(arrivals):
            if item is None:
                continue
            if t >= WARMUP:
                stats["offered"] += 1
            if len(queues[lane]) == DEPTH:
                if t >= WARMUP:
                    stats["dropped"] += 1
            else:
                queues[lane].append(dict(born=item[0], ready=item[1],
                                         banks=item[2], done=[False, False]))
        free = [PORTS] * BANKS
        cycle_reads = []
        for phase in (0, 1):  # fully-ready heads before early partial collection
            for _ in range(SLOTS * 2):
                choices = []
                for lane, q in enumerate(queues):
                    if not q:
                        continue
                    h = q[0]
                    fully_ready = max(h["ready"]) <= t
                    if (phase == 0) != fully_ready:
                        continue
                    for op in (0, 1):
                        bank = h["banks"][op]
                        if h["done"][op] or h["ready"][op] > t or free[bank] == 0:
                            continue
                        age = t - h["born"]
                        # Age shield is applied before completion preference.
                        priority = (age >= 16, bool(h["done"][1-op])) if policy == "hint" else (False, False)
                        choices.append((priority, age, -((lane - t) % SLOTS),
                                        -op, lane, op, bank))
                if not choices:
                    break
                _, _, _, _, lane, op, bank = max(choices)
                h = queues[lane][0]
                assert not h["done"][op] and h["ready"][op] <= t
                h["done"][op] = True
                free[bank] -= 1
                cycle_reads.append((lane, op, bank, phase, h["born"]))
                if t >= WARMUP:
                    stats["rf_reads"] += 1
                    if phase:
                        stats["early_reads"] += 1
        assert all(0 <= f <= PORTS for f in free)
        assert len(cycle_reads) <= SLOTS * 2
        issued_now = 0
        for q in queues:
            if q and all(q[0]["done"]):
                h = q.popleft()
                assert max(h["ready"]) <= t
                issued_now += 1
                if t >= WARMUP:
                    stats["issued"] += 1
                    latencies.append(t - h["born"] + 1)
            elif q and t >= WARMUP:
                stats["stalled_heads"] += 1
        assert issued_now <= SLOTS
        if capture_events and t >= WARMUP:
            events.append((t, cycle_reads, issued_now))
    stats["throughput"] = stats["issued"] / MEASURE
    stats["mean_latency"] = sum(latencies) / len(latencies) if latencies else 0
    stats["p99_latency"] = sorted(latencies)[min(len(latencies)-1, int(.99*len(latencies)))] if latencies else 0
    stats["rf_port_utilization"] = stats["rf_reads"] / (MEASURE * BANKS * PORTS)
    if capture_events:
        return stats, events
    return stats


def evaluate(name):
    stream = list(offered_trace(name))
    baseline = simulate(stream, "age")
    candidate = simulate(stream, "hint")
    assert baseline["offered"] == candidate["offered"]
    ratio = candidate["issued"] / baseline["issued"]
    if name == "hot":
        prediction_pass = 1.0005 <= ratio <= 1.004
    elif name == "no_win":
        prediction_pass = (ratio == 1.0 and baseline["dropped"] == 0
                           and candidate["dropped"] == 0
                           and candidate["p99_latency"] <= baseline["p99_latency"])
    elif name == "transfer":
        prediction_pass = 1.0 <= ratio <= 1.006
    else:
        prediction_pass = None  # sensitivity regime had no directional prediction
    p99_ok = candidate["p99_latency"] <= baseline["p99_latency"]
    return dict(baseline=baseline, candidate=candidate, completion_ratio=ratio,
                prediction_pass=prediction_pass,
                materiality_pass=ratio >= 1.02,
                p99_nonregression=p99_ok,
                retire=(name == "hot" and (ratio < 1.02 or not p99_ok or not prediction_pass)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regime", choices=[*REGIMES, "all"], default="all")
    args = parser.parse_args()
    names = REGIMES if args.regime == "all" else [args.regime]
    result = {n: evaluate(n) for n in names}
    print(json.dumps(dict(evidence_tier="synthetic buffered RF service only",
                          prereg="research/v314/COMPLETION_HINT_PREREG_20261031.md",
                          regimes=result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
