#!/usr/bin/env python3
"""V296-vs-strong-serial logical-net switching proxy, NOT power or timing.

Two independent combinational admissions implement the RTL's four-request,
16-bank, two-read-port greedy semantics. The proxy records value transitions
at explicit RTL-level observed logical signals, not physical cell pins,
glitches, capacitance, placement or routed energy.

This experiment does NOT claim power reduction or GPU throughput.
"""
import argparse
import json
import random

SEEDS = (1701, 1709)
CYCLES = 40000
# Frozen synthetic development and unseen regimes; these are not GPU traces.
TRAIN = {
    "uniform_sparse": (0.35, 0.0, 0.0),
    "uniform_dense": (0.90, 0.0, 0.0),
    "hotbank_dense": (0.90, 0.65, 0.0),
    "hotbank_sparse": (0.35, 0.65, 0.0),
}
UNSEEN = {
    "medium_mixed": (0.60, 0.35, 0.0),
    "extreme_hot": (0.95, 0.95, 0.0),
    "sticky_temporal": (0.75, 0.50, 0.75),
    "cold_temporal": (0.75, 0.50, 0.0),
}

def hamming(a, b):
    if isinstance(a, (bool, int)):
        return (int(a) ^ int(b)).bit_count()
    return sum(hamming(x, y) for x, y in zip(a, b))

def pairwise(valid, banks):
    grant = []
    eq = []
    hits = []
    for i, (a, b) in enumerate(banks):
        ca = cb = 0
        for j in range(i):
            pa, pb = banks[j]
            eq.extend((int(pa == a and grant[j]), int(pb == a and grant[j]),
                       int(pa == b and grant[j]), int(pb == b and grant[j])))
            if grant[j]:
                ca += (pa == a) + (pb == a)
                cb += (pa == b) + (pb == b)
        hits.extend((ca, cb))
        grant.append(int(bool(valid[i]) and
                         (ca == 0 if a == b else ca < 2 and cb < 2)))
    return tuple(grant), tuple(eq) + tuple(hits) + tuple(grant)

def serial(valid, banks):
    once = twice = 0
    grant = []
    trace = []
    for i, (a, b) in enumerate(banks):
        aa = 1 << a
        bb = 1 << b
        if not valid[i]:
            fit = False
        elif a == b:
            fit = (once & aa) == 0
        else:
            fit = (twice & aa) == 0 and (twice & bb) == 0
        g = int(bool(valid[i]) and fit)
        if g:
            if a == b:
                once |= aa
                twice |= aa
            else:
                twice |= once & (aa | bb)
                once |= aa | bb
        grant.append(g)
        trace.extend((aa, bb, once, twice, int(fit), g))
    return tuple(grant), tuple(trace)

def stimulus(seed, cycles, validity, hotness, persistence):
    rng = random.Random(seed)
    prev = None
    for _ in range(cycles):
        if prev is not None and rng.random() < persistence:
            yield prev
            continue
        v = tuple(int(rng.random() < validity) for _ in range(4))
        banks = []
        for _ in range(4):
            a = 0 if rng.random() < hotness else rng.randrange(16)
            b = 0 if rng.random() < hotness else rng.randrange(16)
            banks.append((a, b))
        prev = (v, tuple(banks))
        yield prev

def run_one(name, params, seed, cycles):
    prior_p = prior_s = None
    switches_p = switches_s = 0
    grants = overlap = live = repeated = 0
    previous = None
    for v, bank in stimulus(seed, cycles, *params):
        p, pnets = pairwise(v, bank)
        s, snets = serial(v, bank)
        assert p == s, (name, seed, v, bank, p, s)
        if prior_p is not None:
            switches_p += hamming(prior_p, pnets)
            switches_s += hamming(prior_s, snets)
        prior_p, prior_s = pnets, snets
        grants += sum(p)
        live += sum(v)
        overlap += sum(a == b for i, (a, b) in enumerate(bank) if v[i])
        repeated += int(previous == (v, bank))
        previous = (v, bank)
    return dict(name=name, seed=seed, cycles=cycles, grants=grants,
                grants_per_cycle=grants / cycles,
                live_requests_per_cycle=live / cycles,
                same_bank_operand_rate=overlap / live if live else None,
                repeated_request_rate=repeated / (cycles - 1),
                pairwise_observed_transitions=switches_p,
                serial_observed_transitions=switches_s,
                pairwise_to_serial_transition_ratio=switches_p / switches_s if switches_s else None,
                proxy_scope="observed RTL-level logical values; incomparable internal gate counts and capacitances")

def selftest():
    from itertools import product
    cases = 0
    for valid in product((0, 1), repeat=4):
        for b in product((0, 1, 2), repeat=8):
            banks = tuple(zip(b[::2], b[1::2]))
            assert pairwise(valid, banks)[0] == serial(valid, banks)[0]
            assert sum(pairwise(valid, banks)[0]) <= sum(valid)
            cases += 1
    assert serial((1, 1, 0, 0), ((0, 0), (0, 1), (2, 3), (4, 5)))[0] == (1, 0, 0, 0)
    assert pairwise((1, 1, 0, 0), ((0, 1), (0, 2), (3, 4), (5, 6)))[0] == (1, 1, 0, 0)
    return cases

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()
    tests = selftest() if args.self_test else None
    rows = []
    for group, regimes in (("development", TRAIN), ("unseen", UNSEEN)):
        for name, params in regimes.items():
            for seed in SEEDS:
                rows.append(dict(group=group,
                                 parameters={"validity": params[0], "hotness": params[1],
                                             "persistence": params[2]},
                                 **run_one(name, params, seed, CYCLES)))
    result = {"scope": "synthetic RTL-observed-value switching proxy; NOT cell-level power, no glitch or cap data",
              "source_variants": ["v296_pairwise_arbiter", "v295_issue_core PREDECODE=0"],
              "source_files": ["research/v296/v296_issue_core.sv", "research/v295/v295_issue_core.sv"],
              "frozen_regimes": {"development": TRAIN, "unseen": UNSEEN},
              "selftest_cases": tests, "rows": rows,
              "prediction": "none: activity comparison is an exploratory proxy, not a predictive power law",
              "matched_physical_energy_proven": False, "gpu_throughput_gain_proven": False}
    body = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        with open(args.out, "w") as f:
            f.write(body)
    else:
        print(body)

if __name__ == "__main__":
    main()
