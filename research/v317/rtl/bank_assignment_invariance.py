#!/usr/bin/env python3
"""Exact V317 register-identity bank-assignment uncertainty, not GPU bank evidence.

Exhausts unlabeled bank assignments via restricted-growth strings. Each class
with k occupied banks represents (B)_k labeled assignments for B banks.
"""
import json
from fractions import Fraction
from math import prod

BANKS = (2, 4, 16)
PATTERNS = {
    'eight_distinct': ((0, 1), (2, 3), (4, 5), (6, 7)),
    'all_identical': ((0, 0), (0, 0), (0, 0), (0, 0)),
    'four_doubled': ((0, 0), (1, 1), (2, 2), (3, 3)),
    'shared_sources': ((0, 1), (0, 2), (3, 4), (3, 5)),
    'two_alternating': ((0, 1), (1, 0), (0, 1), (1, 0)),
    'cross_repeated': ((0, 1), (2, 3), (0, 2), (1, 3)),
}

def partitions(n, max_classes):
    """Enumerate every equivalence relation on n labeled tokens up to B classes."""
    if n < 1:
        yield ()
        return
    def rec(prefix, classes):
        if len(prefix) == n:
            yield tuple(prefix)
            return
        for c in range(min(classes + 1, max_classes)):
            prefix.append(c)
            yield from rec(prefix, max(classes, c + 1))
            prefix.pop()
    yield from rec([0], 1)

def compatible(requests, ids):
    counts = {}
    for i in ids:
        for b in requests[i]:
            counts[b] = counts.get(b, 0) + 1
            if counts[b] > 2:
                return False
    return True

def legal_first(requests):
    return [(0,)] + [(0, i) for i in range(1, 4) if compatible(requests, (0, i))]

def second_count(requests, first):
    rem = [i for i in range(4) if i not in first]
    if not rem:
        return 0
    return 1 + int(any(compatible(requests, (rem[0], i)) for i in rem[1:]))

def event(requests):
    choices = legal_first(requests)
    greedy = choices[1] if len(choices) > 1 else (0,)
    g = len(greedy) + second_count(requests, greedy)
    o = max(len(choice) + second_count(requests, choice) for choice in choices)
    assert o - g in (0, 1)
    return o - g, g

def falling(b, k):
    return prod(range(b - k + 1, b + 1)) if k <= b else 0

def run_pattern(pattern, b):
    unique = tuple(dict.fromkeys(v for pair in pattern for v in pair))
    index = {v: i for i, v in enumerate(unique)}
    n = len(unique)
    count = [0, 0]
    labeled = [0, 0]
    g_weight = 0
    for partition in partitions(n, b):
        mapped = tuple((partition[index[a]], partition[index[c]]) for a, c in pattern)
        e, g = event(mapped)
        weight = falling(b, max(partition) + 1)
        count[e] += 1
        labeled[e] += weight
        g_weight += weight * g
    assert sum(labeled) == b ** n, (n, b, labeled)
    prob = Fraction(labeled[1], b ** n)
    expected_g = Fraction(g_weight, b ** n)
    ratio = 1 + prob / expected_g
    return {
        'unique_registers': n, 'bank_count': b,
        'unlabeled_partitions': sum(count), 'partition_E0': count[0], 'partition_E1': count[1],
        'labeled_maps_E0': labeled[0], 'labeled_maps_E1': labeled[1],
        'labeled_maps_total': b ** n,
        'mapping_invariant_E': 0 if not labeled[1] else (1 if not labeled[0] else None),
        'probability_E_iid_uniform_mapping': float(prob),
        'expected_greedy_completions_iid_uniform_mapping': float(expected_g),
        'oracle_to_greedy_ratio_iid_uniform_mapping': float(ratio),
        'exact_probability_fraction': f'{prob.numerator}/{prob.denominator}',
    }

def run():
    results = {name: {str(b): run_pattern(pat, b) for b in BANKS}
               for name, pat in PATTERNS.items()}
    assert results['eight_distinct']['16']['unlabeled_partitions'] == 4140
    predictions = {
        'eight_distinct_ambiguous_b16': results['eight_distinct']['16']['mapping_invariant_E'] is None,
        'all_identical_no_win_all_b': all(results['all_identical'][str(b)]['mapping_invariant_E'] == 0 for b in BANKS),
        'four_doubled_no_win_all_b': all(results['four_doubled'][str(b)]['mapping_invariant_E'] == 0 for b in BANKS),
    }
    return {'schema': 'vektor.v317.bank_assignment_invariance.v1',
            'evidence_tier': 'exact symbolic bank assignment sensitivity, NOT verified SASS mapping or physical RF demand',
            'protocol': 'FROZEN_BANK_ASSIGNMENT_INVARIANCE_20261103.md',
            'bank_counts': BANKS, 'ports_per_bank': 2, 'issue_cap': 2, 'cycles': 2,
            'patterns': {k: [list(p) for p in v] for k, v in PATTERNS.items()},
            'results': results, 'predictions': predictions}

if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
