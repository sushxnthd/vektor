#!/usr/bin/env python3
"""Exact order-robust physical clock break-even test for V317.

A synthetic two-stage FIFO workload is NOT a routed GPU.  Enumerate all
distinct bank-service permutations while preserving the multiset, compute
trace, and candidate issue-spacing.  Report the entire speedup envelope;
do not cherry-pick the favorable trace order.  This is a falsification
of mean-only predictions, not a claim of hardware improvement.
"""
from fractions import Fraction as F
from itertools import permutations, product

def makespan(compute, bank, issue=F(0)):
    assert len(compute) == len(bank) > 0 and issue >= 0
    first = second = F(0)
    for i, (a, b) in enumerate(zip(compute, bank)):
        assert a > 0 and b > 0
        first = max(first, i * issue) + a
        second = max(second, first) + b
    return second

def longest_path(compute, bank, issue):
    n = len(bank)
    return max(j * issue + sum(compute[j:k+1]) + sum(bank[k:])
               for j in range(n) for k in range(j, n))

def envelope(compute, bank, acceleration, clock, issue):
    assert acceleration > 0 and clock > 0
    outcomes = []
    for ordered in sorted(set(permutations(bank))):
        base = makespan(compute, ordered)
        candidate = makespan(compute, tuple(x/acceleration for x in ordered), issue)
        assert base > 0 and candidate > 0
        threshold = base / candidate
        outcomes.append((threshold / clock, threshold, ordered))
    low = min(outcomes)
    high = max(outcomes)
    status = ('ROBUST_WIN' if low[0] > 1 else
              'ROBUST_NO_WIN' if high[0] <= 1 else 'ORDER_DEPENDENT')
    return status, low, high, len(outcomes)

def main():
    checks = 0
    for n in (1, 2, 3, 4):
        for compute in product((F(1), F(2)), repeat=n):
            for bank in product((F(1), F(3)), repeat=n):
                for issue in (F(0), F(1), F(5, 2)):
                    assert makespan(compute, bank, issue) == longest_path(compute, bank, issue)
                    checks += 1
    assert checks == 1020
    # Independently test envelope against direct speedup comparisons.
    for compute, bank in [
        ((F(1),)*4, (F(1),F(1),F(4),F(4))),
        ((F(2),)*4, (F(1),F(1),F(4),F(4))),
    ]:
        for acceleration in (F(1), F(2)):
            for issue in (F(0), F(3)):
                status, lo, hi, count = envelope(compute, bank, acceleration, F(101,100), issue)
                direct = [makespan(compute, p) /
                          (F(101,100)*makespan(compute, tuple(x/acceleration for x in p), issue))
                          for p in set(permutations(bank))]
                assert lo[0] == min(direct) and hi[0] == max(direct)
                assert count == len(set(permutations(bank)))
                assert (status == 'ROBUST_WIN') == all(x > 1 for x in direct)
                assert (status == 'ROBUST_NO_WIN') == all(x <= 1 for x in direct)
    # Prospective synthetic stress regimes, no fitted thresholds.
    regimes = {
        'compute_bound_clock_penalty': ((F(4),)*4, (F(1),)*4, F(2), F(105,100), F(0)),
        'bank_bound_possible_win': ((F(1),)*4, (F(4),)*4, F(2), F(101,100), F(0)),
        'issue_throttle_reversal': ((F(1),)*4, (F(4),)*4, F(2), F(101,100), F(5)),
        'order_sensitivity': ((F(2),)*4, (F(1),F(1),F(4),F(4)), F(2), F(101,100), F(0)),
    }
    for name, args in regimes.items():
        status, lo, hi, count = envelope(*args)
        print(f'{name}: {status}; permutations={count}; '
              f'speedup=[{float(lo[0]):.6f}, {float(hi[0]):.6f}]; '
              f'break_even_clock=[{float(lo[1]):.6f}, {float(hi[1]):.6f}]')
    print(f'PASS {checks} longest-path checks and 8 independent envelope comparisons')
    print('MODEL ONLY: no physical legality, GPU IPC, or unseen workload validation')

if __name__ == '__main__':
    main()
