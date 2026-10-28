#!/usr/bin/env python3
"""Independent exact-state and randomized oracle for V296 deferred-write RF retiming.

Evidence tier: Python semantics only; no RTL, mapped, routed or GPU claim.
Assumes a quiescent reset boundary and one global write per cycle.
"""
import argparse
import itertools
import json
import random


def exhaustive_two_edges():
    cases = 0
    delayed_bad = 0
    naive_bad = 0
    for initial in itertools.product(range(2), repeat=2):
        for reads0 in itertools.product(range(2), repeat=2):
            for write0 in (None, *itertools.product(range(2), repeat=2)):
                for reads1 in itertools.product(range(2), repeat=2):
                    for write1 in (None, *itertools.product(range(2), repeat=2)):
                        cases += 1
                        original = list(initial)
                        delayed = list(initial)
                        naive = list(initial)
                        expected0 = tuple(original[a] for a in reads0)
                        if write0 is not None:
                            original[write0[0]] = write0[1]
                            naive[write0[0]] = write0[1]
                        delayed_bad += tuple(delayed[a] for a in reads0) != expected0
                        naive_bad += tuple(naive[a] for a in reads0) != expected0
                        if write0 is not None:
                            delayed[write0[0]] = write0[1]
                        assert delayed == original
                        expected1 = tuple(original[a] for a in reads1)
                        if write1 is not None:
                            original[write1[0]] = write1[1]
                            naive[write1[0]] = write1[1]
                        delayed_bad += tuple(delayed[a] for a in reads1) != expected1
                        naive_bad += tuple(naive[a] for a in reads1) != expected1
    assert cases == 1600 and delayed_bad == 0 and naive_bad > 0
    return dict(cases=cases, deferred_errors=delayed_bad,
                naive_same_edge_errors=naive_bad)


def trial(depth, seed, cycles):
    rng = random.Random(seed)
    original = [rng.randrange(256) for _ in range(16 * depth)]
    delayed = original.copy()
    naive = original.copy()
    pending = None
    previous_reads = ()
    previous_expected = ()
    errors = naive_errors = collisions = operands = 0
    max_bank_ports = 0
    for t in range(cycles):
        got = tuple(delayed[a] for a in previous_reads)
        errors += got != previous_expected
        naive_errors += tuple(naive[a] for a in previous_reads) != previous_expected
        if pending is not None:
            delayed[pending[0]] = pending[1]
        # After committing W_(t-1), the delayed RF equals the immediate
        # reference state BEFORE W_t. This invariant is checked every edge.
        assert delayed == original, (depth, seed, t, 'RF version invariant')
        counts = [0] * 16
        reads = []
        for _ in range(rng.randrange(9)):
            bank = rng.choice([b for b in range(16) if counts[b] < 2])
            counts[bank] += 1
            reads.append(bank * depth + rng.randrange(depth))
        max_bank_ports = max(max_bank_ports, *counts)
        operands += len(reads)
        current_expected = tuple(original[a] for a in reads)
        write = None
        if t % 11 == 0 and reads:
            write = (reads[0], rng.randrange(256))
        elif t % 3 == 0:
            write = (rng.randrange(len(original)), rng.randrange(256))
        if write is not None:
            collisions += write[0] in reads
            original[write[0]] = write[1]
            naive[write[0]] = write[1]
        pending = write
        previous_reads, previous_expected = reads, current_expected
    errors += tuple(delayed[a] for a in previous_reads) != previous_expected
    naive_errors += tuple(naive[a] for a in previous_reads) != previous_expected
    assert errors == 0 and max_bank_ports <= 2 and naive_errors > 0
    return dict(depth=depth, seed=seed, cycles=cycles, operands=operands,
                collisions=collisions, deferred_errors=errors,
                naive_delayed_errors=naive_errors, max_reads_per_bank=max_bank_ports)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--cycles', type=int, default=20000)
    p.add_argument('--output')
    args = p.parse_args()
    results = dict(evidence_tier='independent Python state invariant, NOT RTL or physical signoff',
                   reset_assumption='no writes during reset; drain pending write before reset',
                   exhaustive=exhaustive_two_edges(),
                   synthetic=[trial(d, s, args.cycles) for d in (4, 8, 16) for s in (101, 911)],
                   physically_validated=False, gpu_advantage=False,
                   mechanism='V296 only; symmetric RF retiming, V287 retired')
    out = json.dumps(results, indent=2, sort_keys=True) + '\n'
    if args.output:
        with open(args.output, 'w') as f:
            f.write(out)
    else:
        print(out)


if __name__ == '__main__':
    main()
