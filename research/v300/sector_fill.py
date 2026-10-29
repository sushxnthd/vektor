"""V300 sector-fill scheduling: frozen synthetic model and independent exhaustive oracle.

Run: python -m research.v300.sector_fill --holdout
No performance/energy claims beyond the simultaneous-arrival four-sector model.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from fractions import Fraction

SECTORS = tuple(range(4))
SEEDS = (300101, 300103, 300107, 300109, 300113)
REGIMES = ("H1", "H2", "H3", "H4", "H5")


def bitcount(x: int) -> int:
    return x.bit_count()


def cost(masks: tuple[int, ...], order: tuple[int, ...]) -> int:
    assert sorted(order) == list(SECTORS)
    completed = 0
    total = 0
    for cycle, sector in enumerate(order, 1):
        completed |= 1 << sector
        total += cycle * sum(mask != 0 and (mask & completed) == mask
                             and (mask & (1 << sector)) != 0
                             for mask in masks)
    return total


def greedy(masks: tuple[int, ...], mode: str,
           prefix: tuple[int, ...] = ()) -> tuple[int, ...]:
    order = list(prefix)
    done = sum(1 << s for s in prefix)
    while len(order) < 4:
        remaining = [s for s in SECTORS if s not in order]
        def score(sector: int):
            bit = 1 << sector
            pending = [m & ~done for m in masks if m and m & ~done]
            fanout = sum(bool(m & bit) for m in pending)
            unlock = sum(m == bit for m in pending)
            if mode == "fanout":
                return (fanout,)
            if mode == "shortest":
                return (sum((Fraction(1, bitcount(m)) for m in pending if m & bit),
                            Fraction(0)),)
            if mode == "unlock":
                return (unlock, fanout)
            raise ValueError(mode)
        chosen = max(remaining, key=lambda s: (score(s), -s))
        order.append(chosen)
        done |= 1 << chosen
    return tuple(order)


def v300(masks: tuple[int, ...]) -> tuple[int, ...]:
    # Enumerate exactly 12 two-sector prefixes, then finish by unlock greedy.
    candidates = [greedy(masks, "unlock", pair)
                  for pair in itertools.permutations(SECTORS, 2)]
    return min(candidates, key=lambda order: (cost(masks, order), order))


def oracle(masks: tuple[int, ...]) -> tuple[int, ...]:
    return min(itertools.permutations(SECTORS),
               key=lambda order: (cost(masks, order), order))


def sample(regime: str, rng: random.Random) -> tuple[int, ...]:
    if regime == "H1":
        pair = rng.sample(SECTORS, 2)
        singleton = rng.choice([s for s in SECTORS if s not in pair])
        masks = [sum(1 << s for s in pair)] * 3 + [1 << singleton] * 3
        masks += [rng.randrange(1, 16) for _ in range(2)]
    elif regime == "H2":
        masks = [1 << rng.randrange(4) for _ in range(8)]
    elif regime == "H3":
        masks = [rng.randrange(1, 16) for _ in range(8)]
    elif regime == "H4":
        common = sum(1 << s for s in rng.sample(SECTORS, 2))
        masks = [common if rng.random() < .75 else 1 << rng.randrange(4)
                 for _ in range(8)]
    elif regime == "H5":
        masks = [rng.randrange(1, 16) for _ in range(2)] + [0] * 6
    else:
        raise ValueError(regime)
    rng.shuffle(masks)
    return tuple(masks)


def exhaustive_check() -> dict:
    # Independent permutation oracle, with no reliance on v300's greedy suffix.
    checked = 0
    mismatches = []
    for n in (1, 2, 3):
        for masks in itertools.product(range(16), repeat=n):
            got = cost(masks, v300(masks))
            expected = cost(masks, oracle(masks))
            if got != expected:
                mismatches.append((masks, got, expected))
            checked += 1
    assert not mismatches, mismatches[:3]
    # Fault injection: a fixed ascending order must fail on some demand pattern.
    witness = (8, 8, 8, 1)
    assert cost(witness, tuple(SECTORS)) > cost(witness, oracle(witness))
    return {"states": checked, "mismatches": len(mismatches),
            "fault_injection_detected": True}


def evaluate() -> dict:
    result = {"protocol": "V300-2026-10-29", "episodes_per_seed": 1000,
              "seeds": list(SEEDS), "regimes": {}, "exhaustive": exhaustive_check()}
    for regime in REGIMES:
        totals = {k: 0 for k in ("fixed", "fanout", "shortest", "unlock", "v300", "oracle")}
        active = 0
        for seed in SEEDS:
            rng = random.Random(seed + 10000 * REGIMES.index(regime))
            for _ in range(1000):
                masks = sample(regime, rng)
                active += sum(bool(m) for m in masks)
                orders = {"fixed": tuple(SECTORS),
                          "fanout": greedy(masks, "fanout"),
                          "shortest": greedy(masks, "shortest"),
                          "unlock": greedy(masks, "unlock"),
                          "v300": v300(masks), "oracle": oracle(masks)}
                for key, order in orders.items():
                    totals[key] += cost(masks, order)
        means = {k: totals[k] / active for k in totals}
        strongest = min(("fanout", "shortest", "unlock"), key=lambda k: totals[k])
        gain = 1 - totals["v300"] / totals[strongest]
        result["regimes"][regime] = {
            "active_warps": active, "total_wakeup_cycles": totals,
            "mean_wakeup_cycles": means,
            "strongest_greedy": strongest,
            "v300_gain_over_strongest_greedy": gain}
    r = result["regimes"]
    result["synthetic_gate_pass"] = (
        r["H1"]["v300_gain_over_strongest_greedy"] >= .05
        and r["H2"]["v300_gain_over_strongest_greedy"] >= -.02
        and all(r[h]["v300_gain_over_strongest_greedy"] >= -.05
                for h in ("H3", "H4", "H5")))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--holdout", action="store_true")
    args = parser.parse_args()
    if args.holdout:
        print(json.dumps(evaluate(), sort_keys=True, indent=2))
    else:
        print(json.dumps(exhaustive_check(), sort_keys=True))
