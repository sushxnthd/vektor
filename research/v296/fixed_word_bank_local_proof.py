#!/usr/bin/env python3
"""Independent exhaustive bank-local equivalence proof for the 2-word RF proxy.

Does NOT prove synthesizable timing, deep SRAM equivalence or GPU performance.
"""
import itertools
import json
from collections import Counter


def grants(bank_pairs, valid):
    admitted = []
    for i, (a, b) in enumerate(bank_pairs):
        if not ((valid >> i) & 1):
            continue
        used = Counter(x for j in admitted for x in bank_pairs[j])
        if (a == b and used[a] == 0) or (a != b and used[a] < 2 and used[b] < 2):
            admitted.append(i)
    return admitted


def original_port_read(words, req):
    if len(req) > 2:
        raise ValueError('More than two physical read ports required')
    addr0 = req[0] if req else 0
    addr1 = req[1] if len(req) > 1 else 0
    return [words[addr1 if i else addr0] for i in range(len(req))]


def fixed_word_read(words, req):
    return [words[w] for w in req]


def exhaustive():
    local_cases = 0
    for word0 in range(256):
        for word1 in range(256):
            words = (word0, word1)
            for req in ((), (0,), (1,), (0, 0), (0, 1), (1, 0), (1, 1)):
                assert original_port_read(words, req) == fixed_word_read(words, req)
                local_cases += 1
    # Every 4-slot bank assignment from a 3-bank subspace, all valid masks.
    admission_cases = 0
    admitted_wave_total = 0
    max_bank_load = 0
    for flat in itertools.product(range(3), repeat=8):
        pairs = tuple((flat[2*i], flat[2*i+1]) for i in range(4))
        for valid in range(16):
            chosen = grants(pairs, valid)
            operands = [x for i in chosen for x in pairs[i]]
            loads = Counter(operands)
            max_bank_load = max(max_bank_load, max(loads.values(), default=0))
            assert max(loads.values(), default=0) <= 2
            admitted_wave_total += len(chosen)
            admission_cases += 1
    # Deliberate out-of-domain counterexample: third read is NOT legal.
    req = (0, 0, 1)
    words = (0, 1)
    old_unsafe = [words[0], words[0], words[0]]
    new_unsafe = fixed_word_read(words, req)
    assert old_unsafe != new_unsafe
    return {
        'decision': 'BANK_LOCAL_TWO_PORT_EQUIVALENCE_EXHAUSTIVE_ONLY',
        'local_word_data_cases': local_cases,
        'three_bank_four_slot_validity_cases': admission_cases,
        'admitted_waves_across_cases': admitted_wave_total,
        'maximum_bank_reads': max_bank_load,
        'out_of_domain_three_read_counterexample': {
            'requests': req, 'words': words, 'old': old_unsafe, 'fixed': new_unsafe},
        'scope': '2 words per bank, <=2 admitted operands per bank; no timing, power, or deep-SRAM transfer',
        'physically_feasible': False,
        'gpu_speedup_claim': False,
    }


if __name__ == '__main__':
    print(json.dumps(exhaustive(), indent=2, sort_keys=True))
