#!/usr/bin/env python3
"""Fixed-port admission-optimality falsifier for V296 (Python stdlib).

Greedy is the shared V296/serial semantics. Maximum-cardinality subset is an
unimplemented, unfair scheduling-policy oracle, NOT an equal-area design.
Frozen protocol: OPTIMAL_SUBSET_ADMISSION_ORACLE_PREREG_20261025.md
"""
import argparse
from fractions import Fraction
from itertools import product
from math import log, sqrt
from random import Random


def greedy(req, banks):
    used = [0] * banks
    accepted = []
    for i, pair in enumerate(req):
        if pair is None:
            continue
        a, b = pair
        assert 0 <= a < banks and 0 <= b < banks
        if used[a] + (a == b) >= 2 or used[b] + (a == b) >= 2:
            continue
        used[a] += 1
        used[b] += 1
        accepted.append(i)
    assert all(n <= 2 for n in used)
    return tuple(accepted)


def subset_feasible(req, mask, banks):
    used = [0] * banks
    for i, pair in enumerate(req):
        if not (mask & (1 << i)):
            continue
        if pair is None:
            return False
        a, b = pair
        used[a] += 1
        used[b] += 1
        if used[a] > 2 or used[b] > 2:
            return False
    return True


def optimal(req, banks):
    """Independent full bitmask enumeration, not a hardware implementation."""
    n = len(req)
    best_mask, best = 0, 0
    for mask in range(1 << n):
        count = mask.bit_count()
        if count > best and subset_feasible(req, mask, banks):
            best, best_mask = count, mask
    return tuple(i for i in range(n) if best_mask & (1 << i))


def recursive_optimal(req, banks):
    """Second oracle with different control flow and mutable occupancy."""
    occupancy = [0] * banks
    def visit(i):
        if i == len(req):
            return 0
        skip = visit(i + 1)
        pair = req[i]
        if pair is None:
            return skip
        a, b = pair
        occupancy[a] += 1
        occupancy[b] += 1
        take = -1000
        if occupancy[a] <= 2 and occupancy[b] <= 2:
            take = 1 + visit(i + 1)
        occupancy[a] -= 1
        occupancy[b] -= 1
        return max(skip, take)
    return visit(0)


def exact_case(banks=3, slots=4, p=Fraction(4, 5), rho=Fraction(1, 5)):
    choices = [None] + list(product(range(banks), repeat=2))
    weights = [1 - p] + [
        p * ((rho / banks if a == b else 0) + (1 - rho) / (banks * banks))
        for a, b in choices[1:]
    ]
    assert sum(weights) == 1
    mass = g = o = nonzero = Fraction(0)
    max_regret = 0
    for indices in product(range(len(choices)), repeat=slots):
        req = tuple(choices[i] for i in indices)
        prob = Fraction(1)
        for i in indices:
            prob *= weights[i]
        if prob == 0:
            continue
        gn = len(greedy(req, banks))
        on = len(optimal(req, banks))
        assert on >= gn
        mass += prob
        g += prob * gn
        o += prob * on
        if on > gn:
            nonzero += prob
            max_regret = max(max_regret, on - gn)
    assert mass == 1
    return dict(banks=banks, slots=slots, greedy=float(g), oracle=float(o),
                regret=float(o - g), positive_regret_frequency=float(nonzero),
                max_regret=max_regret, exact_regret=str(o - g),
                exact_probability_mass=str(mass))


def draw_request(rng, banks, p, rho):
    if rng.random() >= p:
        return None
    a = rng.randrange(banks)
    b = a if rng.random() < rho else rng.randrange(banks)
    return a, b


def simulate(banks, slots, p, rho, n, seed):
    rng = Random(seed)
    gsum = osum = pos = max_regret = 0
    for _ in range(n):
        req = tuple(draw_request(rng, banks, p, rho) for _ in range(slots))
        gn = len(greedy(req, banks))
        on = len(optimal(req, banks))
        regret = on - gn
        assert regret >= 0
        gsum += gn
        osum += on
        pos += regret > 0
        max_regret = max(max_regret, regret)
    half = slots * sqrt(log(2 / 0.01) / (2 * n))
    mean = (osum - gsum) / n
    return dict(banks=banks, slots=slots, p=p, rho=rho, n=n, seed=seed,
                greedy=gsum / n, oracle=osum / n, regret=mean,
                positive_regret_frequency=pos / n, max_regret=max_regret,
                regret_99pct_hoeffding_interval=[max(0, mean - half),
                                                 min(slots, mean + half)],
                bound_half_width=half)


def self_test():
    req = ((0, 1), (0, 0), (1, 1), (2, 2))
    assert greedy(req, 3) == (0, 3)
    assert len(optimal(req, 3)) == recursive_optimal(req, 3) == 3
    assert greedy(((0, 0), (0, 0)), 1) == (0,)
    assert greedy(((0, 1), (0, 1)), 2) == (0, 1)
    assert greedy((None, None), 2) == ()
    assert len(optimal((None, None), 2)) == 0
    choices = [None] + list(product(range(2), repeat=2))
    for req in product(choices, repeat=3):
        assert len(optimal(req, 2)) == recursive_optimal(req, 2)
        assert len(greedy(req, 2)) <= len(optimal(req, 2))
        permuted = tuple(None if r is None else (1-r[0], 1-r[1]) for r in req)
        swapped = tuple(None if r is None else (r[1], r[0]) for r in req)
        assert len(greedy(req, 2)) == len(greedy(permuted, 2)) == len(greedy(swapped, 2))
        assert len(optimal(req, 2)) == len(optimal(permuted, 2)) == len(optimal(swapped, 2))
    print("PASS: exhaustive independent oracle, permutation, operand swap, and port-cap tests")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--evaluate", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    if args.evaluate:
        import json
        result = {
            "evidence_tier": "exact finite synthetic enumeration + seeded independent synthetic simulation; not physical GPU throughput",
            "protocol": "OPTIMAL_SUBSET_ADMISSION_ORACLE_PREREG_20261025.md",
            "exact": exact_case(),
            "predicted_oracle_win": simulate(4, 4, 0.95, 0.20, 120000, 296011),
            "predicted_near_no_win": simulate(16, 4, 0.20, 0.20, 120000, 296012),
            "equal_clock_v296_vs_serial_gain": 0.0,
        }
        result["preregistered_gates"] = {
            "high_contention_regret_gt_0p02": result["predicted_oracle_win"]["regret"] > 0.02,
            "low_contention_regret_lt_0p01": result["predicted_near_no_win"]["regret"] < 0.01,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    if not args.self_test and not args.evaluate:
        parser.print_help()


if __name__ == "__main__":
    main()
