#!/usr/bin/env python3
"""Independent V299 small-state victim checker with deliberate mutant detection."""
import itertools
from v299_tlb_fanout import Entry, TranslationCache


def reference_score(entry, tick):
    age = tick - entry.last
    if age < 16: factor = 1
    elif age < 32: factor = 2
    elif age < 48: factor = 4
    elif age < 64: factor = 8
    else: factor = 16
    return (entry.frequency * entry.fanout_bin) // factor


def check():
    cases = mismatches = mutant_caught = 0
    for f0, f1, w0, w1, a0, a1 in itertools.product(
        range(1, 4), range(1, 4), range(1, 4), range(1, 4),
        (0, 15, 16, 31, 32, 63, 64, 96), (0, 15, 16, 31, 32, 63, 64, 96)
    ):
        # Four 3-valued axes and two 8-valued ages: 5,184 cases.
        tick = 100
        c = TranslationCache('v299', 2)
        e0 = Entry(1, tick - a0, f0, w0)
        e1 = Entry(2, tick - a1, f1, w1)
        c.entries = {1: e0, 2: e1}
        expected = min((e0, e1), key=lambda e: (reference_score(e, tick), e.last, e.page)).page
        actual = c.victim(tick)
        mismatches += actual != expected
        # Deliberate mutation removes age decay; must fail on at least one case.
        mutant = min((e0, e1), key=lambda e: (e.frequency * e.fanout_bin, e.last, e.page)).page
        mutant_caught += mutant != expected
        cases += 1
    assert cases == 5184 and mismatches == 0 and mutant_caught > 0
    print(f'independent checker: PASS ({cases} exhaustive states, {mutant_caught} mutant distinctions)')

if __name__ == '__main__':
    check()
