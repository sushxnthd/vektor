#!/usr/bin/env python3
"""Independent exhaustive partition and labeled-map audit; no evaluator imports."""
import json
import sys
from itertools import product
from math import factorial

def set_partitions(values):
    """Independent recursive block-insertion algorithm, not RGS enumeration."""
    if not values:
        yield []
        return
    first, *rest = values
    for blocks in set_partitions(rest):
        yield [[first]] + [list(b) for b in blocks]
        for i in range(len(blocks)):
            copy = [list(b) for b in blocks]
            copy[i].append(first)
            yield copy

def allowed(reqs, selected):
    count = {}
    for i in selected:
        for bank in reqs[i]:
            count[bank] = count.get(bank, 0) + 1
    return all(n <= 2 for n in count.values())

def options(reqs, pending):
    head = pending[0]
    return [(head,)] + [(head, j) for j in pending[1:] if allowed(reqs, (head, j))]

def direct_event(reqs):
    first_options = options(reqs, (0, 1, 2, 3))
    greedy_first = first_options[1] if len(first_options) > 1 else first_options[0]
    def score(first):
        rem = tuple(i for i in (0, 1, 2, 3) if i not in first)
        return len(first) + max(len(s) for s in options(reqs, rem))
    baseline = score(greedy_first)
    oracle = max(map(score, first_options))
    assert oracle - baseline in (0, 1)
    return oracle - baseline, baseline

def independent_row(pattern, B):
    registers = tuple(sorted(set(v for pair in pattern for v in pair)))
    counts = [0, 0]
    weighted = [0, 0]
    gsum = 0
    for blocks in set_partitions(list(registers)):
        k = len(blocks)
        if k > B:
            continue
        assignment = {v: i for i, block in enumerate(blocks) for v in block}
        mapped = [(assignment[a], assignment[b]) for a, b in pattern]
        e, g = direct_event(mapped)
        weight = factorial(B) // factorial(B-k)
        counts[e] += 1
        weighted[e] += weight
        gsum += g * weight
    return counts, weighted, gsum

def brute_force(pattern, B):
    regs = tuple(sorted(set(v for pair in pattern for v in pair)))
    hits = [0, 0]
    greedy = 0
    for banks in product(range(B), repeat=len(regs)):
        assignment = dict(zip(regs, banks))
        mapped = [(assignment[a], assignment[b]) for a, b in pattern]
        e, g = direct_event(mapped)
        hits[e] += 1
        greedy += g
    return hits, greedy

def audit(data):
    total_partitions = 0
    brute_maps = 0
    for name, raw in data['patterns'].items():
        pattern = [tuple(p) for p in raw]
        m = len(set(x for p in pattern for x in p))
        for B in data['bank_counts']:
            row = data['results'][name][str(B)]
            counts, weighted, gsum = independent_row(pattern, B)
            assert counts == [row['partition_E0'], row['partition_E1']], (name, B, 'partitions')
            assert weighted == [row['labeled_maps_E0'], row['labeled_maps_E1']], (name, B, 'weighted')
            assert sum(weighted) == B ** m == row['labeled_maps_total']
            assert abs(gsum/(B**m)-row['expected_greedy_completions_iid_uniform_mapping']) < 1e-12
            assert abs(weighted[1]/(B**m)-row['probability_E_iid_uniform_mapping']) < 1e-12
            total_partitions += sum(counts)
            if B == 2 or (B == 4 and m <= 8) or (B == 16 and m <= 4):
                labeled, g = brute_force(pattern, B)
                assert labeled == weighted and g == gsum, (name, B, 'brute')
                brute_maps += B ** m
        # An injective register rename preserves the equality pattern and all outcomes.
        renamed = [(a * 17 + 23, b * 17 + 23) for a, b in pattern]
        for B in (2, 4, 16):
            assert independent_row(renamed, B) == independent_row(pattern, B)
    assert data['results']['eight_distinct']['16']['unlabeled_partitions'] == 4140
    assert data['predictions']['eight_distinct_ambiguous_b16']
    assert data['predictions']['all_identical_no_win_all_b']
    assert not data['predictions']['four_doubled_no_win_all_b']
    # Physical bank names are irrelevant; changing names must not alter event.
    for banks in product(range(3), repeat=8):
        mapped = tuple((banks[2*i], banks[2*i+1]) for i in range(4))
        swapped = tuple((2-x, 2-y) for x, y in mapped)
        assert direct_event(mapped) == direct_event(swapped)
    return {'status': 'PASS', 'independent_partition_cases': total_partitions,
            'independent_labeled_maps': brute_maps, 'bank_label_permutations_checked': 3**8,
            'register_rename_cases_checked': len(data['patterns'])*3,
            'four_doubled_prediction_falsified': True}

if __name__ == '__main__':
    with open(sys.argv[1], encoding='utf-8') as f:
        result = audit(json.load(f))
    print(json.dumps(result, sort_keys=True, indent=2))
