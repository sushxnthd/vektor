#!/usr/bin/env python3
"""V313 prospective synthetic screen. NOT a GPU simulator or physical result.

The frozen preregistration is SLACK_ONLY_EARLY_OPERAND_PREREG_20261031.md.
Both policies receive the identical pre-generated offered trace.
"""
import argparse
import json
import random
from collections import deque

SLOTS, BANKS, PORTS, DEPTH = 4, 16, 2, 4
WARMUP, MEASURE = 2000, 20000
REGIMES = {
    "win": dict(seed=313701, hot=.80, affinity=.80, delays=(3, 4, 5, 6)),
    "no_win": dict(seed=313702, hot=0., affinity=0., delays=(0,)),
    "transfer": dict(seed=313703, hot=.65, affinity=.65, delays=(2, 3, 4, 5)),
}


def offered_trace(regime):
    cfg = REGIMES[regime]
    rng = random.Random(cfg["seed"])
    for t in range(WARMUP + MEASURE):
        arrivals = []
        for slot in range(SLOTS):
            if rng.random() >= .90:
                arrivals.append(None)
                continue
            b0 = 0 if rng.random() < cfg["hot"] else rng.randrange(BANKS)
            b1 = (1 + slot) if rng.random() < cfg["affinity"] else rng.randrange(BANKS)
            delay = rng.choice(cfg["delays"])
            arrivals.append((t, (t, t + delay), (b0, b1)))
        yield arrivals


def simulate(trace, early):
    queues = [deque() for _ in range(SLOTS)]
    stats = dict(offered=0, dropped=0, issued=0, rf_reads=0,
                 early_reads=0, ready_reads=0, bank_port_capacity=0)
    latencies = []
    for t, arrivals in enumerate(trace):
        for slot, arrival in enumerate(arrivals):
            if arrival is None:
                continue
            if t >= WARMUP:
                stats["offered"] += 1
            if len(queues[slot]) < DEPTH:
                queues[slot].append([*arrival, [False, False]])
            elif t >= WARMUP:
                stats["dropped"] += 1

        bank_uses = [0] * BANKS
        # First serve fully-ready instructions; early reads use ONLY residual ports.
        for phase in ("ready", "blocked"):
            if phase == "blocked" and not early:
                continue
            for operand in range(2):
                for offset in range(SLOTS):
                    slot = (t + offset) % SLOTS
                    if not queues[slot]:
                        continue
                    item = queues[slot][0]
                    born, ready_at, banks, captured = item
                    fully_ready = max(ready_at) <= t
                    if (phase == "ready") != fully_ready:
                        continue
                    if captured[operand] or ready_at[operand] > t:
                        continue
                    bank = banks[operand]
                    if bank_uses[bank] >= PORTS:
                        continue
                    assert ready_at[operand] <= t
                    bank_uses[bank] += 1
                    captured[operand] = True
                    if t >= WARMUP:
                        stats["rf_reads"] += 1
                        stats["early_reads" if phase == "blocked" else "ready_reads"] += 1
        assert all(0 <= used <= PORTS for used in bank_uses)
        if t >= WARMUP:
            stats["bank_port_capacity"] += BANKS * PORTS
        issued_this_cycle = 0
        for queue in queues:
            if not queue or not all(queue[0][3]):
                continue
            item = queue.popleft()
            assert max(item[1]) <= t, "issued before both operands ready"
            issued_this_cycle += 1
            if t >= WARMUP:
                stats["issued"] += 1
                latencies.append(t - item[0] + 1)
        assert issued_this_cycle <= SLOTS
    stats["throughput"] = stats["issued"] / MEASURE
    stats["mean_latency"] = sum(latencies) / len(latencies) if latencies else 0.
    stats["p99_latency"] = sorted(latencies)[min(len(latencies)-1, int(.99*len(latencies)))] if latencies else 0
    stats["rf_port_utilization"] = stats["rf_reads"] / stats["bank_port_capacity"]
    return stats


def evaluate(regime):
    trace = list(offered_trace(regime))
    baseline = simulate(trace, early=False)
    candidate = simulate(trace, early=True)
    assert baseline["offered"] == candidate["offered"]
    ratio = candidate["issued"] / baseline["issued"]
    if regime == "win":
        assert 1.02 <= ratio <= 1.06, f"frozen win boundary failed: {ratio}"
    if regime == "no_win":
        assert ratio == 1.0, f"frozen no-win failed: {ratio}"
        assert baseline == candidate, "no-win policy should be exactly identical"
    return dict(seed=REGIMES[regime]["seed"], baseline=baseline,
                candidate=candidate, issue_ratio=ratio,
                relative_drop_reduction=(baseline["dropped"]-candidate["dropped"]) /
                max(1, baseline["dropped"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regime", choices=[*REGIMES, "all"], default="all")
    args = parser.parse_args()
    names = REGIMES if args.regime == "all" else [args.regime]
    result = dict(evidence_tier="synthetic four-slot FIFO RF service, not GPU or physical evidence",
                  prospective=True, prereg="research/v313/SLACK_ONLY_EARLY_OPERAND_PREREG_20261031.md",
                  warmup=WARMUP, measured_cycles=MEASURE,
                  regimes={name: evaluate(name) for name in names})
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
