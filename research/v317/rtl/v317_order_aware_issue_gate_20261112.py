#!/usr/bin/env python3
"""Exact finite-workload order-aware tandem/issue-spacing falsification.

Two FIFO single-server stages, exact rational time. Synthetic only, not GPU IPC.
"""
from fractions import Fraction as Q
from itertools import product

def simulate(compute, bank, issue=Q(0)):
    assert len(compute) == len(bank) and compute and issue >= 0
    a_end = b_end = Q(0)
    for i, (a, b) in enumerate(zip(compute, bank)):
        assert a > 0 and b > 0
        a_end = max(a_end, i * issue) + a
        b_end = max(a_end, b_end) + b
    return b_end

def independent_paths(compute, bank, issue=Q(0)):
    """Enumerate all release j and stage-transfer k longest-path cuts."""
    n = len(compute)
    return max(j * issue + sum(compute[j:k+1]) + sum(bank[k:])
               for k in range(n) for j in range(k+1))

def speedup(compute, bank, r, clock, issue):
    assert r > 0 and clock > 0
    return simulate(compute, bank)/(clock * simulate(
        compute, tuple(b/r for b in bank), issue))

def gate(compute, bank, r, clock, issue):
    s = speedup(compute, bank, r, clock, issue)
    return ('WIN' if s > 1 else 'NO_WIN' if s < 1 else 'TIE', s)

def main():
    checks = 0
    for n in (1, 2, 3, 4):
        for a in product((Q(1), Q(2)), repeat=n):
            for b in product((Q(1), Q(3)), repeat=n):
                for h in (Q(0), Q(1), Q(5,2)):
                    assert simulate(a,b,h) == independent_paths(a,b,h)
                    checks += 1
    # Frozen synthetic hypotheses, not unseen hardware validation.
    regimes = {
        'predicted_no_win_compute_bound': ((Q(4),)*4, (Q(1),)*4, Q(2), Q(105,100), Q(0)),
        'predicted_win_bank_bound': ((Q(1),)*4, (Q(4),)*4, Q(2), Q(101,100), Q(0)),
        'occupancy_reversal': ((Q(1),)*4, (Q(4),)*4, Q(2), Q(101,100), Q(5)),
    }
    expected = {'predicted_no_win_compute_bound':'NO_WIN',
                'predicted_win_bank_bound':'WIN', 'occupancy_reversal':'NO_WIN'}
    for name, (a,b,r,c,h) in regimes.items():
        label, s = gate(a,b,r,c,h)
        assert label == expected[name], (name, label, s)
        print(name, label, f'{float(s):.6f}x', f'exact={s}')
    print('PASS', checks, 'independent longest-path comparisons')
    print('Synthetic analytical evidence only; no physical or GPU validation')

if __name__ == '__main__':
    main()
