#!/usr/bin/env python3
"""Latency-sensitive falsification of V296's symmetric operand-capture retiming.

Synthetic synchronized batches only; NOT a GPU benchmark, clock measurement,
or proof of correctness for dependent GPU instructions. The event simulator
is independent of the closed-form expression.
"""
import argparse
import json
import math
import random


def exact_cycles(width, slots, latency, barriers):
    if any(type(x) is not int or x < 1 for x in (width, slots, latency)):
        raise ValueError("width, slots, latency must be positive integers")
    if any(type(b) is not bool for b in barriers):
        raise ValueError("barriers must be booleans")
    n = len(barriers) + 1
    return n * ((width + slots - 1) // slots) + sum(barriers) * (latency - 1) + latency - 1


def event_cycles(width, slots, latency, barriers):
    """Issue actual operations, complete after latency cycles, enforce barriers."""
    if any(type(x) is not int or x < 1 for x in (width, slots, latency)):
        raise ValueError("invalid physical parameters")
    if any(type(b) is not bool for b in barriers):
        raise ValueError("invalid barrier")
    n = len(barriers) + 1
    remaining = [width] * n
    done = [0] * n
    completions = {}
    batch = 0
    for tick in range(n * (width + latency + 3)):
        for b in completions.pop(tick, []):
            done[b] += 1
        if done[-1] == width:
            return tick
        if remaining[batch] == 0 and batch + 1 < n:
            if not barriers[batch] or done[batch] == width:
                batch += 1
        if remaining[batch]:
            for _ in range(min(slots, remaining[batch])):
                completions.setdefault(tick + latency, []).append(batch)
                remaining[batch] -= 1
    raise AssertionError("event model failed to terminate")


def evaluate(width, slots, barriers, hypothetical_clock_ratio,
             bandwidth_cap=math.inf, serial_latency=1, candidate_latency=2):
    r = hypothetical_clock_ratio
    if not isinstance(r, (int, float)) or isinstance(r, bool) or not math.isfinite(r) or r <= 0:
        raise ValueError("clock ratio must be positive finite")
    if not isinstance(bandwidth_cap, (int, float)) or isinstance(bandwidth_cap, bool) or math.isnan(bandwidth_cap) or bandwidth_cap <= 0:
        raise ValueError("bandwidth cap must be positive")
    c = exact_cycles(width, slots, serial_latency, barriers)
    v = exact_cycles(width, slots, candidate_latency, barriers)
    if (c != event_cycles(width, slots, serial_latency, barriers) or
            v != event_cycles(width, slots, candidate_latency, barriers)):
        raise AssertionError("independent event simulation disagrees")
    ops = width * (len(barriers) + 1)
    base = ops / c
    cand = r * ops / v
    return {
        "width": width, "issue_slots": slots, "batches": len(barriers) + 1,
        "barrier_fraction": sum(barriers) / max(1, len(barriers)),
        "serial_latency": serial_latency, "candidate_latency": candidate_latency,
        "serial_cycles": c, "candidate_cycles": v,
        "hypothetical_clock_ratio": r,
        "minimum_clock_ratio_for_positive_compute_gain": v / c,
        "compute_gain": cand / base - 1,
        "ideal_bandwidth_capped_gain": min(cand, bandwidth_cap) / min(base, bandwidth_cap) - 1,
        "bandwidth_cap_ops_per_serial_cycle": bandwidth_cap if math.isfinite(bandwidth_cap) else None,
        "evidence": "EXACT_SYNTHETIC_BOUNDARY_AND_INDEPENDENT_EVENT_SIM_NOT_PHYSICAL_GPU"
    }


def barriers(n, kind, seed=72811):
    if kind == "independent":
        return [False] * (n - 1)
    if kind == "barrier":
        return [True] * (n - 1)
    if kind == "alternating":
        return [i % 2 == 0 for i in range(n - 1)]
    if kind == "random":
        rng = random.Random(seed)
        return [rng.random() < .37 for _ in range(n - 1)]
    raise ValueError(kind)


def self_test():
    rng = random.Random(20261026)
    for _ in range(300):
        w, i, l, n = rng.randint(1, 24), rng.randint(1, 8), rng.randint(1, 5), rng.randint(1, 12)
        bs = [bool(rng.randrange(2)) for _ in range(n - 1)]
        assert exact_cycles(w, i, l, bs) == event_cycles(w, i, l, bs)
    for bs in ([], [False] * 10, [True] * 10, barriers(20, "alternating")):
        assert evaluate(8, 4, bs, 1)["compute_gain"] <= 0
        assert evaluate(8, 4, bs, 1.1, bandwidth_cap=.1)["ideal_bandwidth_capped_gain"] == 0
    for args in ((0, 4, 1, []), (4, 0, 1, []), (4, 4, 0, [])):
        try:
            exact_cycles(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted invalid resource")
    for r in (0, -1, float("nan")):
        try:
            evaluate(4, 4, [], r)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted invalid clock")
    print("V296_DEPENDENCY_EVENT_ORACLE_PASS 300 randomized comparisons")


def study():
    # Exploratory synthetic examples. NOT prospectively preregistered holdouts.
    cases = [
        ("independent_hypothetical_win", 32, 4, "independent", 1.05, math.inf),
        ("single_wavefront_loss", 4, 4, "barrier", 1.05, math.inf),
        ("medium_occupancy_loss", 16, 4, "alternating", 1.10, math.inf),
        ("bandwidth_saturated", 32, 4, "independent", 1.05, .5),
        ("mixed_seed72811", 11, 3, "random", 1.08, math.inf),
        ("high_occupancy_seed72811", 64, 4, "random", 1.05, math.inf),
    ]
    return {name: evaluate(w, i, barriers(257, kind), r, cap)
            for name, w, i, kind, r, cap in cases}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--study", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
    if args.study:
        print(json.dumps(study(), indent=2, sort_keys=True))
    if not (args.self_test or args.study):
        p.error("choose --self-test or --study")
